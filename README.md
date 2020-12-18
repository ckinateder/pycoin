# pycoin

PyCoin is an automated cryptocurrency trading application. Right now it is just a pet project, but will hopefully become more than that soon. It consists of two parts – intermarket arbitrage, and intramarket arbitrage. Both are very much a work in progress.

## Intramarket

An automated speed trading algorithm for cryprocurrency using LSTM. Cryptocurrency was chosen over the stock market due to the limits on trading frequency with less than $25K in your portfolio. The goal of this algorithm is to predict with a >51% gain or loss on bitcoin within the second and then make a trade based on that data.

### Trading Logic

The trading logic used for this is based on the derivative of the predictions graph. Currently the algorithm is able to correctly predict whether the crypto price is increasing or decreasing no less than 80% of the time. I have found the model to perform best with the lookback set to `10`, epochs between `10` and `15`, and units to `65`. As far as structure goes – the main class will be `CryptoTrader`. It will incorporate `CrytoPredict` and `KrakenTrader` and bring them together in one class for a fully functioned release.

```
$ python3 CryptoPredict.py

         unix    close        b  ...        l        h  o
0  1608047145  19393.6  19393.5  ...  19048.9  19551.5  1
1  1608047155  19388.0  19385.7  ...  19048.9  19551.5  1
2  1608047168  19387.0  19385.7  ...  19048.9  19551.5  1
3  1608047178  19386.3  19386.2  ...  19048.9  19551.5  1
4  1608047188  19388.0  19386.8  ...  19048.9  19551.5  1

[5 rows x 10 columns]

Index(['unix', 'close', 'b', 'c', 'v', 'p', 't', 'l', 'h', 'o', 'date'], dtype='object')

midpoint = 2257 
lookback = 10 
epochs = 13 
units = 65 
batch_size = 1

Epoch 1/13
2247/2247 - 8s - loss: 0.0030
Epoch 2/13
2247/2247 - 8s - loss: 9.6016e-04
Epoch 3/13
2247/2247 - 8s - loss: 6.4898e-04
Epoch 4/13
2247/2247 - 8s - loss: 5.7152e-04
Epoch 5/13
2247/2247 - 8s - loss: 6.1073e-04
Epoch 6/13
2247/2247 - 7s - loss: 5.5200e-04
Epoch 7/13
2247/2247 - 8s - loss: 5.1259e-04
Epoch 8/13
2247/2247 - 7s - loss: 5.1466e-04
Epoch 9/13
2247/2247 - 7s - loss: 5.1551e-04
Epoch 10/13
2247/2247 - 7s - loss: 5.3434e-04
Epoch 11/13
2247/2247 - 7s - loss: 4.9744e-04
Epoch 12/13
2247/2247 - 7s - loss: 4.7550e-04
Epoch 13/13
2247/2247 - 8s - loss: 4.8983e-04
RMS: 3.648095667902578
Derivative correct 83.4%
                            price     slope
date                                       
2020-12-16 01:40:18  19367.066406  0.365234
2020-12-16 01:40:28  19367.431641 -0.062500
2020-12-16 01:40:38  19366.941406 -3.123047
2020-12-16 01:40:48  19361.185547 -2.279297
2020-12-16 01:40:59  19362.382812  0.455078
...                           ...       ...
2020-12-16 03:16:17  19425.212891 -0.483398
2020-12-16 03:16:28  19424.423828  0.112305
2020-12-16 03:16:38  19425.437500  0.433594
2020-12-16 03:16:48  19425.291016 -2.908203
2020-12-16 03:16:58  19419.621094 -5.669922

[565 rows x 2 columns]
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