import alpaca_trade_api as alpaca

__author__ = 'Calvin Kinateder'
__email__ = 'calvinkinateder@gmail.com'


class AlpacaTrader:
    def __init__(self, paper=True):
        api_key = open('keys/alpaca_public').read().strip()
        api_secret = open('keys/alpaca_private').read().strip()
        base_url = 'https://paper-api.alpaca.markets'
        if paper:
            base_url = 'https://api.alpaca.markets'
        # or use ENV Vars shown below
        self.api = alpaca.REST(api_key, api_secret,
                               base_url=base_url, api_version='v2')
        # obtain account information
        account = self.api.get_account()
        print(account)


if __name__ == '__main__':
    tester = AlpacaTrader()
