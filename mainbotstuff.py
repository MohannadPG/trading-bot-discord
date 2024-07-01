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
"NASDAQ:AAPL", "NASDAQ:MSFT", "NASDAQ:GOOGL", "NASDAQ:GOOG", "NASDAQ:AMZN", "NASDAQ:META", "NASDAQ:TSLA", "NASDAQ:NVDA", "NASDAQ:PYPL", "NASDAQ:ADBE", 
"NASDAQ:INTC", "NASDAQ:CMCSA", "NASDAQ:PEP", "NASDAQ:CSCO", "NASDAQ:AVGO", "NASDAQ:COST", "NASDAQ:TMUS", "NASDAQ:QCOM", "NASDAQ:TXN", "NASDAQ:CHTR", 
"NASDAQ:AMGN", "NASDAQ:SBUX", "NASDAQ:ISRG", "NASDAQ:AMD", "NASDAQ:BKNG", "NASDAQ:INTU", "NASDAQ:MDLZ", "NASDAQ:MU", "NASDAQ:ADP", "NASDAQ:LRCX", 
"NASDAQ:CSX", "NASDAQ:GILD", "NASDAQ:VRTX", "NASDAQ:KHC", "NASDAQ:MELI", "NASDAQ:ILMN", "NASDAQ:ATVI", "NASDAQ:MRNA", "NASDAQ:MNST", 
"NASDAQ:AMAT", "NASDAQ:JD", "NASDAQ:ZM", "NASDAQ:EBAY", "NASDAQ:ADSK", "NASDAQ:BIIB", "NASDAQ:ASML", "NASDAQ:DOCU", "NASDAQ:WDAY", "NASDAQ:SNPS", 
"NASDAQ:ADI", "NASDAQ:DXCM", "NASDAQ:OKTA", "NASDAQ:REGN", "NASDAQ:EA", "NASDAQ:ROST", "NASDAQ:CTAS", "NASDAQ:MTCH", 
"NASDAQ:KDP", "NASDAQ:IDXX", "NASDAQ:TEAM", "NASDAQ:PCAR", "NASDAQ:WBA", "NASDAQ:MAR", "NASDAQ:VRSN", "NASDAQ:EXC", "NASDAQ:EXPE", "NASDAQ:CPRT", 
"NASDAQ:SIRI", "NASDAQ:ANSS", "NASDAQ:FAST", "NASDAQ:WDC", "NASDAQ:TTWO", "NASDAQ:PAYX", "NASDAQ:SWKS", "NASDAQ:NTES", "NASDAQ:CDNS", 
"NASDAQ:KLAC", "NASDAQ:CTSH", "NASDAQ:VRSK", "NASDAQ:INCY", "NASDAQ:TCOM", "NASDAQ:HAS", "NASDAQ:LULU", "NASDAQ:ULTA", "NASDAQ:NTAP", 
"NASDAQ:CDW", "NASDAQ:ALGN", "NASDAQ:ORLY", "NASDAQ:DLTR", "NASDAQ:CHKP", "NASDAQ:FOX", "NASDAQ:FOXA", "NASDAQ:FTNT",  "NASDAQ:AKAM", "NASDAQ:MCHP", 
"NASDAQ:ILMN",  "NASDAQ:LBTYK", "NASDAQ:QRVO", "NASDAQ:JBHT", 
"NASDAQ:NXPI", "NASDAQ:CSGP", "NASDAQ:ISRG", "NASDAQ:NTES", "NASDAQ:TCOM", 
"NASDAQ:JD",  "NASDAQ:ADSK", "NASDAQ:ADP", "NASDAQ:ALNY", "NASDAQ:AMD", "NASDAQ:AMGN", 
"NASDAQ:ANSS", "NASDAQ:ASML", "NASDAQ:ATVI", "NASDAQ:AVGO", "NASDAQ:AXON", "NASDAQ:BKNG", "NASDAQ:CDNS",
"NASDAQ:COST", "NASDAQ:CPRT", "NASDAQ:CSCO", "NASDAQ:CSGP", "NASDAQ:CSX", "NASDAQ:CTAS", "NASDAQ:CTSH",
"NASDAQ:DLTR", "NASDAQ:EXC", "NASDAQ:EXPE",
"NASDAQ:FOXA", "NASDAQ:FTNT", "NASDAQ:GILD", "NASDAQ:GOOG", "NASDAQ:GOOGL", "NASDAQ:HAS", "NASDAQ:HSIC", "NASDAQ:IDXX", "NASDAQ:ILMN", "NASDAQ:INCY", 
"NASDAQ:INTC", "NASDAQ:INTU", "NASDAQ:JD", "NASDAQ:LBTYA", 
"NASDAQ:MAR", "NASDAQ:MDLZ", "NASDAQ:MRNA", "NASDAQ:MU", 
"NASDAQ:NFLX", "NASDAQ:NTAP", "NASDAQ:NTES", "NASDAQ:NVDA", "NASDAQ:NXPI", "NASDAQ:OKTA", "NASDAQ:ORLY", "NASDAQ:PAYX", "NASDAQ:PCAR", "NASDAQ:PEP", 
"NASDAQ:PYPL", "NASDAQ:ROST", "NASDAQ:SBAC",
"NASDAQ:SWKS", "NASDAQ:TMUS", "NASDAQ:TXN", "NASDAQ:ULTA",  
"NASDAQ:WBA", "NASDAQ:WDAY", "NASDAQ:WDC","NASDAQ:ZG", "NASDAQ:Z",
"NASDAQ:LIN", "NASDAQ:CTAS", "NASDAQ:ODFL", "NASDAQ:TTD", "NASDAQ:XEL", "NASDAQ:TSCO", "NASDAQ:NUAN", "NASDAQ:TER", "NASDAQ:POOL"
'NASDAQ:IFBD', 'NASDAQ:CNTX','NASDAQ:ENVB', 'NASDAQ:QNRX', 'NASDAQ:LITM', 'NASDAQ:GNPX', 'NASDAQ:SSYS', 'NASDAQ:PMCB', 'NASDAQ:IMMX', 'NASDAQ:NLSP', 'NASDAQ:BIOR', 'NASDAQ:BBLG','NASDAQ:VS', 'NASDAQ:NUVL', 'NASDAQ:WIRE', 'NASDAQ:IDN', 'NASDAQ:ALRN', 'NASDAQ:ADD', 'NASDAQ:XELB','NASDAQ:VRPX', 'NASDAQ:HTOO', 'NASDAQ:BRFH','NASDAQ:SIFY', 'NASDAQ:MDJH', 'NASDAQ:NVCT', 'NASDAQ:DSWL','NASDAQ:GNTX', 'NASDAQ:UXIN', 'NASDAQ:TALK', 'NASDAQ:BCTX','NASDAQ:CRCT', 'NASDAQ:CHKP', 'NASDAQ:RCEL', 'NASDAQ:KTRA',  'NASDAQ:MTCH', 'NASDAQ:ATOS', 'NASDAQ:AEHL', 'NASDAQ:CMPX', 'NASDAQ:MNPR', 'NASDAQ:TLSA',  'NASDAQ:ALDX', 'NASDAQ:ACXP', 'NASDAQ:PAX', 'NASDAQ:CHSCO', 'NASDAQ:BHF', 'NASDAQ:ATXI'
"NASDAQ:HYMC", "NASDAQ:GNTA", "NASDAQ:HYZN","NASDAQ:SVC", "NASDAQ:BROG", "NASDAQ:SNPX", "NASDAQ:ARTL", "NASDAQ:VIRI", "NASDAQ:UTSI",  "NASDAQ:AVGO", "NASDAQ:DSGN","NASDAQ:OCUP", "NASDAQ:LTBR","NASDAQ:TAIT", "NASDAQ:LAND", "NASDAQ:BRZE", "NASDAQ:GTHX", "NASDAQ:XBIT", "NASDAQ:XOMA", "NASDAQ:CRMD", "NASDAQ:GLMD"
"NASDAQ: CMPOW", "NASDAQ: ANEB", "NASDAQ: BOLD", "NASDAQ: DHCNI", "NASDAQ: AVXL", "NASDAQ: BNOX", "NASDAQ: TRIV", "NASDAQ: TAYD", "NASDAQ: BZFDW", "NASDAQ: CHSCL", "NASDAQ: QRTEP", "NASDAQ: NNAVW", "NASDAQ: CLBTW", "NASDAQ: VRMEW", "NASDAQ: PCTTU", "NASDAQ: BPYPN", "NASDAQ: BPYPO", "NASDAQ: GOODN", "NASDAQ: CHSCM", "NASDAQ: CHSCN", "NASDAQ: CHSCO", "NASDAQ: CSSEL", "NASDAQ: DHCNL", "NASDAQ: PMN", "NASDAQ: AGRIW", "NASDAQ: MSSAR"






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
        for i in range(-1,0):
            if (data['MACD'].iloc[i-1] < 0) and (data['MACD'].iloc[i-2] < data['Signal'].iloc[i-2]) and \
                (data['MACD'].iloc[i-1] > data['Signal'].iloc[i-1]) and (data['close'].iloc[i-1] >= data['EMA_200'].iloc[i-1]) and data['close'] < 30:
                message = f"YES, {symbol} {data['close'][i-1]}."
                print(message)
                send_discord_message(message)

    except Exception as e:
        print(f"Error processing data for {symbol}: {e}")
        raise  # Re-raise the exception to trigger retry logic

def main():
    exchange = 'NASDAQ'
    interval = Interval.in_30_minute

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
        if execution_time < 1800:
            time.sleep(1800 - execution_time)
        start_time = time.time()

if __name__ == "__main__":
    main()
