import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def create_sequential_data(data, timesteps=60, futuredays=0):
    # futuredays is if we want to predict multiple future days (default is predict one day) after our sliding window
    # timesteps is our sliding window size that we need regardless for the training data - cannot be 1
    X = []
    y = []

    # y will be used to predict the next day price - ex. it is the 61st day, when X is 1 to 60 
    for i in range(len(data) - timesteps - futuredays):
        X.append(data[i:(i + timesteps), 0])
        y.append(data[i + timesteps, 0]) if futuredays == 0 else y.append(data[i + timesteps:i + timesteps + futuredays, 0]) # next futuredays days after each sliding window

    return np.array(X), np.array(y)

# Old function
def create_lstm_data_old(trainData, window_size, future_days=0, predict_multipledays=False):
    X_train = []
    y_train = []

    # y will be used to predict the next day price - ex. it is the 61st day, when X is 1 to 60 
    if (predict_multipledays):
        for i in range(len(trainData) - window_size - future_days + 1):
            window = trainData[i:i + window_size]
            target = trainData[i + window_size:i + window_size + future_days]
            X_train.append(window)
            y_train.append(target) # next 10 days after each sliding window
    ## Predict one day
    else:
        # 60 timestep sequences of length 60 that keep shifting by one day forward
        for i in range(window_size, trainData.shape[0]):
            X_train.append(trainData[i-window_size:i,0]) # up to i, non-inclusive (ex. won't have element at index 60)
            y_train.append(trainData[i,0]) # has element at index 60

    return X_train, y_train

def get_test_data(stock_symbol):
    # get test data

    testData = pd.read_csv(f"Test_{stock_symbol}_stock_data.csv")
    actual_stock_price = testData['Close'].values # or .iloc[:,1:2], actual close stock prices for test data
    inputs = actual_stock_price.reshape(-1, 1) # reshape data into a column vector (second dimension is 1)

    # Rescale data to be between 0 and 1 for better perfomance/normalization
    sc = MinMaxScaler(feature_range=(0,1))

    test_data = sc.fit_transform(inputs)

    # X_test = []

    # # 60 timestep sequences of length 60 that keep shifting by one day forward
    # # for i in range(window_size, test_data.shape[0]): # range(60, 81)
    # #     X_test.append(test_data[i-window_size:i, 0]) # up to i, non-inclusive (ex. won't have element at index 60)
    # X_test.append(test_data[0:60, 0])

    # X_test = np.array(X_test)

    # # Add batch size axis for input into LSTM
    # X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1)) # Last 1 indicates have one feature (the price) in each timestep
    
    return actual_stock_price, test_data