#!/usr/bin/env python
# coding: utf-8
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM
from sklearn.preprocessing import MinMaxScaler
from matplotlib.pylab import rcParams
import matplotlib.pyplot as plt

#setting figure size
rcParams['figure.figsize'] = 20,10

scaler = MinMaxScaler(feature_range=(0, 1))

#read the file
df = pd.read_csv('data/overnight_data.csv')

#print the head
print(df.head())

#setting index as date
df['date'] = pd.to_datetime(df.unix,unit='s') # UNITS IS IMPORTANT
df.index = df.date
#plot
print(df.head())
print(df.keys())

def plotSave(series, xlabel, ylabel, title, legend, filename): # series must be an array
    plt.clf()
    plt.figure(figsize=(16,8))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    for line in series:    
        plt.plot(line)
    plt.legend(legend, loc=4)
    plt.savefig('chart/'+filename)

plotSave([df.close], 'Date', 'Bitcoin Price (USD)', 'Hourly Close Price History', ['Prices'], 'hourly_prices.png') 
#this pointless ngl. don't use the function ^

midpoint = int(len(df.index)*(4/5))
lookback = 10 # 10 is good
epochs = 13
units = 65 # 65 is good
batch_size = 1 # 2 is good

print('midpoint =',midpoint,'\nlookback =',lookback,'\nepochs =',epochs,'\nunits =',units,'\nbatch_size =',batch_size)

def trainModel(df, midpoint, lookback, epochs, units, batch_size):
    #creating dataframe
    data = df.sort_index(ascending=True, axis=0)
    new_data = pd.DataFrame(index=range(0,len(df)),columns=['date', 'close'])
    for i in range(0,len(data)):
        #new_data['date'][i] = data['date'][i] #convert from unix to date here
        new_data['date'][i] = data['date'][i]
        new_data['close'][i] = data['close'][i]

    #setting index
    new_data.index = new_data.date
    new_data.drop('date', axis=1, inplace=True)
    #creating train and test sets
    dataset = new_data.values

    train = dataset[0:midpoint,:]

    #converting dataset into x_train and y_train
    scaled_data = scaler.fit_transform(dataset)

    x_train, y_train = [], []
    for i in range(lookback,len(train)):
        x_train.append(scaled_data[i-lookback:i,0])
        y_train.append(scaled_data[i,0])

    x_train, y_train = np.array(x_train), np.array(y_train) # convert to numpy array

    '''
    We need to convert our data into three-dimensional format. The first dimension is 
    the number of records or rows in the dataset. The second dimension is the number 
    of time steps which is 60 while the last dimension is the number of indicators. 
    Since we are only using one features, the number of indicators will be one. 
    '''
    x_train = np.reshape(x_train, (x_train.shape[0],x_train.shape[1],1))

    # create and fit the LSTM network
    model = Sequential()
    model.add(LSTM(units=units, return_sequences=True, input_shape=(x_train.shape[1],1))) #units=hidden state length
    model.add(LSTM(units=units))
    model.add(Dense(1))

    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size, verbose=2)
    return model, new_data

model, new_data = trainModel(df, midpoint, lookback, epochs, units, batch_size)
#for normalizing data

def predictNext(inputs):
    X_test = []
    for i in range(lookback,inputs.shape[0]):
        X_test.append(inputs[i-lookback:i,0])
    X_test = np.array(X_test)
    X_test = np.reshape(X_test, (X_test.shape[0],X_test.shape[1],1))
    closing_price = model.predict(X_test) #~!!!
    closing_price = scaler.inverse_transform(closing_price)
    rms=np.sqrt(np.mean(np.power((new_data.values[midpoint:,:]-closing_price),2)))
    print('RMS:',rms)
    return closing_price

def conformInputs(inputs):
    inputs = inputs.reshape(-1,1)
    inputs = scaler.transform(inputs)
    return inputs

#predicting values, using past lookback from the train data
# REPLACE?APPEND? THE 10 MOST RECENT VALUES TO THIS
inputs = new_data[len(new_data) - len(new_data.values[midpoint:,:]) - lookback:].values # last section of test data

inputs = conformInputs(inputs)
next_price = predictNext(inputs)

predictions = pd.DataFrame()
predictions['date'] = new_data[midpoint:].index
predictions.index = predictions['date']
predictions['price'] = next_price

def getSlope(nextdf):
    return pd.Series(np.gradient(nextdf.values), nextdf.index, name='slope')

def calcError(actual_slope, pred_slope):    
    tally = 0
    for i in range(0,actual_slope.size):
        #print(actual_slope[i],' ',pred_slope[i])
        if (actual_slope[i]<0 and pred_slope[i]> 0) or (actual_slope[i]>0 and pred_slope[i]< 0):
            tally+=1
    perc_correct = (1-(tally/actual_slope.size))*100

    print('Derivative correct {:.1f}%'.format(perc_correct))
    return perc_correct

predictions['slope'] = getSlope(predictions.price)
actual_slope = getSlope(new_data[midpoint:].close)

r = calcError(predictions.slope, actual_slope)

difference = (predictions.slope - actual_slope)/actual_slope # how far off

# save graphs
plotSave([new_data.close,predictions.price], 'Date', 'Bitcoin Price (USD)', 'Bitcoin Price History + Predictions', ['Actual', 'Predicted'], 'predictions.png') 
plotSave([new_data[midpoint:].close, predictions.price], 'Date', 'Bitcoin Price (USD)', 'Bitcoin Price History + Predictions (zoomed)', ['Actual', 'Predicted'], 'predictions_zoomed.png') 
plotSave([actual_slope, predictions.slope], 'Date', 'Change in Bitcoin Price (USD)', 'Change in Bitcoin Price History + Predictions (zoomed)', ['Actual', 'Predicted'], 'slope.png') 
plotSave([difference], 'Date', 'Percent Change in Bitcoin Price (USD)', 'Error Change in Bitcoin Price History + Predictions (zoomed)', ['Error'], 'error.png') 

print(predictions)