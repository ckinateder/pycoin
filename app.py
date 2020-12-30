from CryptoTrader import ThreadedTrader
import sys
import webserver

if __name__ == '__main__':
    '''
    Sample call -
    $ python3 app.py xbt usd 500
    '''
    headers = {
        'timestamp': 'unix',
        'price': 'a'  # the column used for price
    }

    if len(sys.argv) == 4:
        pair = sys.argv[1:3]
        invest = float(sys.argv[3])
    else:
        # default
        print('Not enough arguments given - must be in format\n  $ python3 CryptoTrader.py (crypto) (usd) (amount to invest)')
        pair = ['eth', 'usd']
        invest = 200
        print('Using default values: {} and ${}'.format(pair, invest))

    #webserver.main()
    threader = ThreadedTrader(
        pair=pair, headers=headers, retrain_every=10, initial_investment=invest)
    threader.run()
