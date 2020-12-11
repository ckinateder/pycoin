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
pair = data_api.getLowHiPair(prices)

def testROI():
    print('\nTesting ROI\n-----------------------------')
    for i in range(0,100,10):
        print('Net ROI w/ ${:d} invested => ${:.4f}'.format((i+10),data_api.calculateReturn((i+10),pair)))
    print('...Net ROI w/ ${:d} invested => ${:.4f}'.format(500,data_api.calculateReturn(500,pair)))
    print('...Net ROI w/ ${:d} invested => ${:.4f}'.format(1000,data_api.calculateReturn(1000,pair)))
    print('...Net ROI w/ ${:d} invested => ${:.4f}'.format(3000,data_api.calculateReturn(3000,pair)))
    print('...Net ROI w/ ${:d} invested => ${:.4f}'.format(9000,data_api.calculateReturn(9000,pair)))

#note bitstamp min is $25

testROI()