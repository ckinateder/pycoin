import requests, json, datetime, CryptoPredict, time, kraken, pandas, asyncio, concurrent.futures, logging, threading, psutil, os
#using crypto compare

filename = 'data/data121820.csv'

##make predictor global

class ThreadedTrader:
    def __init__(self, filename, retrain_every):
        headers = {
            'timestamp': 'unix',
            'price': 'a' # the column used for price
            }
        self.filename = filename
        self.predictor = CryptoPredict.CryptoPredictor(lookback=1,
                                                        epochs=13,
                                                        units=256,
                                                        batch_size=1,
                                                        datafile=filename, 
                                                        cutpoint=2400, 
                                                        important_headers=headers)
        self.trader = kraken.KrakenTrader()
        self.retrain_every = retrain_every*60
        self.current_df = self.predictor.createFrame()

    #write threading here using threads and futures
    def checkRetrainLoop(self):
        ###RETRAIN
        last_time_trained = 0
        while True:
            if (time.time() - last_time_trained) > self.retrain_every or last_time_trained == 0:
                last_time_trained = time.time()
                self.predictor.retrainModel(self.current_df)
                
            print('Last model trained at', datetime.datetime.utcfromtimestamp(last_time_trained).strftime('%Y-%m-%d %H:%M:%S'), 'UTC')
            time.sleep(10)

    def saveLoop(self):
        while True:
            try:
                self.trader.saveBTC(filename)
            except:
                print('api call failed...trying again in 5')
                time.sleep(5)
                self.trader.saveBTC(filename)
                
            self.current_df = self.predictor.createFrame() # re update frame
            current_model = self.predictor.loadModel('current-model')
            decision = self.predictor.decideAction(self.current_df, current_model) # only do this once it can verify last 2400 CONTINUOUS DATA
            
            process = psutil.Process(os.getpid())
            print('* Using {:.2f} MB of memory\n'.format(process.memory_info().rss/(1024*1024)))  # in bytes 

            time.sleep(10)

    def run(self):
        savingThread = threading.Thread(target=self.saveLoop)
        time.sleep(10) # make sure saving is ahead
        retrainingThread = threading.Thread(target=self.checkRetrainLoop)
        savingThread.start()
        retrainingThread.start()
        # x.join()

threader = ThreadedTrader(filename, 15)
threader.run()