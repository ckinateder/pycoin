import requests, json, datetime
import CryptoWrapper


def loadKey(filename):
    with open(filename, 'r') as key:
        return key.read()

cc_key = loadKey('keys/cryptocompare')
exchanges = ['binanceusa','bittrex', 'kraken', 'bitfinex', 'bitstamp', 'gemini']
data_api = CryptoWrapper.CryptoWrapper(cc_key, exchanges)

prices = data_api.getPrices('BTC',exchanges)
print('At',datetime.datetime.now())
data_api.printj(prices)
pair = data_api.getLowHiPair(prices, True)

def testROI():
    print('\nTesting ROI\n-----------------------------')
    for i in range(0,100,10):
        print('ROI w/ ${:d} invested => ${:.2f}'.format(i,data_api.calculateReturn(i, pair[1], pair[0])))
#note bitstamp min is $25

testROI()