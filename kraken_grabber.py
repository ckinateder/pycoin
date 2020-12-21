import kraken, os, sys

filename = sys.argv[1] # data121820.csv

kt = kraken.KrakenTrader()
kt.saveBTC(filename)