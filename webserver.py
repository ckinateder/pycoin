from flask import Flask, request, render_template
import tablib
import os
import platform
import time
import pandas as pd

app = Flask(__name__)


def getInfo():
    l = list(platform.uname())
    return 'System Info: '+' - '.join(l)


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


def main():
    app.run(host='0.0.0.0')
