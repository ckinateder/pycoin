#!/usr/bin/env python
from flask import Flask, request, render_template
from datetime import datetime
from CryptoTrader import ThreadedTrader
import tablib
import threading
import time
import os
import platform
import time
import pandas as pd
import sys

__author__ = 'Calvin Kinateder'
__email__ = 'calvinkinateder@gmail.com'

BUILD = '0.9.4'

app = Flask(__name__)

# headers for csv data

headers = {
    'timestamp': 'unix',
    'price': 'a'  # the column used for price
}

pair = ['ltc', 'usd']
invest = 3000

# create threader
threader = ThreadedTrader(
    pair=pair, headers=headers, retrain_every=10, initial_investment=invest, fees=False)


def getFooter():
    '''
    Get system platform info for footer.
    '''
    l = list(platform.uname())
    return 'System Info: '+' - '.join(l)


def getInfo():
    '''
    Get status for info div. (html safe)
    '''
    return 'Pair: [{}]<br>\
        Investing ${:.2f}<br>\
            Predicting: {}<br>\
            Conservative: {}<br>\
            Fees: {}%<br>\
            Fees?: {}<br>\
            Last time trained: <br>\
            {}'.format(' - '.join(pair).upper(), invest, threader.predicting, threader.conservative, threader.fee*100, threader.fees_applied, datetime.fromtimestamp(threader.last_time_trained).strftime("%m-%d-%Y %H:%M:%S"))

# routes


@app.route('/restart_btn')
def restart_btn():
    '''
    Force retrain the model.
    '''
    print('\n* FORCE RETRAIN\n')
    threader.last_time_trained = time.time()
    threader.predictor.retrainModel(threader.current_df)
    return ('Done (/restart_btn)')


@app.route('/toggle_predicting_btn')
def toggle_predicting_btn():
    '''
    Toggle predicting on and off.
    '''
    if threader.predicting:
        threader.predicting = False
    elif threader.predicting == False:
        threader.predicting = True
    return ('Done (/toggle_predicting_btn)')


@app.route('/toggle_conservative_btn')
def toggle_conservative_btn():
    '''
    Toggle conservattive on and off.
    '''
    if threader.conservative:
        threader.conservative = False
    elif threader.conservative == False:
        threader.lowest_sell_threshold = threader.fiat  # important
        threader.conservative = True
    '''
    threader.toggleFees()
    '''
    return ('Done (/toggle_conservative_btn)')


@app.route('/quit_btn')
def quit_btn():
    '''
    Emergency stop button.
    '''
    os._exit(0)
    return ('Done (/quit_btn)')


@app.route('/')
def table():
    '''
    Run on load and reload table.
    '''
    # get log
    dataset = pd.read_csv('logs/current_log.csv')
    if len(dataset.index) >= 1:
        vals = dataset.iloc[-1].to_frame().T.to_html(table_id='latest',
                                                     index=False)
        # print(vals)
        top_row = vals
    else:
        top_row = dataset.to_html(table_id='latest', index=False)
    # get pure csv
    head = pd.read_csv(threader.getFilename(threader.pair))
    if len(head.values) >= 20:
        head_html = head.iloc[-20:].iloc[::-1].to_html(table_id='csv')
    else:
        head_html = head.iloc[-(len(head_html)) -
                              1:].iloc[::-1].to_html(table_id='csv')

    log = dataset.to_html(table_id='log', index=False)
    return render_template('index.html', footer=getFooter(), build=BUILD, latest=top_row, log=log, info=getInfo(), head=head_html, title='pycoin {} - {}%'.format(BUILD, round(threader.total_net, 3)))


def runServer():
    app.run(host='0.0.0.0', threaded=True)


if __name__ == '__main__':
    # run server in background
    serverThread = threading.Thread(target=runServer, name='server')
    # serverThread.setDaemon(True)
    serverThread.start()
    print('Sent webserver to background \n')
    threader.run()
