import kraken
import os
import sys
import time

filename = sys.argv[1]  # kraken.csv

kt = kraken.KrakenTrader()
kt.saveBTCLOOP(filename)
