import kraken, json, pprint, pandas, time, os

filename = 'overnight_data.csv'

kt = kraken.KrakenTrader()
reply = json.loads(kt.main(['Ticker', 'pair=xbtusd']))['result']['XXBTZUSD']

if not os.path.isfile(filename): # only add header if file doesnt exist
    header = list()
    header.append('unix')
    for i in reply.items():
        header.append(i[0])
    #total.append(header)
    pandas.DataFrame([header]).to_csv(filename, mode='a', header=False,index=False)

while True:
    try:
        reply = json.loads(kt.main(['Ticker', 'pair=xbtusd']))['result']['XXBTZUSD']
        dropped = list()
        dropped.append(time.time())
        for i in reply.values():
            dropped.append(i[0])
        print(dropped)
        pandas.DataFrame([dropped]).to_csv(filename, mode='a', header=False,index=False)
        time.sleep(10)
    except:
        print('Call failed... trying again in 5')
        time.sleep(5)
