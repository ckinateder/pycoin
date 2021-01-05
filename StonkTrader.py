#!/usr/bin/env python
from datetime import datetime, timezone
import CryptoPredict
import time
import csv
import threading
import psutil
import os
import sklearn
import sys
import json
import alpaca
import math
from guppy import hpy
import logging

__author__ = 'Calvin Kinateder'
__email__ = 'calvinkinateder@gmail.com'


class ThreadedTrader:
    def __init__(self, pair, headers, retrain_every, fees=False, conservative=True):
        self.headers = headers
        self.pair = [pair[0].upper(), pair[1]]  # [{ticker}, 'usd']
        self.filename = self.getFilename(pair)
        self.retrain_every = retrain_every*60
        self.trader = alpaca.AlpacaTrader()
        self.predictor = CryptoPredict.CryptoPredictor(lookback=1,
                                                       epochs=13,
                                                       units=256,
                                                       batch_size=1,
                                                       pair=pair,
                                                       ext='alpaca',
                                                       cutpoint=1800,  # 300?
                                                       important_headers=headers,
                                                       verbose=2)
        self.current_df = self.predictor.createFrame()
        self.smallest_size = 20
        self.total_net = 0
        self.time_delay = 2
        self.start_time = datetime.now()
        self.conservative = conservative
        self.predicting = True  # for pausing
        self.last_time_trained = 0
        self.fiat = self.trader.getCash()
        self.lowest_sell_threshold = self.fiat
        self.initial_investment = self.fiat
        self.stonk = self.trader.getPosition(pair[0])

        print('Starting with ${} and {} shares of {}.'.format(
            self.fiat, self.stonk, self.pair[0]))

        # reset file
        headers = ['unix', 'action', 'price ({})'.format(self.pair[0]), 'balance ({})'.format(
            self.pair[1]), 'balance ({})'.format(self.pair[0]), 'valuation ({})'.format(self.pair[1]), 'total net (%)', 'uptime', 'dataset size']

        with open('logs/current_log.csv', 'w+') as filename:
            writer = csv.writer(filename)
            writer.writerow(headers)

    def utc_to_local(self, utc_dt):
        '''
        Converts UTC time to local timezone.
        '''
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

    def logToCSV(self, row):
        '''
        Logs diagnostics to file.
        '''
        with open('logs/current_log.csv', 'a') as filename:
            writer = csv.writer(filename)
            writer.writerow(row)

    def getFilename(self, pair):
        '''
        Gets the appropiate filename given a pair.
        '''
        return 'data/'+'-'.join(pair)+'_alpaca.csv'

    def getFees(self):
        '''
        Gets the fees for each exchange (no longer needed).
        '''
        # open file with json of fees and return dict of fees for the prices keys
        with open('data/fees.json', 'r') as jfees:
            self.fees = json.loads(jfees.read())
        return self.fees

    def checkMemory(self, heapy=False):
        '''
        Checks size of memory and prints it in MB.
        '''
        process = psutil.Process(os.getpid())
        # in bytes
        logging.info(
            'Using {:.2f} MB of memory\n'.format(process.memory_info().rss/(1024*1024)))
        if heapy:
            h = hpy()
            print(h.heap())

    def checkRetrainLoop(self):
        '''
        Checks to see whether or not the model needs to be retrained.
        '''
        # RETRAIN
        while True:
            if self.predicting:

                if ((time.time() - self.last_time_trained) >= self.retrain_every or self.last_time_trained == 0) and len(self.current_df) >= self.smallest_size:
                    self.last_time_trained = time.time()
                    logging.info('Retraining model ...\n')
                    self.predictor.retrainModel(self.current_df)

                if self.last_time_trained != 0:
                    logging.info('Last model trained at {}'.format(self.utc_to_local(
                        datetime.utcfromtimestamp(self.last_time_trained))))
                else:
                    logging.info('Model not trained yet ...')

            time.sleep(10)

    def saveLoop(self):
        '''
        Saves the latest price for the currency to the csv file, applies the model, and makes a decision.
        Will later be modified to trade as well.
        '''
        while True:
            try:
                self.trader.saveTickerPair(self.pair)
            except:
                logging.warning('api call failed...trying again in 5')
                time.sleep(5)
                self.trader.saveTickerPair(self.pair)

            self.current_df = self.predictor.createFrame()  # re update frame

            try:
                if self.predicting:
                    if len(self.current_df) >= self.smallest_size:
                        current_model = self.predictor.loadModel()
                        # only do this once it can verify last 2400 CONTINUOUS DATA
                        decision = self.predictor.decideAction(
                            self.current_df, current_model)
                        # update current standings agaim
                        self.fiat = self.trader.getCash()
                        self.stonk = self.trader.getPosition(self.pair[0])
                        # buy or sell here
                        current_price = self.current_df.iloc[-1][self.headers['price']]
                        stonk_value = self.fiat/current_price  # in crypto
                        dollar_value = self.stonk*current_price  # in usd

                        action_taken = 'hold'

                        if decision == 'buy':
                            if not self.trader.anyOpen(self.pair[0]):
                                self.trader.submitOrder(
                                    self.pair[0], 'buy', math.floor(self.fiat/current_price))
                                # self.lowest_sell_threshold = math.floor(
                                # self.fiat/current_price)*current_price  # THIS MIGHJT NOT BE GOOD
                                # change this\/?
                                action_taken = 'buy'
                                logging.info('Bought')
                            else:
                                logging.warning('Open orders - trade canceled')
                            logging.info(
                                '[Balance: {:.2f} {}, {:.8f} {}, (bought)]'.format(
                                    self.fiat, self.pair[1].upper(), self.stonk, self.pair[0].upper()))
                        elif decision == 'sell' and self.stonk >= stonk_value:
                            if self.conservative:
                                # so no loss from selling
                                if dollar_value >= self.lowest_sell_threshold:  # change this line maybe
                                    if not self.trader.anyOpen(self.pair[0]):
                                        self.trader.submitOrder(
                                            self.pair[0], 'sell', self.stonk)
                                        action_taken = 'sell'
                                        logging.info('Sold')
                                    else:
                                        logging.warning(
                                            'Open orders - trade canceled')
                            else:  # just do it
                                if not self.trader.anyOpen(self.pair[0]):
                                    self.trader.submitOrder(
                                        self.pair[0], 'sell', self.stonk)
                                    action_taken = 'sell'
                                    logging.info('Sold')
                                    # change this/\?
                                else:
                                    logging.warning(
                                        'Open orders - trade canceled')
                            logging.info(
                                '[Balance: {:.2f} {}, {:.8f} {}, (sold)]'.format(
                                    self.fiat, self.pair[1].upper(), self.stonk, self.pair[0].upper()))
                        else:
                            logging.info(
                                '[Balance: {:.2f} {}, {:.8f} {} (valued at {:.2f} USD), (holding)]'.format(
                                    self.fiat, self.pair[1].upper(), self.stonk, self.pair[0].upper(), dollar_value))

                    else:
                        logging.warning(
                            'Not predicting, dataset not big enough ({} < {})'.format(len(self.current_df), self.smallest_size))

                    #  end
                    # update current standings again
                    time.sleep(self.time_delay)

                    self.fiat = self.trader.getCash()
                    self.stonk = self.trader.getPosition(self.pair[0])
                    if decision != action_taken:
                        logging.warning(
                            'decision != action_taken - reasons unknown atm')

                    # end transaction
                    self.total_net = (((self.fiat/self.initial_investment) +
                                       ((self.stonk*current_price)/self.initial_investment))*100)-100
                    print('+ Total net: {:.3f}%\n   (since {})\n'.format(
                        self.total_net, self.start_time.replace(microsecond=0)))
                    logging.info('Current Standings:\n  + Total net: {:.5f}%\n  + Balance:\n  + {:.2f} {}\n  + {:.8f} {} (valued at {:.2f} USD)\n  + Open trades? {}\n   ({})'.format(self.total_net,
                                                                                                                                                                                      self.fiat, self.pair[1].upper(), self.stonk, self.pair[0].upper(), dollar_value, self.trader.anyOpen(self.pair[0]), action_taken))
                    #  save to current log
                    row = [datetime.now().replace(microsecond=0), action_taken, current_price, round(self.fiat, 2), round(self.stonk, 8), round(
                        self.stonk*current_price+self.fiat, 2), round(self.total_net, 3), str(datetime.now()-self.start_time)[:-7], len(self.current_df)]
                    self.logToCSV(row)
                    self.checkMemory()
                else:
                    logging.info(
                        'Not predicting, toggled off ... just saving.')
            except sklearn.exceptions.NotFittedError as e:
                time.sleep(self.time_delay)
                logging.warning(
                    'Model not fit yet - waiting til next cycle ({})'.format(e))
            except UnboundLocalError as e:
                time.sleep(self.time_delay)
                logging.warning(
                    'Model not fit yet - waiting til next cycle ({})'.format(e))
            except FileNotFoundError as e:
                time.sleep(self.time_delay)
                logging.warning(
                    'Model not found - {} ...'.format(e))

    def run(self):
        '''
        Main function.
        '''
        try:
            logging.info('Initial training ...')
            logging.info('Creating savingThread ...')
            self.savingThread = threading.Thread(
                target=self.saveLoop, name='saver')
            self.savingThread.setDaemon(True)
            logging.info('Starting savingThread ...')
            self.savingThread.start()
            logging.info('Creating retrainingThread ...')
            self.retrainingThread = threading.Thread(
                target=self.checkRetrainLoop, name='retrainer')
            self.retrainingThread.setDaemon(True)
            logging.info('Waiting 10 seconds ...\n')
            time.sleep(10)
            logging.info('Starting retrainingThread ...\n')
            self.retrainingThread.start()
            logging.info('\nGood to go!\n')

        except (KeyboardInterrupt, SystemExit):
            logging.fatal('Cancelled')
