from datetime import datetime, timezone
import CryptoPredict
import time
import kraken
import threading
import psutil
import os
import sklearn
import sys
import json
from guppy import hpy


class ThreadedTrader:
    def __init__(self, pair, headers, retrain_every, initial_investment):
        self.headers = headers
        self.usd = initial_investment
        self.initial_investment = initial_investment
        self.crypto = 0
        self.pair = pair
        self.filename = self.getFilename(pair)
        self.retrain_every = retrain_every*60
        self.k_trader = kraken.KrakenTrader()
        self.predictor = CryptoPredict.CryptoPredictor(lookback=1,
                                                       epochs=13,
                                                       units=256,
                                                       batch_size=1,
                                                       pair=pair,
                                                       cutpoint=2400,
                                                       important_headers=headers,
                                                       verbose=0)
        self.current_df = self.predictor.createFrame()

    def getFilename(self, pair):
        return 'data/'+'-'.join(pair)+'_kraken.csv'

    def getFees(self):
        # open file with json of fees and return dict of fees for the prices keys
        with open('data/fees.json', 'r') as jfees:
            self.fees = json.loads(jfees.read())
        return self.fees

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
                print('* Retraining model ...\n')
                self.predictor.retrainModel(self.current_df)

            print('Last model trained at', self.k_trader.utc_to_local(
                datetime.utcfromtimestamp(last_time_trained)))
            print('')
            time.sleep(10)

    def saveLoop(self):
        while True:
            try:
                self.k_trader.saveTickerPair(self.pair)
            except:
                print('api call failed...trying again in 5')
                time.sleep(5)
                self.k_trader.saveTickerPair(self.pair)

            try:
                self.current_df = self.predictor.createFrame()  # re update frame
                current_model = self.predictor.loadModel()
            except FileNotFoundError as e:
                print(e)
                print(
                    '* Model not found - {} ...'.format(e.args[1]))
            try:
                # only do this once it can verify last 2400 CONTINUOUS DATA
                decision = self.predictor.decideAction(
                    self.current_df, current_model)

                # buy or sell here
                current_price = self.current_df.iloc[-1][headers['price']]
                crypto_value = self.usd/current_price  # in crypto
                dollar_value = self.crypto*current_price  # in usd

                if decision == 'buy' and self.usd >= dollar_value:
                    self.crypto = self.crypto + crypto_value
                    self.usd = self.usd - self.crypto*current_price
                    print(
                        '+ Balance:\n  + {:.2f} {}\n  + {:.8f} {}\n   (bought)'.format(
                            self.usd, self.pair[1].upper(), self.crypto, self.pair[0].upper()))
                elif decision == 'sell' and self.crypto >= crypto_value:
                    self.usd = self.usd + dollar_value
                    self.crypto = self.crypto - self.usd/current_price
                    print(
                        '+ Balance:\n  + {:.2f} {}\n  + {:.8f} {}\n   (sold)'.format(
                            self.usd, self.pair[1].upper(), self.crypto, self.pair[0].upper()))
                else:
                    print(
                        '+ Balance:\n  + {:.2f} {}\n  + {:.8f} {} (valued at {:.2f} USD)\n   (holding)'.format(
                            self.usd, self.pair[1].upper(), self.crypto, self.pair[0].upper(), dollar_value))
                total_net = (((self.usd/self.initial_investment) +
                              ((self.crypto*current_price)/self.initial_investment))*100)-100
                print('+ Total net: {:.3f}%\n'.format(total_net))
                # end transaction
            except sklearn.exceptions.NotFittedError:
                print('* Model not fit yet - waiting til next cycle')

            except UnboundLocalError:
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


if __name__ == '__main__':
    '''
    Sample call -
    $ python3 CryptoTrader.py xbt usd 500
    '''
    headers = {
        'timestamp': 'unix',
        'price': 'a'  # the column used for price
    }

    if len(sys.argv) == 4:
        pair = sys.argv[1:3]
        invest = float(sys.argv[3])
    else:
        # default
        pair = ['xbt', 'usd']
        invest = 500

    threader = ThreadedTrader(
        pair=pair, headers=headers, retrain_every=10, initial_investment=invest)
    threader.run()
