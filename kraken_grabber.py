import kraken
import os
import sys
import time

kt = kraken.KrakenTrader()

while True:
    try:
        kt.saveTickerPair(sys.argv[1:])
        time.sleep(10)
    except Exception as e:
        print('* Call failed... trying again in 2\n* Message: {}'.format(e))
        time.sleep(2)
