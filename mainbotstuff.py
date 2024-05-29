import time
import os
import requests
from tvDatafeed import TvDatafeed, Interval
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import pytz

# Load environment variables from .env file
load_dotenv('mem.env')

# Initialize the TvDatafeed object
tv = TvDatafeed()

# Fetch the Discord webhook URL from environment variables
discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')

if not discord_webhook_url:
    raise ValueError("Discord webhook URL is not set. Please set the DISCORD_WEBHOOK_URL environment variable.")

# List of symbols
symbols = [
"NASDAQ:AAPL", "NASDAQ:MSFT", "NASDAQ:GOOGL", "NASDAQ:GOOG", "NASDAQ:AMZN", "NASDAQ:FB", "NASDAQ:TSLA", "NASDAQ:NVDA", "NASDAQ:PYPL", "NASDAQ:ADBE", 
"NASDAQ:INTC", "NASDAQ:CMCSA", "NASDAQ:PEP", "NASDAQ:CSCO", "NASDAQ:AVGO", "NASDAQ:COST", "NASDAQ:TMUS", "NASDAQ:QCOM", "NASDAQ:TXN", "NASDAQ:CHTR", 
"NASDAQ:AMGN", "NASDAQ:SBUX", "NASDAQ:ISRG", "NASDAQ:AMD", "NASDAQ:BKNG", "NASDAQ:INTU", "NASDAQ:MDLZ", "NASDAQ:MU", "NASDAQ:ADP", "NASDAQ:LRCX", 
"NASDAQ:CSX", "NASDAQ:GILD", "NASDAQ:VRTX", "NASDAQ:KHC", "NASDAQ:FISV", "NASDAQ:MELI", "NASDAQ:ILMN", "NASDAQ:ATVI", "NASDAQ:MRNA", "NASDAQ:MNST", 
"NASDAQ:AMAT", "NASDAQ:JD", "NASDAQ:ZM", "NASDAQ:EBAY", "NASDAQ:ADSK", "NASDAQ:BIIB", "NASDAQ:ASML", "NASDAQ:DOCU", "NASDAQ:WDAY", "NASDAQ:SNPS", 
"NASDAQ:ADI", "NASDAQ:XLNX", "NASDAQ:DXCM", "NASDAQ:SGEN", "NASDAQ:OKTA", "NASDAQ:REGN", "NASDAQ:EA", "NASDAQ:ROST", "NASDAQ:CTAS", "NASDAQ:MTCH", 
"NASDAQ:KDP", "NASDAQ:IDXX", "NASDAQ:TEAM", "NASDAQ:PCAR", "NASDAQ:WBA", "NASDAQ:MAR", "NASDAQ:VRSN", "NASDAQ:EXC", "NASDAQ:EXPE", "NASDAQ:CPRT", 
"NASDAQ:SIRI", "NASDAQ:ANSS", "NASDAQ:FAST", "NASDAQ:WDC", "NASDAQ:TTWO", "NASDAQ:PAYX", "NASDAQ:SWKS", "NASDAQ:SPLK", "NASDAQ:NTES", "NASDAQ:CDNS", 
"NASDAQ:KLAC", "NASDAQ:CTSH", "NASDAQ:VRSK", "NASDAQ:INCY", "NASDAQ:ALXN", "NASDAQ:TCOM", "NASDAQ:HAS", "NASDAQ:LULU", "NASDAQ:ULTA", "NASDAQ:NTAP", 
"NASDAQ:CDW", "NASDAQ:ALGN", "NASDAQ:ORLY", "NASDAQ:CTXS", "NASDAQ:DLTR", "NASDAQ:CHKP", "NASDAQFOX", "NASDAQ:FOXA", "NASDAQ:MSCI", "NASDAQ:FTNT", 
"NASDAQ:MXIM", "NASDAQ:AKAM", "NASDAQ:MCHP", "NASDAQ:BIIB", "NASDAQ:ILMN", "NASDAQ:ADI", "NASDAQ:LBTYK", "NASDAQ:QRVO", "NASDAQ:JBHT", "NASDAQ:SGEN", 
"NASDAQ:CDK", "NASDAQ:NXPI", "NASDAQ:CSGP", "NASDAQ:VRSN", "NASDAQ:CERN", "NASDAQ:VRTX", "NASDAQ:ISRG", "NASDAQ:NTES", "NASDAQ:TTWO", "NASDAQ:TCOM", 
"NASDAQ:JD", "NASDAQ:ADBE", "NASDAQ:ADSK", "NASDAQ:ADP", "NASDAQ:ALXN", "NASDAQ:ALGN", "NASDAQ:ALNY", "NASDAQ:AMD", "NASDAQ:AMGN", "NASDAQ:AMZN", 
"NASDAQ:ANSS", "NASDAQ:ASML", "NASDAQ:ATVI", "NASDAQ:AVGO", "NASDAQ:AXON", "NASDAQ:BIIB", "NASDAQ:BKNG", "NASDAQ:CDNS", "NASDAQ:CERN", "NASDAQ:CHKP", 
"NASDAQ:CMCSA", "NASDAQ:CMG", "NASDAQ:COST", "NASDAQ:CPRT", "NASDAQ:CSCO", "NASDAQ:CSGP", "NASDAQ:CSX", "NASDAQ:CTAS", "NASDAQ:CTSH", "NASDAQ:CTXS", 
"NASDAQ:DLTR", "NASDAQ:DXCM", "NASDAQ:EA", "NASDAQ:EBAY", "NASDAQ:EXC", "NASDAQ:EXPE", "NASDAQ:FAST", "NASDAQ:FB", "NASDAQ:FISV", "NASDAQ:FOX", 
"NASDAQ:FOXA", "NASDAQ:FTNT", "NASDAQ:GILD", "NASDAQ:GOOG", "NASDAQ:GOOGL", "NASDAQ:HAS", "NASDAQ:HSIC", "NASDAQ:IDXX", "NASDAQ:ILMN", "NASDAQ:INCY", 
"NASDAQ:INTC", "NASDAQ:INTU", "NASDAQ:ISRG", "NASDAQ:JD", "NASDAQ:KLAC", "NASDAQ:KHC", "NASDAQ:LBTYA", "NASDAQ:LBTYK", "NASDAQ:LRCX", "NASDAQ:LULU", 
"NASDAQ:MAR", "NASDAQ:MDLZ", "NASDAQ:MELI", "NASDAQ:MCHP", "NASDAQ:MNST", "NASDAQ:MRNA", "NASDAQ:MSFT", "NASDAQ:MSCI", "NASDAQ:MU", "NASDAQ:MXIM", 
"NASDAQ:NFLX", "NASDAQ:NTAP", "NASDAQ:NTES", "NASDAQ:NVDA", "NASDAQ:NXPI", "NASDAQ:OKTA", "NASDAQ:ORLY", "NASDAQ:PAYX", "NASDAQ:PCAR", "NASDAQ:PEP", 
"NASDAQ:PYPL", "NASDAQ:QCOM", "NASDAQ:QRVO", "NASDAQ:REGN", "NASDAQ:ROST", "NASDAQ:SBAC", "NASDAQ:SBUX", "NASDAQ:SGEN", "NASDAQ:SIRI", "NASDAQ:SNPS", 
"NASDAQ:SPLK", "NASDAQ:SWKS", "NASDAQ:TCOM", "NASDAQ:TEAM", "NASDAQ:TMUS", "NASDAQ:TSLA", "NASDAQ:TXN", "NASDAQ:ULTA", "NASDAQ:VRSK", "NASDAQ:VRSN", 
"NASDAQ:WBA", "NASDAQ:WDAY", "NASDAQ:WDC", "NASDAQ:XLNX", "NASDAQ:ZM", "NASDAQ:ZG", "NASDAQ:Z", "NASDAQ:ALXN", "NASDAQ:ADP", "NASDAQ:ADSK", 
"NASDAQ:ASML", "NASDAQ:ADBE", "NASDAQ:AMD", "NASDAQ:BIIB", "NASDAQ:BKNG", "NASDAQ:CSCO", "NASDAQ:COST", "NASDAQ:CHTR", "NASDAQ:CMCSA", "NASDAQ:CME", 
"NASDAQ:DLTR", "NASDAQ:EBAY", "NASDAQ:EA", "NASDAQ:EXC", "NASDAQ:FAST", "NASDAQ:FB", "NASDAQ:FISV", "NASDAQ:GILD", "NASDAQ:HAS", "NASDAQ:INTC", 
"NASDAQ:INTU", "NASDAQ:JD", "NASDAQ:KLAC", "NASDAQ:LBTYA", "NASDAQ:LBTYK", "NASDAQ:LULU", "NASDAQ:MDLZ", "NASDAQ:MELI", "NASDAQ:MCHP", "NASDAQ:MSFT", 
"NASDAQ:MNST", "NASDAQ:NTES", "NASDAQ:NFLX", "NASDAQ:NVDA", "NASDAQ:NXPI", "NASDAQ:ORLY", "NASDAQ:PAYX", "NASDAQ:PCAR", "NASDAQ:PEP", "NASDAQ:PYPL", 
"NASDAQ:QCOM", "NASDAQ:ROST", "NASDAQ:REGN", "NASDAQ:SBUX", "NASDAQ:SNPS", "NASDAQ:SGEN", "NASDAQ:SPLK", "NASDAQ:SWKS"
]

def send_discord_message(message):
    data = {
        "content": message
    }
    response = requests.post(discord_webhook_url, json=data)
    if response.status_code != 204:
        print(f"Failed to send message to Discord: {response.status_code}, {response.text}")

# Fetch historical data and process it
def fetch_and_process_data(tv, symbol, exchange, interval):
    try:
        # Fetch historical data
        data = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=500)
        if data is None or 'close' not in data.columns:
            raise ValueError(f"Invalid data fetched for {symbol}")

        # Calculate the EMAs for MACD and 200 EMA
        short_window = 12
        long_window = 26
        signal_window = 9

        # Calculate short-term EMA (12 periods)
        data['EMA_short'] = data['close'].ewm(span=short_window, adjust=False).mean()

        # Calculate long-term EMA (26 periods)
        data['EMA_long'] = data['close'].ewm(span=long_window, adjust=False).mean()

        # Calculate MACD line
        data['MACD'] = data['EMA_short'] - data['EMA_long']

        # Calculate Signal line (9-period EMA of MACD)
        data['Signal'] = data['MACD'].ewm(span=signal_window, adjust=False).mean()

        # Calculate the 200-period EMA
        data['EMA_200'] = data['close'].ewm(span=200, adjust=False).mean()

        # Check for signal conditions in the last candle
        m = data['close'].tail(1), ' ' , symbol
        print(m)
        for i in range(-3,0):
            if (data['MACD'].iloc[i-1] < 0) and (data['MACD'].iloc[i-2] < data['Signal'].iloc[i-2]) and \
            (data['MACD'].iloc[i-1] > data['Signal'].iloc[i-1]) and (data['close'].iloc[i-1] >= data['EMA_200'].iloc[i-1]):
                message = f"YES, {symbol} {data['close'][i-1]}."
                print(message)
                send_discord_message(message)

    except Exception as e:
        print(f"Error processing data for {symbol}: {e}")
        raise  # Re-raise the exception to trigger retry logic

def main():
    exchange = 'NASDAQ'
    interval = Interval.in_1_hour

    # Define the timezone for GMT (UTC)
    tz = pytz.timezone('Etc/GMT')
    start_time = time.time()
    
    while True:
        for symbol in symbols:
            retries = 2
            for attempt in range(retries):
                try:
                    fetch_and_process_data(tv, symbol, exchange, interval)
                    break  # Exit retry loop if successful
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed for {symbol}. Retrying in {3 * (attempt + 1)} seconds...")
                    time.sleep(3 * (attempt + 1))
                    if attempt == retries - 1:
                        print(f"Failed to fetch data for {symbol} after {retries} attempts. Skipping...")

        end_time = time.time()  # Record the current time after each iteration
        execution_time = end_time - start_time  # Calculate the time difference
        print(f"Iteration completed. Execution time: {execution_time} seconds")
        if execution_time < 3600:
            time.sleep(3600 - execution_time)
        start_time = time.time()

if __name__ == "__main__":
    main()
