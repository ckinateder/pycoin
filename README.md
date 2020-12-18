# pycoin

PyCoin is an automated cryptocurrency trading application. Right now it is just a pet project, but will hopefully become more than that soon. It consists of two parts – intermarket arbitrage, and intramarket arbitrage. Both are very much a work in progress.

## Intramarket

An automated speed trading algorithm for cryprocurrency using LSTM. Cryptocurrency was chosen over the stock market due to the limits on trading frequency with less than $25K in your portfolio. The goal of this algorithm is to predict with a >51% gain or loss on bitcoin within the second and then make a trade based on that data.

### Trading Logic

The trading logic used for this is based on the derivative of the predictions graph. Currently the algorithm is able to correctly predict whether the crypto price is increasing or decreasing no less than 80% of the time. I have found the model to perform best with the lookback set to `10`, epochs between `10` and `15`, and units to `65`. As far as structure goes – the main class will be `CryptoTrader`. It will incorporate `CrytoPredict` and `KrakenTrader` and bring them together in one class for a fully functioned release.

```
$ python3 CryptoTrader.py

midpoint = 2973 
lookback = 15 
epochs = 15 
units = 70 
batch_size = 1

Epoch 1/15
2958/2958 - 14s - loss: 0.0016
Epoch 2/15
2958/2958 - 13s - loss: 3.7860e-04
Epoch 3/15
2958/2958 - 13s - loss: 2.5028e-04
Epoch 4/15
2958/2958 - 13s - loss: 2.1414e-04
Epoch 5/15
2958/2958 - 13s - loss: 1.8036e-04
Epoch 6/15
2958/2958 - 13s - loss: 1.8532e-04
Epoch 7/15
2958/2958 - 12s - loss: 1.7738e-04
Epoch 8/15
2958/2958 - 12s - loss: 1.6096e-04
Epoch 9/15
2958/2958 - 13s - loss: 1.7846e-04
Epoch 10/15
2958/2958 - 13s - loss: 1.6599e-04
Epoch 11/15
2958/2958 - 13s - loss: 1.4877e-04
Epoch 12/15
2958/2958 - 13s - loss: 1.4937e-04
Epoch 13/15
2958/2958 - 13s - loss: 1.4104e-04
Epoch 14/15
2958/2958 - 13s - loss: 1.4720e-04
Epoch 15/15
2958/2958 - 12s - loss: 1.3790e-04
Saved model to disk
-0.6933594 -0.7000000000007276
Derivative correct 76.3%
                                      price     slope
date                                                 
2020-12-18 13:43:18.270774364  22824.494141 -0.693359
2020-12-18 13:43:28.515594006  22823.800781 -0.701172
2020-12-18 13:43:38.794413090  22823.091797 -0.593750
2020-12-18 13:43:49.047344685  22822.613281 -0.541992
2020-12-18 13:43:59.322089195  22822.007812 -0.284180
...                                     ...       ...
2020-12-18 15:49:37.415970564  22470.824219  3.090820
2020-12-18 15:49:47.644010067  22483.535156 -0.080078
2020-12-18 15:49:57.894225121  22470.664062 -3.223633
2020-12-18 15:50:08.085751534  22477.087891  1.916016
2020-12-18 15:50:18.379809141  22474.496094 -2.591797

[744 rows x 2 columns]
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