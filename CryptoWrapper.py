import requests, json, datetime
#using crypto compare

#load api_key

class CryptoWrapper:
    def __init__(self, key, exchanges):
        self.key = key
        self.exchanges = exchanges
        self.base_url = 'https://min-api.cryptocompare.com/data/'

    def getExchanges(self, filename):
        try:
            exc = requests.get(self.base_url+'exchanges/general?'+
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
            call = self.base_url+'price?fsym='+currency+'&tsyms=USD&e='+exc+'&api_key='+self.key
            print('Asking for',currency,'on '+exc+'...')
            try:
                recieved = requests.get(call).json()['USD']
            except:
                recieved = 'NA'
            summation[exc] = float(recieved) # return dict
        return summation

    def getLowHiPair(self, prices, fees=True): #returns min and max
        minimum = min(prices, key=prices.get)
        maximum = max(prices, key=prices.get)
        print('Lowest =',minimum,'at $'+str(prices[minimum]))
        print('Highest =',maximum,'at $'+str(prices[maximum]))
        print('Gross difference => ${:.2f}'.format(prices[maximum]-prices[minimum]))
        if fees:
            self.getFees()
            hiwfee = prices[maximum]*(1-(self.fees[maximum]['taker']*0.01)) #is this right?
            lowwfee = prices[minimum]*(1-(self.fees[minimum]['taker']*0.01))
            #print('Difference w/ fees => ${:.2f}'.format(hiwfee-lowwfee))
        return [prices[minimum], prices[maximum], minimum, maximum] #maybe make into dict

    def getFees(self):
        #open file with json of fees and return dict of fees for the prices keys
        with open('data/fees.json', 'r') as jfees:
            self.fees = json.loads(jfees.read())
    
    def calculateReturn(self, investment, pairs): #meant to recieve out from get hi low pair
        #use fees here not above
        alpha = investment/(pairs[1]*(1+self.fees[pairs[3]]['taker']/100)) # fraction of currency
        dif = (pairs[1]*(1+self.fees[pairs[3]]['taker']/100))-(pairs[0]*(1+self.fees[pairs[2]]['taker']/100))
        ret = alpha*dif
        return ret
    
    def getHistorical(self, howfarback, currency, exchanges=None): #test
        if exchanges is None:
            exchanges = self.exchanges
        each = {}
        for exc in exchanges:
            call = self.base_url+'v2/histominute?fsym='+currency+'&tsym=USD&e='+exc+'&limit='+howfarback+'&api_key='+self.key 
            print('Asking for last',howfarback,'minutes on',exc,'for',currency,'...')
            try:
                recieved = requests.get(call).json()
            except:
                recieved = 'NA'
            each[exc] = recieved # return dict
        return each

    def printj(self, js):
        print(json.dumps(js, indent=2))