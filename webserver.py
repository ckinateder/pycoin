from flask import Flask
import tablib
import os
import pandas as pd

app = Flask(__name__)


@ app.route('/')
def index():
    dataset = pd.read_csv('logs/current_log.csv')
    return dataset.to_html()


def main():
    app.run(host='0.0.0.0')
