import datetime
import CryptoPredict
import time
import kraken
import threading
import psutil
import os
import sklearn
import sys
# using crypto compare
from guppy import hpy

filename = 'data/data121820.csv'

# make predictor global


class ThreadedTrader:
    def __init__(self, filename, retrain_every, initial_investment):
        headers = {
            'timestamp': 'unix',
            'price': 'a'  # the column used for price
        }
        self.usd = initial_investment
        self.btc = 0
        self.filename = filename
        self.retrain_every = retrain_every*60
        self.trader = kraken.KrakenTrader()
        self.predictor = CryptoPredict.CryptoPredictor(lookback=1,
                                                       epochs=13,
                                                       units=256,
                                                       batch_size=1,
                                                       datafile=filename,
                                                       cutpoint=1800,
                                                       important_headers=headers,
                                                       verbose=0)
        self.current_df = self.predictor.createFrame()

    def checkMemory(self, heapy=False):
        process = psutil.Process(os.getpid())
        # in bytes
        print(
            '* Using {:.2f} MB of memory\n'.format(process.memory_info().rss/(1024*1024)))
        if heapy:
            h = hpy()
            print(h.heap())

    # write threading here using threads and futures
    def checkRetrainLoop(self):
        # RETRAIN
        last_time_trained = 0
        while True:
            if (time.time() - last_time_trained) > self.retrain_every or last_time_trained == 0:
                last_time_trained = time.time()
                print('* Retraining model ...')
                self.predictor.retrainModel(self.current_df)

            print('Last model trained at', datetime.datetime.utcfromtimestamp(
                last_time_trained).strftime('%Y-%m-%d %H:%M:%S'), 'UTC')
            time.sleep(10)

    def saveLoop(self):
        while True:
            try:
                self.trader.saveBTC(filename)
            except:
                print('api call failed...trying again in 5')
                time.sleep(5)
                self.trader.saveBTC(filename)

            self.current_df = self.predictor.createFrame()  # re update frame
            current_model = self.predictor.loadModel('current-model')
            try:
                # only do this once it can verify last 2400 CONTINUOUS DATA
                decision = self.predictor.decideAction(
                    self.current_df, current_model)

                # buy or sell here
                current_price = self.current_df.iloc[-1].a

                crypto_value = self.usd/current_price  # in btc
                dollar_value = self.btc*current_price  # in usd

                if decision == 'buy' and self.usd >= dollar_value:
                    self.btc = self.btc + crypto_value
                    self.usd = self.usd - self.btc*current_price
                    print(
                        '+ Balance:\n  + {:.2f} USD\n  + {:.8f} BTC\n   (bought)\n'.format(self.usd, self.btc))
                elif decision == 'sell' and self.btc >= crypto_value:
                    self.usd = self.usd + dollar_value
                    self.btc = self.btc - self.usd/current_price
                    print(
                        '+ Balance:\n  + {:.2f} USD\n  + {:.8f} BTC\n   (sold)\n'.format(self.usd, self.btc))
                else:
                    print(
                        '+ Balance:\n  + {:.2f} USD\n  + {:.8f} BTC\n   (holding)\n'.format(self.usd, self.btc))
                # end transaction
            except sklearn.exceptions.NotFittedError:
                print('* Model not fit yet - waiting til next cycle')

            self.checkMemory()

            time.sleep(10)

    def run(self):
        try:
            print('* Initial training ...')
            # self.predictor.retrainModel(self.current_df) ## initialize with retrained model

            print('* Creating savingThread ...')
            savingThread = threading.Thread(target=self.saveLoop)
            print('* Starting savingThread ...')
            savingThread.start()
            print('* Creating retrainingThread ...')
            retrainingThread = threading.Thread(target=self.checkRetrainLoop)
            print('* Starting retrainingThread ...\n')
            retrainingThread.start()
            print('\nGood to go!\n')

        except (KeyboardInterrupt, SystemExit):
            print('* Cancelled')


threader = ThreadedTrader(filename, retrain_every=10, initial_investment=500)
threader.run()
