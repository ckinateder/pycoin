from flask import Flask, request, render_template
import tablib
import os
import pandas as pd

app = Flask(__name__)


@app.route('/')
def table():
    dataset = pd.read_csv('logs/current_log.csv').to_html()
    return render_template('index.html', table=dataset)


def main():
    app.run(host='0.0.0.0')
