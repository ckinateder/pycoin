#!/bin/bash
python3 kraken_grabber.py eth usd &
python3 kraken_grabber.py ltc usd &
python3 kraken_grabber.py xbt usd &
python3 kraken_grabber.py xrp usd &
python3 kraken_grabber.py rep usd && fg