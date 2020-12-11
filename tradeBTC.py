import requests, json, datetime
import getCC

cc_key = getCC.loadKey('keys/cryptocompare')
exchanges = ['binanceusa','bittrex', 'kraken', 'bitfinex', 'bitstamp', 'gemini']
prices = getCC.getPrices('BTC',exchanges, cc_key)
print('At',datetime.datetime.now())
getCC.printj(prices)
getCC.getLowHiPair(prices)
