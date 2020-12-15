import kraken, json, pprint, pandas, time

kt = kraken.KrakenTrader()
reply = json.loads(kt.main(['Ticker', 'pair=xbtusd']))['result']['XXBTZUSD']

header = list()
total = list()

for i in reply.items():
    header.append(i[0])
total.append(header)

while True:
    reply = json.loads(kt.main(['Ticker', 'pair=xbtusd']))['result']['XXBTZUSD']
    dropped = list()
    dropped.append(time.time())
    for i in reply.values():
        dropped.append(i[0])
    print(dropped)
    total.append(dropped)
    pandas.DataFrame(total).to_csv("overnight_data.csv", mode='a', header=False)
    time.sleep(10)
