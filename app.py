#!/usr/bin/env python
from flask import Flask, request, render_template
from datetime import datetime, time
from StonkTrader import ThreadedTrader
import tablib
import logging
import threading
import time as t
import os
import platform
import pandas as pd
import sys

print('Imported modules...')

detail = 'logs/detail/' + \
    datetime.now().strftime("%m-%d-%Y_%H-%M-%S")+'.log'
logging.basicConfig(format='%(asctime)s: %(message)s',
                    filename=detail, level=logging.DEBUG)

__author__ = 'Calvin Kinateder'
__email__ = 'calvinkinateder@gmail.com'

BUILD = '0.9.5'

app = Flask(__name__)

# headers for csv data

headers = {
    'timestamp': 'timestamp',
    'price': 'askprice'  # the column used for price
}

pair = ['tsla', 'usd']

# create threader
threader = ThreadedTrader(
    pair=pair, headers=headers, retrain_every=1, fees=False)


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
            Last time trained: <br>\
            {}'.format(' - '.join(pair).upper(), threader.fiat, threader.predicting, threader.conservative, datetime.fromtimestamp(threader.last_time_trained).strftime("%m-%d-%Y %H:%M:%S"))

# routes


@app.route('/restart_btn')
def restart_btn():
    '''
    Force retrain the model.
    '''
    print('\nFORCE RETRAIN\n')
    threader.last_time_trained = t.time()
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
    Toggle conservative on and off.
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
    show = 2
    if len(head.values) >= show:
        head_html = head.iloc[-show:].iloc[::-1].to_html(table_id='csv')
    else:
        head_html = head.iloc[-(len(head_html)) -
                              1:].iloc[::-1].to_html(table_id='csv')

    log = dataset.to_html(table_id='log', index=False)
    return render_template('index.html', footer=getFooter(), build=BUILD, latest=top_row, log=log, info=getInfo(), head=head_html)


def runServer():
    app.run(host='0.0.0.0', threaded=True)


def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else:  # crosses midnight
        return check_time >= begin_time or check_time <= end_time


if __name__ == '__main__':
    # run server in background
    serverThread = threading.Thread(target=runServer, name='server')
    # serverThread.setDaemon(True)
    serverThread.start()
    logging.info('Sent webserver to background')
    threader.run()
