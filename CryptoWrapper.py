import requests, json, datetime
#using crypto compare

#load api_key

class CryptoWrapper:
    def __init__(self, key, exchanges):
        self.key = key
        self.exchanges = exchanges

    def getExchanges(self, filename):
        try:
            exc = requests.get('https://min-api.cryptocompare.com/data/exchanges/general?'+
                                key).json()['Data']
            with open(filename, 'w') as outfile:
                json.dump(exc, outfile)
            return exc
        except:
            return -1    

    def getPrices(self, currency, exchanges=None): #returns dictionary
        if exchanges is None:
            exchanges = self.exchanges
        summation = {}
        for exc in exchanges:
            call = 'https://min-api.cryptocompare.com/data/price?fsym='+currency+'&tsyms=USD&e='+exc+'&api_key='+self.key
            print('Asking for',currency,'on '+exc+'...')
            try:
                recieved = requests.get(call).json()['USD']
            except:
                recieved = 'NA'
            summation[exc] = float(recieved) # return dict
        return summation

    def getLowHiPair(self, prices): #returns min and max
        minimum = min(prices, key=prices.get)
        maximum = max(prices, key=prices.get)
        print('Lowest =',minimum,'at $'+str(prices[minimum]))
        print('Highest =',maximum,'at $'+str(prices[maximum]))
        print('Difference => ${:.2f}'.format(prices[maximum]-prices[minimum]))
        return [minimum, maximum]

    def getFees(self, prices):
        #open file with json of fees and return dict of fees for the prices keys
        pass

    def printj(self, js):
        print(json.dumps(js, indent=2))