import alpaca
import time
import os
import sys

ap = alpaca.AlpacaTrader()

print(sys.argv[1:])

while True:
    try:
        for i in range(1, len(sys.argv)):
            pair = [sys.argv[i], "usd"]  # for compatibility
            ap.saveTickerPair(pair)
        time.sleep(5)
    except Exception as e:
        print("* Call failed... trying again in 2\n* Message: {}".format(e))
        time.sleep(2)
