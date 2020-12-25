import kraken
import os
import sys
import time

filename = sys.argv[1]  # data121820.csv

kt = kraken.KrakenTrader()
kt.saveBTCLOOP(filename)
