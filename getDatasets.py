import CryptoWrapper, json, csv, pprint
# scratch file to get datasets

def loadKey(filename):
    with open(filename, 'r') as key:
        return key.read()

cc_key = loadKey('keys/cryptocompare')
exchanges = ['kraken']
filename = 'data/last1000mins.csv'

with open(filename, mode='w') as datafile:
    DataPi = CryptoWrapper.CryptoWrapper(cc_key, exchanges)
    recall = (DataPi.getHistorical('2000','BTC', ['kraken']))['kraken']['Data']['Data']

    write = csv.writer(datafile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    print('Writing header...')
    write.writerow(recall[0].keys())
    for minute in recall:
        #pprint.pprint(minute)
        write.writerow(minute.values())
    print('Closing file.')
print('Done')
#pprint.pprint()