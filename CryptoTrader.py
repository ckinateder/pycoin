import requests, json, datetime, CryptoPredict
#using crypto compare

cp = CryptoPredict.CryptoPredictor(setp='data/last1000mins.csv')
cp.main()