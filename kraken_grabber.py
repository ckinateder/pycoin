import kraken
import os
import sys
import time

filename = 'kraken.csv'  # kraken.csv

kt = kraken.KrakenTrader()
kt.saveBTCLOOP(filename)
