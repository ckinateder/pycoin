# pycoin

PyCoin is an automated cryptocurrency trading application. Right now it is just a pet project, but will hopefully become more than that soon. It consists of two parts – intermarket arbitrage, and intramarket arbitrage. Both are very much a work in progress.

## Intermarket

This side of pycoin will scan given markets for each's crypto price, make a decision on the greatest difference between the two, buy at the lowest, and sell at the highest – all with in the same moment.

Example call for prices: 
```
Asking for BTC on binanceusa...
Asking for BTC on bittrex...
Asking for BTC on kraken...
Asking for BTC on bitfinex...
Asking for BTC on bitstamp...
Asking for BTC on gemini...
At 2020-12-11 00:19:20.161191
{
  "binanceusa": 17937.43,
  "bittrex": 17946.22,
  "kraken": 17937.8,
  "bitfinex": 17960.0,
  "bitstamp": 17940.11,
  "gemini": 17937.72
}
Lowest = binanceusa at $17937.43
Highest = bitfinex at $17960.0
Difference w/ fees => $17.98

Testing ROI
-----------------------------
Net ROI w/ $10 invested => $0.0001
Net ROI w/ $20 invested => $0.0001
Net ROI w/ $30 invested => $0.0002
Net ROI w/ $40 invested => $0.0002
Net ROI w/ $50 invested => $0.0003
Net ROI w/ $60 invested => $0.0003
Net ROI w/ $70 invested => $0.0004
Net ROI w/ $80 invested => $0.0004
Net ROI w/ $90 invested => $0.0005
Net ROI w/ $100 invested => $0.0006
...Net ROI w/ $500 invested => $0.0028
...Net ROI w/ $1000 invested => $0.0056
```

Keep in mind this is meant to be traded up to every 10 seconds, so these values compounded == $$$. Or, at least $.

## Intramarket

An automated speed trading algorithm for cryprocurrency using LSTM. Cryptocurrency was chosen over the stock market due to the limits on trading frequency with less than $25K in your portfolio. The goal of this algorithm is to predict with a >51% gain or loss on bitcoin within the second and then make a trade based on that data.

### Charts
Historical hourly Bitcoin prices –
![Hourly prices](chart/hourly_prices.png)
Historical prices + predicted with actual prices –
![Predictions](chart/predictions.png)
Historical prices + predicted with actual prices (zoomed in) –
![Zoomed Predictions](chart/predictions_zoomed.png)
Rate of change of predicted prices –
![Slope](chart/slope.png)
