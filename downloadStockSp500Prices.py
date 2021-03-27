import os
from pandas_datareader import data as pdr
import pandas as pd
import yfinance as yf
import parseFundData

yf.pdr_override()

fundstatspath = "intraQuarter/_KeyStats"

# should be from the start of fundamental data, to the time delta after that from parseFundData.py
# for comparing and predicting percent change over a given period of time
start_date = "2003-08-01"
end_date = "2015-01-01"

def get_sp500_data(start=start_date, end=end_date):
    """
    Creates the dataset containing S&P500 prices
    :returns: sp500_index.csv
    """
    index_data = pdr.get_data_yahoo("SPY", start=START_DATE, end=END_DATE)
    index_data.to_csv("sp500_index.csv")


def get_stock_data(date_start=start_date, date_end=end_date):
    #fundstatspath = "intraQuarter/_KeyStats/"
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
    #all_data = pdr.get_data_yahoo(ticker_list, start, end)
    #stock_data = all_data["Adj Close"]

    #tickerlist[idx_start:idx_end]

    stock_data_df = pd.DataFrame()

    counter = 0
    for ticker in ticker_list:
        print(ticker)
        ticker = ticker.upper()

        stock = pdr.get_data_yahoo(ticker, start=date_start, end=date_end)
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
    get_sp500_data()