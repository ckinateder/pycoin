import kraken, os, sys, time

filename = sys.argv[1] # data121820.csv

kt = kraken.KrakenTrader()
kt.saveBTCLOOP(filename)
