import requests, json, datetime, CryptoPredict, time, kraken, pandas, asyncio, concurrent.futures, logging, threading
#using crypto compare

filename = 'data/data121820.csv'

##make predictor global

def saveWithCatch(trader, filename):
    try:
        trader.saveBTC(filename)
    except:
        print('api call failed...trying again in 5')
        time.sleep(5)
        trader.saveBTC(filename)

#write threading here using threads and futures
def checkRetrain(predictor):
    retrain_every = 15*60
    ###RETRAIN
    last_time_trained = 0
    while True:
        df = predictor.createFrame()
        if (time.time() - last_time_trained) > retrain_every or last_time_trained == 0:
            last_time_trained = time.time()
            latest_model = predictor.retrainModel(df)
            
        print('Last model trained at', datetime.datetime.utcfromtimestamp(last_time_trained).strftime('%Y-%m-%d %H:%M:%S'), 'UTC')
        time.sleep(10)

def saveLoop(trader, predictor):
    while True:
        try:
            trader.saveBTC(filename)
        except:
            print('api call failed...trying again in 5')
            time.sleep(5)
            trader.saveBTC(filename)
        df = predictor.createFrame()
        current_model = predictor.loadModel('current-model')

        decision = predictor.decideAction(df, current_model) # only do this once it can verify last 2400 CONTINUOUS DATA
        '''     
        df = predictor.createFrame() # uses file passed already in constructor

        if len(df.index)>1800: # if set is big enough with absolute MIN
            predictor.cutpoint = len(df.index)
        else:
            print('Dataframe not big enough - missing',(2400-len(df.index)),'points')
         '''     
        time.sleep(10)


def runThreaded(filename):

    headers = {
        'timestamp': 'unix',
        'price': 'a' # the column used for price
        }
    
    predictor = CryptoPredict.CryptoPredictor(lookback=1,epochs=13,units=256,batch_size=1,datafile=filename, cutpoint=2400, important_headers=headers)
    df = predictor.createFrame()
    if len(df.index) < 1800:
        print('Dataset too small (',len(df.index),') < 1800 – models will not be optimal',)
        #return False
    trader = kraken.KrakenTrader()
    '''
    - turn into handleNext
    - write function in CryptoTrader to deal with getting the new data, retraining every fifteen minutes, even acting on the trade flag?
    '''
    # initialize
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    savingThread = threading.Thread(target=saveLoop, args=(trader, predictor))
    savingThread.start()
    retrainingThread = threading.Thread(target=checkRetrain, args=[predictor])
    retrainingThread.start()
    # x.join()


### run code

def testRealTime(filename, retrain_every=15): # in mins
    headers = {
        'timestamp': 'unix',
        'price': 'a' # the column used for price
        }
    
    predictor = CryptoPredict.CryptoPredictor(lookback=1,epochs=13,units=256,batch_size=1,datafile=filename, cutpoint=2400, important_headers=headers)
    trader = kraken.KrakenTrader()
    '''
    - turn into handleNext
    - write function in CryptoTrader to deal with getting the new data, retraining every fifteen minutes, even acting on the trade flag?
    '''
    retrain_every = retrain_every*60

    last_time_trained = 0
    while True:
        saveWithCatch(trader, filename)

        df = predictor.createFrame() # uses file passed already in constructor

        if len(df.index)>1800: # if set is big enough with absolute MIN
            predictor.cutpoint = len(df.index)
            ###RETRAIN
            if (time.time() - last_time_trained) > retrain_every:
                last_time_trained = time.time()
                latest_model = predictor.retrainModel(df)
                
            print('Last model trained at', datetime.datetime.utcfromtimestamp(last_time_trained).strftime('%Y-%m-%d %H:%M:%S'), 'UTC')
            decision = predictor.decideAction(df, latest_model) # only do this once it can verify last 2400 CONTINUOUS DATA
        else:
            print('Dataframe not big enough - missing',(2400-len(df.index)),'points')
        
        time.sleep(10)

#testRealTime('data/data121820.csv')
runThreaded(filename)