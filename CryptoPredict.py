#!/usr/bin/env python
# coding: utf-8
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM
from keras.models import model_from_json
from sklearn.preprocessing import MinMaxScaler
from matplotlib.pylab import rcParams
import matplotlib.pyplot as plt
import datetime
#setting figure size

class CryptoPredictor:

    def __init__(self, lookback=10,epochs=15,units=65,batch_size=1, important_headers={'timestamp': 'time','price': 'close'}, datafile='', cutpoint=2000):
        self.models_path = 'models/'
        self.csvset = datafile
        self.cutpoint = cutpoint # only use last x datapoints
        # define headers
        self.important_headers = important_headers
        self.lookback = lookback # 10 is good
        self.epochs = epochs
        self.units = units # 65 is good
        self.batch_size = batch_size # 2 is good
        #self.rcParams['figure.figsize'] = 20,10
        self.scaler = MinMaxScaler(feature_range=(0, 1))

    def loadCSV(self, filename):
        #read the file
        df = pd.read_csv(filename)
        #setting index as date
        df['date'] = pd.to_datetime(df[self.important_headers['timestamp']],unit='s') # UNITS IS IMPORTANT
        df.index = df.date
        #plot
        return df

    def createFrame(self):
        df = self.loadCSV(self.csvset)
        df = df.iloc[(len(df.index)-self.cutpoint):]
        return df

    def plotSave(self, series, xlabel, ylabel, title, legend, filename): # series must be an array
        plt.clf()
        plt.figure(figsize=(16,8))
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        textstr = 'Size =',self.cutpoint,'\nLookback =',self.lookback,'\nEpochs =',self.epochs,'\nUnits =',self.units
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.text(0.05, 0.95, textstr, fontsize=12,verticalalignment='top', bbox=props)
        for line in series:    
            plt.plot(line)
        plt.legend(legend, loc=4)
        plt.savefig('chart/'+filename)
        print('Saved plot '+title)

    def saveModel(self, model, filename):
        # serialize model to JSON
        model_json = model.to_json()
        with open(self.models_path+filename+'.json', 'w') as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        model.save_weights(self.models_path+filename+'.h5')
        print('Saved model to disk')

    def loadModel(self, filename):
        # load json and create model
        json_file = open(self.models_path+filename+'.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)
        # load weights into new model
        loaded_model.load_weights(self.models_path+filename+'.h5')
        print('Loaded model from disk')
        return loaded_model

    def trainModelForTest(self, df, midpoint, lookback, epochs, units, batch_size):
        #creating dataframe
        data = df.sort_index(ascending=True, axis=0)
        new_data = pd.DataFrame(index=range(0,len(df)),columns=['date', 'close'])
        for i in range(0,len(data)):
            #new_data['date'][i] = data['date'][i] #convert from unix to date here
            new_data['date'][i] = data['date'][i]
            new_data['close'][i] = data[self.important_headers['price']][i]

        #setting index
        new_data.index = new_data.date
        new_data.drop('date', axis=1, inplace=True)
        #creating train and test sets
        dataset = new_data.values

        train = dataset[0:midpoint,:] # will be changed to the whole dataset

        #converting dataset into x_train and y_train
        scaled_data = self.scaler.fit_transform(dataset)

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
    
    def trainModel(self, df, lookback, epochs, units, batch_size):
        #creating dataframe
        data = df.sort_index(ascending=True, axis=0)
        new_data = pd.DataFrame(index=range(0,len(df)),columns=['date', 'close'])
        for i in range(0,len(data)):
            #new_data['date'][i] = data['date'][i] #convert from unix to date here
            new_data['date'][i] = data['date'][i]
            new_data['close'][i] = data[self.important_headers['price']][i]
        #setting index
        new_data.index = new_data.date
        new_data.drop('date', axis=1, inplace=True)
        #creating train and test sets
        dataset = new_data.values
        #converting dataset into x_train and y_train
        scaled_data = self.scaler.fit_transform(dataset)

        x_train, y_train = [], []
        for i in range(lookback,len(dataset)):
            x_train.append(scaled_data[i-lookback:i,0])
            y_train.append(scaled_data[i,0])

        x_train, y_train = np.array(x_train), np.array(y_train) # convert to numpy array
        x_train = np.reshape(x_train, (x_train.shape[0],x_train.shape[1],1))

        # create and fit the LSTM network
        model = Sequential()
        model.add(LSTM(units=units, return_sequences=True, input_shape=(x_train.shape[1],1))) #units=hidden state length
        model.add(LSTM(units=units))
        model.add(Dense(1))

        model.compile(loss='mean_squared_error', optimizer='adam')
        model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size, verbose=2)
        return model, new_data

    def retrainModel(self, data):
        df = self.loadCSV(data) # maybe not?
        df = df.iloc[(len(df.index)-self.cutpoint):]

        #self.plotSave([df[self.important_headers['price']]], 'Date', 'Bitcoin Price (USD)', 'Price History', ['Prices'], 'hourly_prices.png') 

        print('lookback =',self.lookback,'\nepochs =',self.epochs,'\nunits =',self.units,'\nbatch_size =',self.batch_size)

        model, new_data = self.trainModel(df, self.lookback, self.epochs, self.units, self.batch_size)
        return model, new_data

    def predictNextTest(self, inputs, model):
        X_test = []
        for i in range(self.lookback,inputs.shape[0]):
            X_test.append(inputs[i-self.lookback:i,0])
        X_test = np.array(X_test)
        X_test = np.reshape(X_test, (X_test.shape[0],X_test.shape[1],1))
        closing_price = model.predict(X_test) #~!!!
        closing_price = self.scaler.inverse_transform(closing_price)
        #rms=np.sqrt(np.mean(np.power((self.new_data.values[self.midpoint:,:]-closing_price),2)))
        #print('RMS:',rms)
        return closing_price

    def predictNextValue(self, inputs, model): #withOUT validation*
        # inputs should be current value and value before
        X_test = []
        for i in range(self.lookback,inputs.shape[0]):
            X_test.append(inputs[i-self.lookback:i,0])
        X_test = np.array(X_test)
        X_test = np.reshape(X_test, (X_test.shape[0],X_test.shape[1],1))
        closing_price = model.predict(X_test) #~!!!
        closing_price = self.scaler.inverse_transform(closing_price)
        return closing_price

    def conformInputs(self, inputs):
        inputs = inputs.reshape(-1,1)
        inputs = self.scaler.transform(inputs)
        return inputs

    def decideAction(self, pair): # bring it all together here
        # pair is derivative pair [n-1, n]
        # compare current slope to last n slopes
        # with that info decide to buy or sell - buy if bottoming, sell if peaking
        alpha = 0 # play with
        if pair[0] < alpha and pair[1] > alpha:
            return 'buy'
        elif pair[0] > alpha and pair[1] < alpha:
            return 'sell'
        else:
            return 'hold'

    def getGradient(self, nextdf):
        return pd.Series(np.gradient(nextdf.values), nextdf.index, name='slope')

    def getSlope(self, pair):
        constant = 10
        return (pair[1]-pair[0])/constant

    def calcError(self, actual_slope, pred_slope):    
        tally = 0
        for i in range(0,actual_slope.size):
            #print(actual_slope[i],' ',pred_slope[i])
            if (actual_slope[i]<0 and pred_slope[i]> 0) or (actual_slope[i]>0 and pred_slope[i]< 0):
                tally+=1
        perc_correct = (1-(tally/actual_slope.size))*100

        print('Derivative correct {:.1f}%'.format(perc_correct))
        return perc_correct

    ### run code
    def testRealTime(self):
        '''
        - get current(next) value and last value from csv file
        - get current(next) derivative and last derivative
        - load model
        - predict next value
        - retrain every 15 mins
        '''
        df = self.createFrame()
        lastv = df[self.important_headers['price']][len(df.index)-2]
        currentv = df[self.important_headers['price']][len(df.index)-1]

        latest_model, frame = self.retrainModel(self.csvset)

        inputs = self.conformInputs(np.array([lastv, currentv]))
        nextv = self.predictNextValue(inputs,latest_model)[0][0]
        raw_vals_list = np.array([lastv, currentv, nextv])

        print('------\nn-1:',raw_vals_list[0],'(actual)\nn:',raw_vals_list[1],'(actual)\nn+1:',raw_vals_list[2], '(predicted)')
        #get derivatives
        prev = self.getSlope(raw_vals_list[0:2])
        forw = self.getSlope(raw_vals_list[1:])
        print('\nactual (previous) d/dx: {:.2f}\npredicted (next) d/dx: {:.2f}'.format(prev,forw))
        print('\npredicted action:',self.decideAction([prev, forw]),'\n------')

    def testModel(self): # move this to crptotrader class and move the logic there too possibly
        df = self.createFrame()

        self.plotSave([df[self.important_headers['price']]], 'Date', 'Bitcoin Price (USD)', 'Price History', ['Prices'], 'hourly_prices.png') 

        self.midpoint = int(len(df.index)*(3/4)) # have to set after df init

        print('midpoint =',self.midpoint,'\nlookback =',self.lookback,'\nepochs =',self.epochs,'\nunits =',self.units,'\nbatch_size =',self.batch_size)

        model, new_data = self.trainModelForTest(df, self.midpoint, self.lookback, self.epochs, self.units, self.batch_size)
        self.saveModel(model,(str(datetime.datetime.now()))+'-model')

        #predicting values, using past lookback from the train data

        # REPLACE?APPEND? THE 10 MOST RECENT VALUES TO THIS
        inputs = new_data[len(new_data) - len(new_data.values[self.midpoint:,:]) - self.lookback:].values # last section of test data

        inputs = self.conformInputs(inputs)
        next_price = self.predictNextTest(inputs, model) # note that this has validation built in

        predictions = pd.DataFrame()
        predictions['date'] = new_data[self.midpoint:].index
        predictions.index = predictions['date']
        predictions.drop('date', axis=1, inplace=True) # drop duplicate column
        predictions['price'] = next_price

        predictions['slope'] = self.getGradient(predictions.price)
        actual_slope = self.getGradient(new_data[self.midpoint:].close)

        #print(predictions.slope[0],actual_slope[0])

        r = self.calcError(predictions.slope, actual_slope)
        difference = (predictions.slope - actual_slope)/actual_slope # how far off

        # save graphs
        self.plotSave([new_data.close,predictions.price], 'Date', 'Bitcoin Price (USD)', 'Bitcoin Price History + Predictions', ['Actual', 'Predicted'], 'predictions.png') 
        self.plotSave([new_data[self.midpoint:].close, predictions.price], 'Date', 'Bitcoin Price (USD)', 'Bitcoin Price History + Predictions (zoomed)', ['Actual', 'Predicted'], 'predictions_zoomed.png') 
        self.plotSave([actual_slope, predictions.slope], 'Date', 'Change in Bitcoin Price (USD)', 'Change in Bitcoin Price History + Predictions (zoomed)', ['Actual', 'Predicted'], 'slope.png') 
        self.plotSave([difference], 'Date', 'Percent Change in Bitcoin Price (USD)', 'Error Change in Bitcoin Price History + Predictions (zoomed)', ['Error'], 'error.png') 
        print(predictions)