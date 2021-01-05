import alpaca_trade_api as alpaca
import pandas
import os
import json
import logging
import requests

__author__ = 'Calvin Kinateder'
__email__ = 'calvinkinateder@gmail.com'


class AlpacaTrader:
    def __init__(self, paper=True):
        api_key = open('keys/alpaca_public').read().strip()
        api_secret = open('keys/alpaca_private').read().strip()
        base_url = 'https://api.alpaca.markets'
        if paper:
            api_key = open('keys/alpaca_paper_public').read().strip()
            api_secret = open('keys/alpaca_paper_private').read().strip()
            base_url = 'https://paper-api.alpaca.markets'
        # or use ENV Vars shown below
        self.api = alpaca.REST(api_key, api_secret,
                               base_url=base_url, api_version='v2')
        # obtain account information

    def cleanup(self, filename, how_far_back):
        '''
        Cleans up the file so it doesn't overflow memory.
        '''

        whole_file = pandas.read_csv(filename)
        whole_file = whole_file.drop_duplicates()
        whole_file.to_csv(filename, index=False)
        num_lines = sum(1 for line in open(filename))
        if num_lines > how_far_back:
            end = num_lines-how_far_back

            parsed = whole_file.drop(list(range(0, end)))
            parsed.to_csv(filename, index=False)
            # drop early rows and then rewrite NOT APPEND

    def saveTickerPair(self, pair):
        '''
        Saves latest price to file.
        '''
        ticker = pair[0]
        quote = self.api.get_last_quote(ticker.upper()).__dict__['_raw']
        filename = 'data/'+'-'.join(pair)+'_alpaca.csv'
        if not os.path.isfile(filename):
            header = list()
            for i in quote.items():
                header.append(i[0])
            pandas.DataFrame([header]).to_csv(
                filename, mode='a', header=False, index=False)

        dropped = list()

        quote['timestamp'] = quote['timestamp']/1000000  # convert from us to s
        print('Recieved from \'{}\': {}'.format(ticker, quote))

        for i in quote.values():
            dropped.append(i)

        pandas.DataFrame([dropped]).to_csv(
            filename, mode='a', header=False, index=False)
        self.cleanup(filename, 4096)
        return quote

    def submitOrder(self, ticker, side, qty):
        '''
        Submit a market order.
        '''
        if qty == 0:
            logging.warning('Passed qty of 0 - won\'t trade')
            return False
        self.api.submit_order(
            symbol=ticker,
            side=side,
            type='market',
            qty=qty,
            time_in_force='day',
        )
        return self.api.list_orders()

    def anyOpen(self, ticker):
        '''
        Checks to see if any orders are still open.
        '''
        listed = self.api.list_orders(
            status='open',
        )
        if len(listed) != 0:
            return True
        else:
            return False

    def getCash(self):
        return float(self.api.get_account().cash)

    def getPosition(self, ticker):
        try:
            return float(self.api.get_position(ticker).qty)
        except:
            return 0

    def listPositions(self):
        return self.api.list_positions()

    def test(self):
        print(self.saveTickerPair('TSLA'))


if __name__ == '__main__':
    headers = {
        'timestamp': 'timestamp',
        'price': 'askprice'  # the column used for price
    }
    tester = AlpacaTrader(paper=True)
    print(tester.getCash())
    print(tester.getPosition('TSLA'))
    print(tester.listPositions())
