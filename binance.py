import requests, json, datetime
#using crypto compare

#load api_key

class Binance:
    def __init__(self, key):
        self.key = key