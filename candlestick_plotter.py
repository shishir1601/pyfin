import sys
import yfinance as yf
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

def calculate_bollinger_bands(data, window=20, num_std_dev=2):
    """Calculate Bollinger Bands."""
    rolling_mean = data['Close'].rolling(window).mean()
    rolling_std = data['Close'].rolling(window).std()
    data['Upper Band'] = rolling_mean + (rolling_std * num_std_dev)
    data['Lower Band'] = rolling_mean - (rolling_std * num_std_dev)
    return data

def calculate_rsi(data, periods=14):
    """Calculate Relative Strength Index (RSI)."""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    return data

def plot_stock_data(ticker, start_date, end_date):

    end_date = pd.to_datetime(end_date)

    # Fetch 15-minute interval stock data
    #data = yf.download(ticker, interval='15m',start=start_date, end=end_date.strftime('%Y-%m-%d %H:%M:%S'))
    #data = yf.download(ticker, start=start_date, end=end_date, interval='15m', prepost=True)
    data = yf.download(ticker, start=start_date, end=end_date)
    if data.empty:
        print(f"No data found for ticker {ticker}. Please check the symbol and dates.")
        return

    # Reset index for plotting candlestick chart
    data.reset_index(inplace=True)
    data['Date'] = mdates.date2num(data['Datetime'])

    # Calculate Bollinger Bands and RSI
    data = calculate_bollinger_bands(data)
    data = calculate_rsi(data)

    # Create the plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [3, 1]})
    fig.suptitle(f"{ticker.upper()} Stock Price (15m Interval) with Bollinger Bands and RSI", fontsize=16)

    # Candlestick chart with Bollinger Bands
    ax1.set_title('Candlestick Chart with Bollinger Bands')
    candlestick_ohlc(ax1, data[['Date', 'Open', 'High', 'Low', 'Close']].values, width=0.01, colorup='green', colordown='red')
    ax1.plot(data['Date'], data['Upper Band'], color='blue', linestyle='--', label='Upper Band')
    ax1.plot(data['Date'], data['Lower Band'], color='blue', linestyle='--', label='Lower Band')
    ax1.legend()
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    ax1.set_ylabel('Price')
    ax1.grid()

    # RSI section
    ax2.set_title('Relative Strength Index (RSI)')
    ax2.plot(data['Date'], data['RSI'], label='RSI', color='purple')
    ax2.axhline(70, color='red', linestyle='--', label='Overbought')
    ax2.axhline(30, color='green', linestyle='--', label='Oversold')
    ax2.set_ylabel('RSI')
    ax2.set_xlabel('Date')
    ax2.legend()
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    ax2.grid()

    # Save the plot
    output_file = f"{ticker}_candlestick_with_bollinger_and_rsi.jpg"
    plt.tight_layout()
    plt.savefig(output_file, format='jpg')
    print(f"Graph saved as {output_file}")
    plt.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <ticker> <start_date> <end_date>")
        sys.exit(1)

    # Parse command-line arguments
    ticker = sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]

    # Check if the date range is valid
    date_diff = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days
    if date_diff > 100:
        raise ValueError("Date range cannot exceed 100 days.")

    plot_stock_data(ticker, start_date, end_date)


#example
#     python candlestick_plotter.py AAPL 2023-11-30 2023-12-05
 