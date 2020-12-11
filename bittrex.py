import requests, json, datetime
#using crypto compare

#load api_key

class Bittrex:
    def __init__(self, key):
        self.key = key