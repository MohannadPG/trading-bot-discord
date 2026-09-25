# Stock Market Signal Bot

A Python bot that scans 231 NASDAQ and NYSE stocks every 30 minutes during US market hours, looks for a MACD bullish crossover confirmed by the 200-period EMA, and posts any matches to a Discord channel.

## How it works

Every 30 minutes, the bot downloads the last 500 half-hour candles for each stock on its watchlist from TradingView (via [tvDatafeed](https://github.com/rongardF/tvdatafeed)). It then uses pandas to calculate three indicators:

| Indicator | Calculation |
| --- | --- |
| MACD | 12-period EMA minus 26-period EMA |
| Signal line | 9-period EMA of the MACD |
| Trend filter | 200-period EMA of the closing price |

A stock triggers a **buy signal** when all three conditions are true on the latest completed candle:

1. **MACD crosses above the signal line**: momentum is turning upward.
2. **The cross happens below zero**: the move is early, coming out of a downswing.
3. **Price is at or above the 200 EMA**: the long-term trend is still up.

The idea is to catch short-term pullbacks that are turning back up inside a longer-term uptrend, and to filter out crossovers that happen against the trend.

When a stock matches, the bot sends a message to Discord through a webhook:

```
YES, AAPL 189.52.,30min
```

The bot only runs during US market hours (13:30–20:30 GMT, Monday to Friday) and skips scans outside that window. If data for one ticker fails to download, it logs the error and moves on, so a single failure doesn't stop the scan.

## Tech stack

- **Python**
- **tvDatafeed**: historical price data from TradingView
- **pandas**: indicator calculations (exponential moving averages)
- **requests**: sends signals to the Discord webhook
- **python-dotenv**: loads the webhook URL from an environment file
- **pytz**: time zone handling for market hours

## Setup

1. **Clone the repo**

   ```bash
   git clone https://github.com/MohannadPG/trading-bot-discord.git
   cd trading-bot-discord
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   bash setup.sh   # installs tvDatafeed from GitHub
   ```

3. **Create a Discord webhook**

   In your Discord server, go to Server Settings → Integrations → Webhooks, create a webhook for the channel you want signals in, and copy its URL.

4. **Add your webhook URL**

   Create a file called `mem.env` in the project folder:

   ```
   DISCORD_WEBHOOK_URL=your_webhook_url_here
   ```

   This file is listed in `.gitignore` and should never be committed, since anyone with the URL can post to your channel.

5. **Run the bot**

   ```bash
   python bot.py
   ```

The repo also includes a `Procfile`, so it can run as a background worker on platforms such as Heroku.

## Customising

- **Watchlist**: edit the `symbols` list in `bot.py`. Each entry uses the format `EXCHANGE:TICKER`, for example `NASDAQ:AAPL`.
- **Timeframe**: change `Interval.in_30_minute` in `main()` to another tvDatafeed interval, such as `Interval.in_1_hour`.
- **Indicator settings**: adjust `short_window`, `long_window` and `signal_window` in `fetch_and_process_data()`.

## Disclaimer

This project is for learning purposes only and is not financial advice. The signals have not been backtested, and TradingView data accessed without logging in may be delayed or limited.
