import os
import pandas as pd
import yfinance as yf
import parseFundData
from datetime import datetime, timedelta
import numpy as np

#fundstatspath = "intraQuarter/_KeyStats"

# should be from the start of fundamental data, to the time delta after that from parseFundData.py
# for comparing and predicting percent change over a given period of time
# start_date = "2022-01-01"
# end_date = "2022-12-31"

def get_sp500_data(start_date, end_date):
    """
    Creates the dataset containing S&P500 prices
    :returns: sp500_index.csv
    """
    index_data = yf.download("SPY", start=start_date, end=end_date)
    index_data.to_csv("sp500_index.csv")

def get_stock_data(stock_symbol, start_date, end_date):

    # Fetch the stock data using yfinance
    stock_data = yf.download(stock_symbol, start=start_date, end=end_date)

    # Save the stock data to a CSV file
    csv_filename = f"{stock_symbol}_stock_data.csv"
    stock_data.to_csv(csv_filename)

def get_stock_test_data(stock_symbol, start_date_timestamp, num_trading_days):
    # get test data, num_trading_days should be window_size + predict_days (NOTE: business days)
    # start test date timestamp should be one day after train data end date (no overlap)

    # Initialize variables: timestamp object and trading days
    end_date = start_date_timestamp
    trading_days_count = 0

    # Fetch stock data for the specified number of trading days
    while trading_days_count < num_trading_days:
        end_date += timedelta(days=1)
        if end_date.weekday() < 5:  # Check if it's a trading day (Monday to Friday)
            trading_days_count += 1

    print(f'Total days: {trading_days_count}')

    # Convert the updated datetime object back to a timestamp string
    test_start_timestamp_str = start_date_timestamp.strftime("%Y-%m-%d")
    test_end_timestamp_str = end_date.strftime("%Y-%m-%d")
    print(f'Test Start date: {test_start_timestamp_str}')
    print(f'Test End date: {test_end_timestamp_str}')

    # Fetch the stock data using yfinance
    stock_data = yf.download(stock_symbol, start=test_start_timestamp_str, end=test_end_timestamp_str)

    # Save the test stock data to a CSV file
    csv_filename = f"Test_{stock_symbol}_stock_data.csv"
    stock_data.to_csv(csv_filename)

def predict_stock_price(stock_symbol, input_date, window_size):
    # Check if the input date is a valid date format
    try:
        input_date = pd.to_datetime(input_date)
    except ValueError:
        print("Invalid Date Format. Please enter date in YYYY-MM-DD format.")
        return

    trading_days = window_size + 30
    # Fetch data from yfinance
    end_date = input_date
    start_date = input_date - timedelta(days=trading_days)  # Fetch more days to ensure we enough trading days, ex. at least 60
    data = yf.download(stock_symbol, start=start_date, end=end_date)

    if len(data) < window_size:
        print("Not enough historical data to make a prediction. Try an earlier date.")
        return

    return data

def get_market_variables(start, end):
    # Define the tickers for the market variables
    tickers = ["^GSPC", "^IRX", "^FVX", "^DXY", "^CRX", "^VIX"]

    # Retrieve the daily data for the specified time period
    start_date = "2023-01-01"
    end_date = "2023-06-30"
    data = yf.download(tickers, start=start_date, end=end_date)

    # Extract the relevant features for each day
    daily_features = []
    for i in range(len(data.index)):
        day_features = [
            data.loc[data.index[i], "^GSPC_Open"],
            data.loc[data.index[i], "^GSPC_High"],
            data.loc[data.index[i], "^GSPC_Low"],
            data.loc[data.index[i], "^GSPC_Close"],
            data.loc[data.index[i], "^GSPC_Volume"],
            data.loc[data.index[i], "^IRX_yield"], #US Treasury Bond Yields (2-Year)
            #data.loc[data.index[i], "^TNX_yield"], #US Treasury Bond Yields (10-Year)
            data.loc[data.index[i], "^FVX_yield"], #US Treasury Bond Yields (10-Year)
            data.loc[data.index[i], "^DXY_regularMarketPrice"], # Dollar Index
            data.loc[data.index[i], "^CRX_regularMarketPrice"], # Commodity Index
            data.loc[data.index[i], "^VIX_regularMarketPrice"] # Volatility Index
        ]
        daily_features.append(day_features)

    # Convert the list of daily features to a numpy tensor
    daily_features_tensor = np.array(daily_features)

    return daily_features_tensor


def get_stock_data_old(date_start, date_end):
    fundstatspath = "intraQuarter/_KeyStats/"
    ticker_list = os.listdir(fundstatspath)
    ticker_dir_list = [x[0] for x in os.walk(fundstatspath)]
    #ticker_list = [x[1] for x in os.walk(fundstatspath)]
    #print(ticker_dir_list)
    print(ticker_list)

    # Required on Mac
    if ".DS_Store" in ticker_list:
        ticker_list.remove(".DS_Store")

    
    ## Get all Adjusted Close prices for all the tickers in our list,
    ## at once - this may be very slow
    all_data = yf.download(ticker_list, start=date_start, end=date_end)
    stock_data = all_data["Adj Close"]

    #tickerlist[idx_start:idx_end]

    stock_data_df = pd.DataFrame()

    counter = 0
    for ticker in ticker_list:
        print(ticker)
        ticker = ticker.upper()

        stock = yf.download(ticker, start=date_start, end=date_end)
        if stock.empty:
            print(f"No data for {ticker}")
            continue
        # only get Adj Close price data column from data frame
        adj_close = stock["Adj Close"].rename(ticker)
        stock_data_df = pd.concat([stock_data_df, adj_close], axis=1)

    ## Remove any columns that hold no data, and print their tickers
    #stock_data_df.dropna(how="all", axis=1, inplace=True)
    #missing_tickers = [ticker for ticker in ticker_list if ticker.upper() not in stock_data_df.columns]
    #print(f"{len(missing_tickers)} tickers are missing: \n {missing_tickers} ")
    ## If there are only some missing datapoints, forward fill
    #stock_data_df.ffill(inplace=True)

    stock_data_df.to_csv("stock_prices.csv")


if __name__ == "__main__":
    get_stock_data()    
    #get_sp500_data()