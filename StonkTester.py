from CryptoPredict import CryptoPredictor
import sys
import datetime
import pandas as pd
from pathlib import Path


def testModel(stonker):
    df = stonker.createFrame()

    stonker.midpoint = int(len(df.index)*(3/4))  # have to set after df init

    print('midpoint =', stonker.midpoint, '\nlookback =', stonker.lookback, '\nepochs =',
          stonker.epochs, '\nunits =', stonker.units, '\nbatch_size =', stonker.batch_size)

    model, new_data = stonker.trainModel(
        df, stonker.lookback, stonker.epochs, stonker.units, stonker.batch_size)
    # predicting values, using past lookback from the train data

    # REPLACE?APPEND? THE 10 MOST RECENT VALUES TO THIS
    inputs = new_data[len(new_data) - len(new_data.values[stonker.midpoint:, :]
                                          ) - stonker.lookback:].values  # last section of test data
    inputs = stonker.conformInputs(inputs)
    # note that this has validation built in
    next_prices = stonker.predictNextValue(inputs, model)

    predictions = pd.DataFrame()
    predictions['date'] = new_data[stonker.midpoint:].index
    predictions.index = predictions['date']
    predictions.drop('date', axis=1, inplace=True)  # drop duplicate column
    predictions['price'] = next_prices

    predictions['slope'] = stonker.getGradient(predictions.price)
    actual_slope = stonker.getGradient(new_data[stonker.midpoint:].close)

    # print(predictions.slope[0],actual_slope[0])

    r = stonker.calcError(predictions.slope, actual_slope)
    difference = (predictions.slope - actual_slope) / \
        actual_slope  # how far off

    # save graphs
    folder_path = 'chart/'+'tests/' + \
        datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")+'/'
    Path(folder_path).mkdir(parents=True,
                            exist_ok=True)  # make directory

    stonker.plotSave([df[stonker.important_headers['price']]], 'Date',
                     '{} Price (USD)'.format(stonker.pair[0]), 'Price History', ['Prices'], folder_path+'hourly_prices.png')
    stonker.plotSave([new_data.close, predictions.price], 'Date', '{} Price (USD)'.format(stonker.pair[0]),
                     '{} Price History + Predictions'.format(
        stonker.pair[0]), ['Actual', 'Predicted'], folder_path+'predictions.png')
    stonker.plotSave([new_data[stonker.midpoint:].close, predictions.price], 'Date', '{} Price (USD)'.format(stonker.pair[0]),
                     '{} Price History + Predictions (zoomed)'.format(
        stonker.pair[0]), ['Actual', 'Predicted'], folder_path+'predictions_zoomed.png')
    stonker.plotSave([actual_slope, predictions.slope], 'Date', 'Change in {} Price (USD)'.format(stonker.pair[0]),
                     'Change in {} Price History + Predictions (zoomed)'.format(
        stonker.pair[0]), ['Actual', 'Predicted'], folder_path+'slope.png')
    stonker.plotSave([difference], 'Date', 'Percent Change in {} Price (USD)'.format(stonker.pair[0]),
                     'Error % Change in {} Price History + Predictions (zoomed)'.format(
        stonker.pair[0]), ['Error'], folder_path+'error.png')

    # write params to file
    params = 'ticker={}\nlookback={}\ncutpoint={}\nepochs={}\nunits={}\nr^2={}\ndataset size={}'.format(
        stonker.pair[0], stonker.lookback, stonker.cutpoint, stonker.epochs, stonker.units, r, len(new_data.index))
    with open((folder_path+'params.txt'), 'w+') as f:
        f.write(params)

    print(predictions)


if __name__ == '__main__':
    pair = ['tsla', 'usd']
    if len(sys.argv) == 2:
        pair = [sys.argv[1], 'usd']
    stonker = CryptoPredictor(pair=pair, cutpoint=1800,
                              epochs=15, units=256, lookback=1)
    print('Predicting with [ticker={}, cutpoint={}, epochs={}, units={}'.format(
        stonker.pair[0], stonker.cutpoint, stonker.epochs, stonker.units))
    testModel(stonker)
