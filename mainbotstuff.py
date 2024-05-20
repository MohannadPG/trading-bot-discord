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
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "TSLA", "PEP", "AVGO", "CSCO", "ADBE", "CMCSA", "ORCL",
    "VRTX", "INTC", "TXN", "NFLX", "AMD", "HON", "INTU", "QCOM", "AMGN", "MDLZ", "TMUS", "PYPL", "SBUX", "ISRG", "ADP",
    "AMAT", "GILD", "FISV", "MU", "PLD", "NOW", "LRCX", "MNST", "BKNG", "CHTR", "CTAS", "ILMN", "ATVI", "CSX", "XEL",
    "MRVL", "MCHP", "ADSK", "ADI", "AEP", "IDXX", "KLAC", "MAR", "EA", "CDNS", "CTSH", "FTNT", "SNPS", "AEE", "ROST",
    "WDAY", "DXCM", "KDP", "NXPI", "EXC", "DLTR", "LULU", "PCAR", "CEG", "PAYX", "ODFL", "PANW", "VRSK", "COST", "SIRI",
    "VRSN", "LBTYA", "NTES", "DOCU", "SPLK", "WBA", "BIIB", "ALGN", "JD", "TEAM", "CRWD", "ZM", "PDD", "ZS", "DDOG",
    "MRNA", "OKTA", "BIDU", "CSGP", "SGEN", "MELI", "ASML", "AZN", "TCOM", "EXPE", "NTAP", "GFS", "SNP", "CPRT", "MTCH",
    "KHC", "ETSY"
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
        if (data['MACD'].iloc[-2] < 0) and (data['MACD'].iloc[-3] < data['Signal'].iloc[-3]) and \
        (data['MACD'].iloc[-2] > data['Signal'].iloc[-2]) and (data['close'].iloc[-2] >= data['EMA_200'].iloc[-2]):
            message = f"YES, {symbol} {data['close'][-1]}."
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
            retries = 3
            for attempt in range(retries):
                try:
                    fetch_and_process_data(tv, symbol, exchange, interval)
                    break  # Exit retry loop if successful
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed for {symbol}. Retrying in {60 * (attempt + 1)} seconds...")
                    time.sleep(60 * (attempt + 1))
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
