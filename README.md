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
At 2020-12-10 23:55:15.150892
{
  "binanceusa": 17979.2,
  "bittrex": 17995.99,
  "kraken": 17980.3,
  "bitfinex": 18008.0,
  "bitstamp": 17984.82,
  "gemini": 17987.93
}
Lowest = binanceusa at $17979.2
Highest = bitfinex at $18008.0
Difference w/ fees => $18.04

Testing ROI
-----------------------------
ROI w/ $0 invested => $0.00
ROI w/ $10 invested => $0.28
ROI w/ $20 invested => $0.56
ROI w/ $30 invested => $0.84
ROI w/ $40 invested => $1.11
ROI w/ $50 invested => $1.39
ROI w/ $60 invested => $1.67
ROI w/ $70 invested => $1.95
ROI w/ $80 invested => $2.23
ROI w/ $90 invested => $2.51
```

Keep in mind this is meant to be traded up to every 10 seconds, so these values compounded == $$$.

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
