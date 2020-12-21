import requests, json, datetime, CryptoPredict, time, kraken, pandas, asyncio
#using crypto compare

### run code
def testRealTime(retrain_every=15): # in mins
    filename = 'data/data121820.csv'
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
    retrain_every = 15*60

    last_time_trained = 0
    while True:
        trader.saveBTC(filename)
        df = predictor.createFrame() # uses file passed already in constructor
        if (time.time() - last_time_trained) > retrain_every:
            last_time_trained = time.time()
            latest_model = predictor.retrainModel(df)
        else:
            #print('Retraining in {:.2f}s'.format())
            pass
        decision = predictor.decideAction(df, latest_model)
        time.sleep(10)

testRealTime()