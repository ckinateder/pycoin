import kraken
import os
import sys
import time

kt = kraken.KrakenTrader()

while True:
    try:
        for i in range(1, len(sys.argv), 2):
            pair = sys.argv[i:i+2]
            kt.saveTickerPair(pair)
        time.sleep(10)
    except Exception as e:
        print('* Call failed... trying again in 2\n* Message: {}'.format(e))
        time.sleep(2)
