import requests, json, datetime, CryptoPredict
#using crypto compare
headers = {
        'timestamp': 'unix',
        'price': 'a' # the column used for price
        }
cp = CryptoPredict.CryptoPredictor(lookback=1,epochs=13,units=256,batch_size=1,datafile='data/data121820.csv', cutpoint=2400, important_headers=headers)
cp.testRealTime()