import sys
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

def plot_stock_data(ticker, start_date, end_date):
    # Fetch stock data using yfinance
    data = yf.download(ticker, start=start_date, end=end_date)
    if data.empty:
        print(f"No data found for ticker {ticker}. Please check the symbol and dates.")
        return

    # Plot stock price and volume
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot closing price
    ax1.plot(data.index, data['Close'], label='Close Price', color='blue', lw=2)
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Stock Price', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    # Format x-axis for date
    ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)

    # Add a secondary y-axis for volume
    ax2 = ax1.twinx()
    ax2.bar(data.index, data['Volume'], alpha=0.3, color='gray', label='Volume')
    ax2.set_ylabel('Volume', color='gray')
    ax2.tick_params(axis='y', labelcolor='gray')

    # Title and legend
    plt.title(f"{ticker.upper()} Stock Price and Volume")
    fig.tight_layout()
    plt.legend(loc='upper left')

    # Save as a jpg image
    output_file = f"{ticker}_stock_graph.jpg"
    plt.savefig(output_file, format='jpg')
    print(f"Graph saved as {output_file}")
    plt.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <ticker> <start_date> <end_date> <num_days>")
        sys.exit(1)

    # Parse command-line arguments
    ticker = sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]
    
    plot_stock_data(ticker, start_date, end_date)
