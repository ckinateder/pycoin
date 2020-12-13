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

#for normalizing data
scaler = MinMaxScaler(feature_range=(0, 1))

#read the file
df = pd.read_csv('data/Binance_BTCUSDT_1h.csv')

#print the head
print(df.head())

#setting index as date
df.keys()
df['date'] = pd.to_datetime(df.date)
df.index = df['date']

#plot

def plot_and_save(series, xlabel, ylabel, title, legend, filename):
    plt.clf()
    plt.figure(figsize=(16,8))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)    
    plt.plot(series)
    plt.legend(legend, loc=4)
    plt.savefig('chart/'+filename)

plot_and_save(df['close'], 'Date', 'Bitcoin Price (USD)', 'Hourly Close Price History', ['Prices'], 'hourly_prices.png') 
#this pointless ngl. don't use the function ^

midpoint = 2350
lookback = 10

#creating dataframe
data = df.sort_index(ascending=True, axis=0)
new_data = pd.DataFrame(index=range(0,len(df)),columns=['date', 'close'])
for i in range(0,len(data)):
    new_data['date'][i] = data['date'][i]
    new_data['close'][i] = data['close'][i]

#setting index
new_data.index = new_data.date
new_data.drop('date', axis=1, inplace=True)

#creating train and test sets
dataset = new_data.values

train = dataset[0:midpoint,:]
valid = dataset[midpoint:,:]

#converting dataset into x_train and y_train
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(dataset)

x_train, y_train = [], []
for i in range(lookback,len(train)):
    x_train.append(scaled_data[i-lookback:i,0])
    y_train.append(scaled_data[i,0])
x_train, y_train = np.array(x_train), np.array(y_train)

x_train = np.reshape(x_train, (x_train.shape[0],x_train.shape[1],1))

# create and fit the LSTM network
model = Sequential()
model.add(LSTM(units=65, return_sequences=True, input_shape=(x_train.shape[1],1))) #units=hidden state length
model.add(LSTM(units=65))
model.add(Dense(1))

model.compile(loss='mean_squared_error', optimizer='adam')
model.fit(x_train, y_train, epochs=4, batch_size=1, verbose=2)

#predicting values, using past lookback from the train data
inputs = new_data[len(new_data) - len(valid) - lookback:].values
inputs = inputs.reshape(-1,1)
inputs = scaler.transform(inputs)

X_test = []
for i in range(lookback,inputs.shape[0]):
    X_test.append(inputs[i-lookback:i,0])
X_test = np.array(X_test)

X_test = np.reshape(X_test, (X_test.shape[0],X_test.shape[1],1))
closing_price = model.predict(X_test) #~!!!
closing_price = scaler.inverse_transform(closing_price)

rms=np.sqrt(np.mean(np.power((valid-closing_price),2)))
rms

#for plotting
train = new_data[:midpoint]
valid = new_data[midpoint:]
valid['predictions'] = closing_price

# use standalone code because function is special enough
plt.clf()
plt.xlabel('Date')
plt.ylabel('Bitcoin Price (USD)')
plt.title('Bitcoin Price History + Predictions')    
plt.plot(train['close'])
plt.plot(valid['close'], label='close')
plt.plot(valid['predictions'], label='predictions')
plt.legend(['Actual', 'Predicted'], loc=4)
plt.savefig('chart/predictions.png')

# plot zoomed
plt.clf()
plt.xlabel('Date')
plt.ylabel('Bitcoin Price (USD)')
plt.title('Bitcoin Price Predictions (zoomed)')    
plt.plot(valid[['close','predictions']])
plt.legend(['Actual', 'Predicted'], loc=4)
plt.savefig('chart/predictions_zoomed.png')

pred_slope = pd.Series(np.gradient(valid.predictions.values), valid.predictions.index, name='slope')
actual_slope = pd.Series(np.gradient(valid.close.values), valid.close.index, name='slope')

df = pd.concat([valid.predictions.rename('predictions'), pred_slope], axis=1)
print(df)

plt.clf()
plt.xlabel('Date')
plt.ylabel('Change in Bitcoin Price (USD)')
plt.title('Change in Bitcoin Price Predictions')
plt.plot(actual_slope)    
plt.plot(pred_slope)
plt.legend(['Actual', 'Predicted'], loc=4)
plt.savefig('chart/slope.png')

tally = 0
for i in range(0,actual_slope.size):
    #print(actual_slope[i],' ',pred_slope[i])
    if (actual_slope[i]<0 and pred_slope[i]> 0) or (actual_slope[i]>0 and pred_slope[i]< 0):
        tally+=1
print(tally/actual_slope.size)