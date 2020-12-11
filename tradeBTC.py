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
data_api.getLowHiPair(prices)
