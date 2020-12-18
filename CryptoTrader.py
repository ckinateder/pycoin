import requests, json, datetime, CryptoPredict
#using crypto compare
headers = {
        'timestamp': 'unix',
        'price': 'a' # the column used for price
        }
cp = CryptoPredict.CryptoPredictor(lookback=15,epochs=15,units=70,batch_size=1,datafile='data/data121820.csv', important_headers=headers)
cp.main()