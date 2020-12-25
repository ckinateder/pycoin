# Kraken Rest API
#
# Usage: ./krakenapi.py method [parameters]
# Example: ./krakenapi.py Time
# Example: ./krakenapi.py OHLC pair=xbtusd interval=1440
# Example: ./krakenapi.py Balance
# Example: ./krakenapi.py OpenPositions
# Example: ./krakenapi.py AddOrder pair=xxbtzusd type=buy ordertype=market volume=0.003 leverage=5
# use MARKET ORDERS

import sys
import platform
import time
import base64
import hashlib
import hmac
import pprint
import urllib.request as urllib2
import json
import os
import pandas
import csv

class KrakenTrader:
    def __init__(self):
        self.api_public = {"Time", "Assets", "AssetPairs", "Ticker", "OHLC", "Depth", "Trades", "Spread"}
        self.api_private = {"Balance", "BalanceEx", "TradeBalance", "OpenOrders", "ClosedOrders", "QueryOrders", "TradesHistory", "QueryTrades", "OpenPositions", "Ledgers", "QueryLedgers", "TradeVolume", "AddExport", "ExportStatus", "RetrieveExport", "RemoveExport", "GetWebSocketsToken"}
        self.api_trading = {"AddOrder", "CancelOrder", "CancelAll"}
        self.api_funding = {"DepositMethods", "DepositAddresses", "DepositStatus", "WithdrawInfo", "Withdraw", "WithdrawStatus", "WithdrawCancel", "WalletTransfer"}

        self.api_domain = "https://api.kraken.com"

    def main(self, args):
        api_data = ""
        args = ['']+args # for the stupid sys.argv conversion -- fix later
        if len(args) < 2:
            api_method = "Time"
        elif len(args) == 2:
            api_method = args[1]
        else:
            api_method = args[1]
            for count in range(2, len(args)):
                if count == 2:
                    api_data = args[count]
                else:
                    api_data = api_data + "&" + args[count]
        #print(args)
        if api_method in self.api_private or api_method in self.api_trading or api_method in self.api_funding:
            api_path = "/0/private/"
            api_nonce = str(int(time.time()*1000))
            try:
                api_key = open("keys/kraken_public").read().strip()
                api_secret = base64.b64decode(open("keys/kraken_private").read().strip())
            except:
                print("API public key and API private (secret) key must be in text files in keys/ called kraken_public and kraken_private")
                sys.exit(1)
            api_postdata = api_data + "&nonce=" + api_nonce
            api_postdata = api_postdata.encode('utf-8')
            api_sha256 = hashlib.sha256(api_nonce.encode('utf-8') + api_postdata).digest()
            api_hmacsha512 = hmac.new(api_secret, api_path.encode('utf-8') + api_method.encode('utf-8') + api_sha256, hashlib.sha512)
            api_request = urllib2.Request(self.api_domain + api_path + api_method, api_postdata)
            api_request.add_header("API-Key", api_key)
            api_request.add_header("API-Sign", base64.b64encode(api_hmacsha512.digest()))
            api_request.add_header("User-Agent", "Kraken REST API")
        elif api_method in self.api_public:
            api_path = "/0/public/"
            api_request = urllib2.Request(self.api_domain + api_path + api_method + '?' + api_data)
            api_request.add_header("User-Agent", "Kraken REST API")
        else:
            print("Usage: %s method [parameters]" % args[0])
            print("Example: %s OHLC pair=xbtusd interval=1440" % args[0])
            sys.exit(1)

        try:
            api_reply = urllib2.urlopen(api_request).read()
        except Exception as error:
            print("API call failed (%s)" % error)
            sys.exit(1)

        try:
            api_reply = api_reply.decode()
        except Exception as error:
            if api_method == 'RetrieveExport':
                sys.stdout.buffer.write(api_reply)
                sys.exit(0)
            print("API response invalid (%s)" % error)
            sys.exit(1)

        if '"error":[]' in api_reply:
            #print(api_reply)
            return api_reply
            #sys.exit(0)
        else:
            print(api_reply)
            return api_reply
            #sys.exit(1)
    
    def cleanup(self, filename, how_far_back):
        num_lines = sum(1 for line in open(filename))
        if num_lines>how_far_back:
            whole_file = pandas.read_csv(filename)
            
            end = num_lines-how_far_back
            
            parsed = whole_file.drop(list(range(0,end)))
            parsed.to_csv(filename, index=False)
            # drop early rows and then rewrite NOT APPEND

    def saveBTC(self, filename): # just save latest:
        args = ['Ticker', 'pair=xbtusd']
        reply = json.loads(self.main(args))['result']['XXBTZUSD']

        if not os.path.isfile(filename): # only add header if file doesnt exist
            header = list()
            header.append('unix')
            for i in reply.items():
                header.append(i[0])
            #total.append(header)
            pandas.DataFrame([header]).to_csv(filename, mode='a', header=False,index=False)
        
        dropped = list()
        dropped.append(time.time())
        for i in reply.values():
            dropped.append(i[0])
        print('Recieved response from with',args)
        #open and delete everything back from the day before
        pandas.DataFrame([dropped]).to_csv(filename, mode='a', header=False,index=False)
        print('Saved response at time',dropped[0], 'to file')
        # cleanup
        self.cleanup(filename, 4096)
        return pandas.DataFrame([dropped]) # dont usually need to return it
        

    def saveBTCLOOP(self, filename):
        while True:
            try:
                self.saveBTC(filename)
                time.sleep(10)
            except:
                print('Call failed... trying again in 2')
                time.sleep(2)
