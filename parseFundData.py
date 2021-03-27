import pandas as pd
import os
import time
from datetime import datetime

#fundstatspath = "intraQuarter/_KeyStats/"
global fundstatspath
fundstatspath = "intraQuarter/_KeyStats"
#fundstatspath = "/Users/justinhess/Python/Python for Finance/intraQuarter"
unix_time_delta = 1
num_days = 1

# our S&P 500 price data end date
sp500_end_date = ""

def initialize_date_range():
    # get number of days (from 1 to 365) to set baseline time
    # for calculating stock and s&p price change
    num_days = 365
    unix_time_delta = num_days * 86400 # this will be added to unix time for each stock time stamp from html files

def preprocess_price_data():
    # our historial S&P500 data from 2003-2014 (one year after end of fundamental data)
    #sp500_df = pd.read_csv("sp500_index.csv")
    sp500_df = pd.read_csv("sp500_index.csv", index_col="Date", parse_dates=True)

    # get start and end dates for S&P 500 price data
    start_date = str(sp500_df.index[0])
    end_date = str(sp500_df.index[-1])
    # get rid of "00:00:00" if its in date, only keep date, not time
    if ("00:00:00" in end_date) & ("00:00:00" in start_date):
        dateformat = '%Y-%m-%d %H:%M:%S'
        start_date = str(datetime.strptime(start_date, dateformat).date())
        end_date = str(datetime.strptime(end_date, dateformat).date())

    # end s&p500 datetime string
    global sp500_end_date
    sp500_end_date = end_date # get rid of H:M:S in datetime string

    dateformat = '%Y-%m-%d'
    tdelta = datetime.strptime(end_date, dateformat) - datetime.strptime(start_date, dateformat)
    tdelta_days = tdelta.days
    print(f"Time Range from S&P500 csv data is {tdelta_days} days")

    # reindex to include the weekends
    idx = pd.date_range(start_date, end_date)
    sp500_df = sp500_df.reindex(idx)
    #print(sp500_df)
    #stock_raw_data = stock_raw_data.reindex(idx)

    # Now the weekends are NaN, so we fill forward these NaNs
    # (i.e weekends take the value of Friday's adjusted close).
    sp500_df.ffill(inplace=True)
    #stock_raw_data.ffill(inplace=True)

    #sp500_df.set_index('Date', inplace=True)


    return sp500_df

def process_fundamentals(sp500_df, gather="Total Debt/Equity (mrq)"):
    # get the directory path for each ticker in fundstatspath
    stock_dir_list = [x[0] for x in os.walk(fundstatspath)]

    df = pd.DataFrame(columns = ['Date','Unix','Ticker','DE Ratio'])

    # for each ticker directory path
    for each_dir in stock_dir_list[1:]:
        # get list of html filenames in current ticker directory
        htmlfiles = os.listdir(each_dir)

        # Get rid of the .DS_Store file in Mac
        if ".DS_Store" in htmlfiles:
            htmlfiles.remove(".DS_Store")

        #print(each_dir)

        #ticker = each_dir.split("\\")[2] # Windows!!!
        ticker = each_dir.split("/")[2] # Mac

        # skip ticker folder if no html files
        if (len(htmlfiles) == 0):
            print(f"No data files for ticker {ticker}")
            continue

        # make sure our time delta for calculating percentage change is not greater than the 
        # time delta between the end of fundamental data and our available S&P500 data
        last_file = htmlfiles[-1]
        # get fundamental end date datetime object from html filename
        fund_end_date_dtobject = datetime.strptime(last_file, '%Y%m%d%H%M%S.html')
        #print(fund_end_date_dtobject)
        # get rid of H:M:S from fundamental datetime object
        dateformat = '%Y-%m-%d %H:%M:%S'
        # fundamental end date string without H:M:S
        fund_end_date = str(fund_end_date_dtobject.date())
        #print(fund_end_date)
        dateformat = '%Y-%m-%d'
        # subtract datetime objects to get time delta datetime object
        tdelta = datetime.strptime(sp500_end_date, dateformat) - datetime.strptime(fund_end_date, dateformat)
        tdelta_days = tdelta.days

        # desired predicted time range from fundamental data eclipses our available S&P500 data 
        if (num_days > tdelta_days):
            print(f"ERROR for ticker {ticker}: Pick a smaller time range to compare stock and S&P500 percentage change")
            #print(fund_end_date)
            #print(sp500_end_date)
            continue

        for file in htmlfiles:
            # convert the datetime of our file name to unix time
            html_date_stamp = datetime.strptime(file, '%Y%m%d%H%M%S.html')
            html_unix_time = time.mktime(html_date_stamp.timetuple())

            # get the full html file path string
            full_file_path = each_dir + '/' + file

            source = open(full_file_path,'r').read()

            ## do loop for below for all features ##

            variable = gather

            try: 
                value = float(source.split(variable+':</td><td class="yfnc_tabledata1">')[1].split('</td>')[0])
                print(value)
            except AttributeError:
                # In the past, 'Avg Vol' was instead named 'Average Volume'
                # If 'Avg Vol' fails, search for 'Average Volume'.
                if variable == "Avg Vol (3 month)":
                    try:
                        subvariable = "Average Volume (3 month)"
                        value = float(source.split(subvariable+':</td><td class="yfnc_tabledata1">')[1].split('</td>')[0])
                        print("Average", value)
                    except AttributeError:
                        pass
                else:
                    print('Crap')
                    pass
            except Exception as e:
                #print("Exception", value, e, ticker, file)
                # if list index out of range exception, there's a newline
                try:
                    value = float(source.split(variable+':</td>\n<td class="yfnc_tabledata1">')[1].split('</td>')[0])
                # if could not convert string to float: 'N/A' exception, it's a "N/A"
                except Exception as e:
                    #print("Exception", value, e, ticker, file)
                    value = "N/A"
                    # some values will be 'N/A' or 'Nan', can't convert to float
                    # in this case, just return value as 'N/A' instead of a float
                    pass          

            # current date from the current html keystats file
            current_date = datetime.fromtimestamp(html_unix_time).strftime('%Y-%m-%d')
            # end date = current date + time delta
            end_date = datetime.fromtimestamp(html_unix_time + unix_time_delta).strftime("%Y-%m-%d")
            
            #row = sp500_df[(sp500_df.index == current_date)]
            #print(row)
            #sp500_value = float(row["Adjusted Close"])
            #sp500_price = float(row["Adj Close"])
            #print(float(sp500_df.iloc['2003-11-26', "Adj Close"]))
            # SP500 prices now and one year later, and the percentage change
            #sp500_df.set_index('Date', inplace=True)
            #print(sp500_df)
            sp500_price = float(sp500_df.loc[current_date, "Adj Close"])
            #print(sp500_price)
            end_sp500_price = float(sp500_df.loc[end_date, "Adj Close"])
            sp500_p_change = ((end_sp500_price - sp500_price) / sp500_price * 100)

            try:
                #stock_price = float(stock_df.loc[current_date, ticker.upper()])
                #end_stock_price = float(stock_df.loc[end_date, ticker.upper()])
                r = 1+1
            except KeyError:
                # If stock data is missing, we must skip this datapoint
                # print(f"PRICE RETRIEVAL ERROR for {ticker}")
                continue

            #stock_p_change = ((end_stock_price - stock_price) / stock_price * 100)
            


    save = variable.replace(' ','').replace(')','').replace('(','').replace('/','')+('.csv')
    print(save)
    df.to_csv(save)


if __name__ == "__main__":
    initialize_date_range()
    sp500_df = preprocess_price_data()
    process_fundamentals(sp500_df)