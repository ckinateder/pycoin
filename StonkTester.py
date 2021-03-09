from CryptoPredict import CryptoPredictor
import sys
import datetime
import pandas as pd
from pathlib import Path


def testModel(stonk_predictor):
    df = stonk_predictor.createFrame()

    stonk_predictor.midpoint = int(len(df.index) * (3 / 4))  # have to set after df init

    print(
        "midpoint =",
        stonk_predictor.midpoint,
        "\nlookback =",
        stonk_predictor.lookback,
        "\nepochs =",
        stonk_predictor.epochs,
        "\nunits =",
        stonk_predictor.units,
        "\nbatch_size =",
        stonk_predictor.batch_size,
    )

    model, new_data = stonk_predictor.trainModel(
        df,
        stonk_predictor.lookback,
        stonk_predictor.epochs,
        stonk_predictor.units,
        stonk_predictor.batch_size,
    )
    # predicting values, using past lookback from the train data

    # REPLACE?APPEND? THE 10 MOST RECENT VALUES TO THIS
    inputs = new_data[
        len(new_data)
        - len(new_data.values[stonk_predictor.midpoint :, :])
        - stonk_predictor.lookback :
    ].values  # last section of test data
    inputs = stonk_predictor.conformInputs(inputs)
    # note that this has validation built in
    next_prices = stonk_predictor.predictNextValue(inputs, model)

    predictions = pd.DataFrame()
    predictions["date"] = new_data[stonk_predictor.midpoint :].index
    predictions.index = predictions["date"]
    predictions.drop("date", axis=1, inplace=True)  # drop duplicate column
    predictions["price"] = next_prices

    predictions["slope"] = stonk_predictor.getGradient(predictions.price)
    actual_slope = stonk_predictor.getGradient(
        new_data[stonk_predictor.midpoint :].close
    )

    # print(predictions.slope[0],actual_slope[0])

    r = stonk_predictor.calcError(predictions.slope, actual_slope)
    difference = (predictions.slope - actual_slope) / actual_slope  # how far off

    # save graphs
    folder_path = (
        "chart/"
        + "tests/"
        + datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
        + "/"
    )
    Path(folder_path).mkdir(parents=True, exist_ok=True)  # make directory

    stonk_predictor.plotSave(
        [df[stonk_predictor.important_headers["price"]]],
        "Date",
        "{} Price (USD)".format(stonk_predictor.pair[0]),
        "Price History",
        ["Prices"],
        folder_path + "hourly_prices.png",
    )
    stonk_predictor.plotSave(
        [new_data.close, predictions.price],
        "Date",
        "{} Price (USD)".format(stonk_predictor.pair[0]),
        "{} Price History + Predictions".format(stonk_predictor.pair[0]),
        ["Actual", "Predicted"],
        folder_path + "predictions.png",
    )
    stonk_predictor.plotSave(
        [new_data[stonk_predictor.midpoint :].close, predictions.price],
        "Date",
        "{} Price (USD)".format(stonk_predictor.pair[0]),
        "{} Price History + Predictions (zoomed)".format(stonk_predictor.pair[0]),
        ["Actual", "Predicted"],
        folder_path + "predictions_zoomed.png",
    )
    stonk_predictor.plotSave(
        [actual_slope, predictions.slope],
        "Date",
        "Change in {} Price (USD)".format(stonk_predictor.pair[0]),
        "Change in {} Price History + Predictions (zoomed)".format(
            stonk_predictor.pair[0]
        ),
        ["Actual", "Predicted"],
        folder_path + "slope.png",
    )
    stonk_predictor.plotSave(
        [difference],
        "Date",
        "Percent Change in {} Price (USD)".format(stonk_predictor.pair[0]),
        "Error % Change in {} Price History + Predictions (zoomed)".format(
            stonk_predictor.pair[0]
        ),
        ["Error"],
        folder_path + "error.png",
    )

    # write params to file
    params = "ticker={}\nlookback={}\ncutpoint={}\nepochs={}\nunits={}\nr^2={}\ndataset size={}".format(
        stonk_predictor.pair[0],
        stonk_predictor.lookback,
        stonk_predictor.cutpoint,
        stonk_predictor.epochs,
        stonk_predictor.units,
        r,
        len(new_data.index),
    )
    with open((folder_path + "params.txt"), "w+") as f:
        f.write(params)

    print(predictions)


if __name__ == "__main__":
    pair = ["tsla", "usd"]
    if len(sys.argv) == 2:
        pair = [sys.argv[1], "usd"]
    stonk_predictor = CryptoPredictor(
        pair=pair, cutpoint=1800, epochs=15, units=256, lookback=1
    )
    print(
        "Predicting with [ticker={}, cutpoint={}, epochs={}, units={}".format(
            stonk_predictor.pair[0],
            stonk_predictor.cutpoint,
            stonk_predictor.epochs,
            stonk_predictor.units,
        )
    )
    testModel(stonk_predictor)
