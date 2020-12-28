#!/bin/bash
python3 CryptoTrader.py eth usd &
python3 CryptoTrader.py ltc usd &
python3 CryptoTrader.py xbt usd &
python3 CryptoTrader.py xrp usd &
python3 CryptoTrader.py rep usd && fg