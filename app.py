#!/usr/bin/env python
from flask import Flask, request, render_template
from CryptoTrader import ThreadedTrader
import tablib
import threading
import os
import platform
import time
import pandas as pd
import sys

__author__ = 'Calvin Kinateder'
__email__ = 'calvinkinateder@gmail.com'

app = Flask(__name__)


def getInfo():
    l = list(platform.uname())
    return 'System Info: '+' - '.join(l)


@app.route('/quit_btn')
def quit_btn():
    print('Does nothing rn')
    return ('Done (/quit_btn)')


@app.route('/')
def table():
    # time.sleep(10)
    dataset = pd.read_csv('logs/current_log.csv')
    if len(dataset.index) >= 1:
        vals = dataset.iloc[-1].to_frame().T.to_html(table_id='latest',
                                                     index=False)
        # print(vals)
        top_row = vals
    else:
        top_row = 'No data yet'
    log = dataset.to_html(table_id='log', index=False)
    return render_template('index.html', info=getInfo(), build='0.8.5', latest=top_row, log=log)


def runServer():
    app.run(host='0.0.0.0', threaded=True)


headers = {
    'timestamp': 'unix',
    'price': 'a'  # the column used for price
}

pair = ['eth', 'usd']
invest = 200
threader = ThreadedTrader(
    pair=pair, headers=headers, retrain_every=10, initial_investment=invest)

if __name__ == '__main__':
    '''
    Sample call -
    $ python3 app.py xbt usd 500
    '''
    if len(sys.argv) == 4:
        pair = sys.argv[1:3]
        invest = float(sys.argv[3])
    else:
        # default
        print('Not enough arguments given - must be in format\n  $ python3 CryptoTrader.py (crypto) (usd) (amount to invest)')
        print('Using default values: {} and ${}'.format(pair, invest))

    # run server in background
    threading.Thread(target=runServer, name='server').start()
    print('Sent webserver to background \n')
    threader.run()
