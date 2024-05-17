import time
import pandas as pd
import os
import requests
from tvDatafeed import TvDatafeed, Interval

# Initialize the TvDatafeed object
tv = TvDatafeed()

# Fetch the Discord webhook URL from environment variables
discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')

if not discord_webhook_url:
    raise ValueError("Discord webhook URL is not set. Please set the DISCORD_WEBHOOK_URL environment variable.")

# List of symbols
symbols = ['TADAWUL:2082', 'TADAWUL:1120', 'TADAWUL:2010']  # Example symbols for Saudi market

def send_discord_message(message):
    data = {
        "content": message
    }
    response = requests.post(discord_webhook_url, json=data)
    if response.status_code != 204:
        print(f"Failed to send message to Discord: {response.status_code}, {response.text}")

# Fetch historical data with retries
def fetch_and_process_data(tv, symbol, exchange, interval):
    try:
        # Fetch historical data
        data = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=200)
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

        # Calculate MACD Histogram
        data['MACD_Hist'] = data['MACD'] - data['Signal']

        # Calculate the 200-period EMA
        data['EMA_200'] = data['close'].ewm(span=200, adjust=False).mean()

        # Check for signal conditions
        signal = False
        if data['EMA_short'].iloc[-2] < data['EMA_long'].iloc[-2] and data['EMA_short'].iloc[-1] > data['EMA_long'].iloc[-1] and \
           data['close'].iloc[-1] >= data['EMA_200'].iloc[-1]:
            signal = True

        # Output signal for each symbol
        if signal:
            message = f"YES, {symbol} - Short-term EMA crossed above long-term EMA and price is above 200 EMA."
            print(message)
            send_discord_message(message)
        else:
            message = f"NO, {symbol} - No signal."
            send_discord_message(message)
            print(message)

        # Display the last few rows with the calculated values
        print(data[['close', 'EMA_short', 'EMA_long', 'MACD', 'Signal', 'MACD_Hist', 'EMA_200']].tail())

    except Exception as e:
        print(f"Error processing data for {symbol}: {e}")
        raise  # Re-raise the exception to trigger retry logic

def main():
    exchange = 'TADAWUL'
    interval = Interval.in_5_minute

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

        time.sleep(300)  # Wait for 5 minutes before the next iteration

if __name__ == "__main__":
    main()
