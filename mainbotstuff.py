import time
import os
import requests
from tvDatafeed import TvDatafeed, Interval
from dotenv import load_dotenv
import pandas as pd

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
    'TADAWUL:4080', 'TADAWUL:4081', 'TADAWUL:2360', 'TADAWUL:2170', 'TADAWUL:2290', 'TADAWUL:2250',
    'TADAWUL:2020', 'TADAWUL:2010', 'TADAWUL:2210', 'TADAWUL:2330', 'TADAWUL:2310', 'TADAWUL:2350',
    'TADAWUL:2001', 'TADAWUL:2080', 'TADAWUL:4200', 'TADAWUL:4180', 'TADAWUL:4190', 'TADAWUL:4240',
    'TADAWUL:4001', 'TADAWUL:4003', 'TADAWUL:1214', 'TADAWUL:4164', 'TADAWUL:4012', 'TADAWUL:4008',
    'TADAWUL:4163', 'TADAWUL:4007', 'TADAWUL:4013', 'TADAWUL:4002', 'TADAWUL:4004', 'TADAWUL:2230',
    'TADAWUL:4292', 'TADAWUL:4291', 'TADAWUL:6002', 'TADAWUL:6004', 'TADAWUL:6001', 'TADAWUL:2050',
    'TADAWUL:2270', 'TADAWUL:2280', 'TADAWUL:2100', 'TADAWUL:6010', 'TADAWUL:4162', 'TADAWUL:6013',
    'TADAWUL:6012', 'TADAWUL:4061', 'TADAWUL:6020', 'TADAWUL:6060', 'TADAWUL:2030', 'TADAWUL:2120',
    'TADAWUL:2081', 'TADAWUL:7010', 'TADAWUL:7020', 'TADAWUL:7040', 'TADAWUL:7030', 'TADAWUL:2160',
    'TADAWUL:2040', 'TADAWUL:2180', 'TADAWUL:2240', 'TADAWUL:2150', 'TADAWUL:2090', 'TADAWUL:2130',
    'TADAWUL:1301', 'TADAWUL:2320', 'TADAWUL:2340', 'TADAWUL:1302', 'TADAWUL:1303', 'TADAWUL:1202',
    'TADAWUL:3007', 'TADAWUL:3008', 'TADAWUL:7201', 'TADAWUL:7202', 'TADAWUL:7203', 'TADAWUL:4170',
    'TADAWUL:1820', 'TADAWUL:1810', 'TADAWUL:4030', 'TADAWUL:4040', 'TADAWUL:4260', 'TADAWUL:4323',
    'TADAWUL:4321', 'TADAWUL:4320', 'TADAWUL:4150', 'TADAWUL:4100', 'TADAWUL:4090', 'TADAWUL:4300',
    'TADAWUL:4310', 'TADAWUL:4230'
]
# Example symbol for BTCUSDT on Binance

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
        if (data['MACD'].iloc[-1] < 0) and (data['MACD'].iloc[-2] < data['Signal'].iloc[-2]) and \
        (data['MACD'].iloc[-1] > data['Signal'].iloc[-1]) and (data['close'].iloc[-1] >= data['EMA_200'].iloc[-1]):
            message = f"YES, {symbol} {data['close'][-1]}."
            print(message)
            send_discord_message(message)
        else:
            message =f"NO Signal for {symbol}"
            print(message)
            send_discord_message(message)

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

        

if __name__ == "__main__":
    main()
