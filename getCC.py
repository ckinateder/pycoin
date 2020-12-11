import requests, json, datetime
#using crypto compare

#load api_key
# make into object

def loadKey(filename):
    with open(filename, 'r') as key:
        return key.read()

def getExchanges(filename, key):
    try:
        exc = requests.get('https://min-api.cryptocompare.com/data/exchanges/general?'+
                            key).json()['Data']
        with open(filename, 'w') as outfile:
            json.dump(exc, outfile)
        return exc
    except:
        return -1    

def getPrices(currency, exchanges, key): #returns dictionary
    summation = {}
    for exc in exchanges:
        call = 'https://min-api.cryptocompare.com/data/price?fsym='+currency+'&tsyms=USD&e='+exc+'&api_key='+key
        print('Asking for',currency,'on '+exc+'...')
        try:
            recieved = requests.get(call).json()['USD']
        except:
            recieved = 'NA'
        summation[exc] = float(recieved) # return dict
    return summation

def getLowHiPair(prices): #returns min and max
    minimum = min(prices, key=prices.get)
    maximum = max(prices, key=prices.get)
    print('Lowest =',minimum,'at $'+str(prices[minimum]))
    print('Highest =',maximum,'at $'+str(prices[maximum]))
    print('Difference => ${:.2f}'.format(prices[maximum]-prices[minimum]))
    return [minimum, maximum]

def getFees(prices):
    #open file with json of fees and return dict of fees for the prices keys
    pass

def printj(js):
    print(json.dumps(js, indent=2))

# use cryptocompare to GET the data
# use individual apis for each exchange ugh

if __name__ == '__main__':
    cc_key = loadKey('keys/cryptocompare')
    exchanges = ['binanceusa','bittrex', 'kraken', 'bitfinex', 'bitstamp', 'gemini']
    prices = getPrices('BTC',exchanges, cc_key)
    print('At',datetime.datetime.now())
    printj(prices)
    # code fees for each exchange in a json file