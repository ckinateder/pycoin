# pycoin

PyCoin is an automated cryptocurrency trading application. Right now it is just a pet project, but will hopefully become more than that soon. It consists of two parts – intermarket arbitrage, and intramarket arbitrage. Both are very much a work in progress.

## Intramarket

An automated speed trading algorithm for cryprocurrency using LSTM. Cryptocurrency was chosen over the stock market due to the limits on trading frequency with less than $25K in your portfolio. The goal of this algorithm is to predict with a >51% gain or loss on bitcoin within the second and then make a trade based on that data.

### Trading Logic

The trading logic used for this is based on the derivative of the predictions graph. Currently the algorithm is able to correctly predict whether the crypto price is increasing or decreasing no less than 80% of the time. I have found the model to perform best with the lookback set to `10`, epochs between `10` and `15`, and units to `65`. As far as structure goes – the main class will be `CryptoTrader`. It will incorporate `CrytoPredict` and `KrakenTrader` and bring them together in one class for a fully functioned release.

```
$ python3 CryptoTrader.py

Saved plot Hourly Close Price History
midpoint = 1800 
lookback = 1 
epochs = 13 
units = 256 
batch_size = 1

Epoch 1/13
1799/1799 - 5s - loss: 0.0038
Epoch 2/13
1799/1799 - 5s - loss: 4.0020e-04
Epoch 3/13
1799/1799 - 4s - loss: 4.8217e-04
Epoch 4/13
1799/1799 - 5s - loss: 4.3370e-04
Epoch 5/13
1799/1799 - 5s - loss: 3.8176e-04
Epoch 6/13
1799/1799 - 5s - loss: 4.0487e-04
Epoch 7/13
1799/1799 - 5s - loss: 4.2265e-04
Epoch 8/13
1799/1799 - 5s - loss: 3.9150e-04
Epoch 9/13
1799/1799 - 5s - loss: 3.7182e-04
Epoch 10/13
1799/1799 - 5s - loss: 3.4439e-04
Epoch 11/13
1799/1799 - 5s - loss: 3.4022e-04
Epoch 12/13
1799/1799 - 5s - loss: 3.1977e-04
Epoch 13/13
1799/1799 - 5s - loss: 3.3645e-04
Saved model to disk
Derivative correct 84.2%
Saved plot Bitcoin Price History + Predictions
Saved plot Bitcoin Price History + Predictions (zoomed)
Saved plot Change in Bitcoin Price History + Predictions (zoomed)
Saved plot Error Change in Bitcoin Price History + Predictions (zoomed)
                                      price     slope
date                                                 
2020-12-18 17:41:03.557963610  22766.437500  0.000000
2020-12-18 17:41:13.855086803  22766.437500  0.000000
2020-12-18 17:41:24.052181244  22766.437500  0.000000
2020-12-18 17:41:34.330092907  22766.437500  0.000000
2020-12-18 17:41:44.845845222  22766.437500 -1.244141
...                                     ...       ...
2020-12-18 19:22:50.398678541  22755.033203  0.000000
2020-12-18 19:23:00.681419611  22755.033203  0.000000
2020-12-18 19:23:10.906343222  22755.033203  0.000000
2020-12-18 19:23:21.398822546  22755.033203  0.000000
2020-12-18 19:23:31.702734232  22755.033203  0.000000

[600 rows x 2 columns]
```

### Charts
Historical hourly Bitcoin prices –
![Hourly prices](chart/hourly_prices.png)
Historical prices + predicted with actual prices –
![Predictions](chart/predictions.png)
Historical prices + predicted with actual prices (zoomed in) –
![Zoomed Predictions](chart/predictions_zoomed.png)
Rate of change of predicted prices –
![Slope](chart/slope.png)
Perent error in rate of change of predicted prices –
![Error](chart/error.png)

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
At 2020-12-11 10:19:47.768476
{
  "binanceusa": 18058.85,
  "bittrex": 18073.28,
  "kraken": 18070.1,
  "bitfinex": 18087.0,
  "bitstamp": 18070.29,
  "gemini": 18074.83
}
Lowest = binanceusa at $18058.85
Highest = bitfinex at $18087.0
Gross difference => $28.15

Testing ROI per transaction
-----------------------------
Net ROI w/ $10 invested => $0.0255
Net ROI w/ $20 invested => $0.0511
Net ROI w/ $30 invested => $0.0766
Net ROI w/ $40 invested => $0.1021
Net ROI w/ $50 invested => $0.1276
Net ROI w/ $60 invested => $0.1532
Net ROI w/ $70 invested => $0.1787
Net ROI w/ $80 invested => $0.2042
Net ROI w/ $90 invested => $0.2298
Net ROI w/ $100 invested => $0.2553
...Net ROI w/ $500 invested => $1.2764
...Net ROI w/ $1000 invested => $2.5528
...Net ROI w/ $3000 invested => $7.6585
...Net ROI w/ $9000 invested => $22.9754
```

Keep in mind this is meant to be traded up to every 10 seconds, so these values compounded == $$$. Or, at least $.