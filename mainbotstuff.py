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
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT", "XRPUSDT", "DOTUSDT", "DOGEUSDT", "AVAXUSDT", "LUNAUSDT", "LINKUSDT", "LTCUSDT", "BCHUSDT", "ALGOUSDT", "ICPUSDT", "VETUSDT", "FILUSDT", "TRXUSDT", "ATOMUSDT", "AAVEUSDT", "UNIUSDT", "EOSUSDT", "XTZUSDT", "FTTUSDT", "SHIBUSDT", "ETCUSDT", "THETAUSDT", "CAKEUSDT", "SANDUSDT", "AXSUSDT", "XLMUSDT", "FTMUSDT", "MANAUSDT", "MATICUSDT", "NEOUSDT", "MKRUSDT", "ENJUSDT", "KSMUSDT", "RUNEUSDT", "CVCUSDT", "CHZUSDT", "ZECUSDT", "WAVESUSDT", "GRTUSDT", "HOTUSDT", "ZILUSDT", "TFUELUSDT", "ONEUSDT", "UMAUSDT", "BATUSDT", "COMPUSDT", "RVNUSDT", "IOSTUSDT", "SUSHIUSDT", "DOGEUSDT", "STXUSDT", "EGLDUSDT", "DASHUSDT", "AMPUSDT", "YFIUSDT", "QTUMUSDT", "NEARUSDT", "ZRXUSDT", "SCUSDT", "BNTUSDT", "RENUSDT", "ONTUSDT", "SXPUSDT", "LSKUSDT", "TUSDUSDT", "GALAUSDT", "ZENUSDT", "LRCUSDT", "NEXOUSDT", "CRVUSDT", "OMGUSDT", "CELOUSDT", "FETUSDT", "VGXUSDT"
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
            time.sleep(0.5)
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
