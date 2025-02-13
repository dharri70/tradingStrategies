import yfinance as yf
import pandas as pd
import time

def fetch_and_save_data(ticker, start_date, end_date, interval='1d', retry_limit=3, delay=2):
    """
    Fetch historical stock data from Yahoo Finance with rate limiting and retries, then save to CSV.
	Covered calll strategy, need to hold 100 shares of stock to mitigate risks

    Args:
        ticker (str): Stock ticker symbol.
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        interval (str): Data interval ('1d', '1wk', '1mo').
        retry_limit (int): Number of retry attempts in case of failure.
        delay (int): Delay in seconds between retries.

    Returns:
        None: Data is saved to a CSV file instead of returned.
    """
    for attempt in range(retry_limit):
        try:
            print(f"Fetching data for {ticker} (Attempt {attempt + 1})...")
            data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
            if data.empty:
                print(f"No data returned for {ticker}.")
                return
            print(f"Data fetched successfully for {ticker}.")
            data.to_csv(f"{ticker}_data.csv")
            return
        except Exception as e:
            print(f"Error fetching data: {e}")
            if attempt < retry_limit - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("All retries failed.")

def backtest_options_strategy_from_csv(file_path, strike_price, option_type='put', premium=1.0):
    """
    Backtest a basic options strategy using data from a CSV file.

    Args:
        file_path (str): Path to the CSV file containing stock data.
        strike_price (float): Strike price of the option.
        option_type (str): Type of the option ('call' or 'put').
        premium (float): Premium collected from selling the option.

    Returns:
        float: Total profit/loss from the strategy.
    """
    # Check for the correct date column name in the CSV
    data = pd.read_csv(file_path)
    # yfinance might use 'Date' or 'Datetime' as the column name for dates
    date_column = 'Date' if 'Date' in data.columns else 'Datetime' if 'Datetime' in data.columns else None
    
    if date_column is None:
        print("Could not find a date column in the CSV.")
        return None
    
    data[date_column] = pd.to_datetime(data[date_column])
    data.set_index(date_column, inplace=True)
    
    total_pnl = 0
    for _, row in data.iterrows():
        close_price = row['Close']  # Extract close price as a scalar value

        if option_type == 'put':
            if close_price < strike_price:
                pnl = premium + (strike_price - close_price)
            else:
                pnl = premium
        elif option_type == 'call':
            if close_price > strike_price:
                pnl = premium + (close_price - strike_price)
            else:
                pnl = premium
        else:
            raise ValueError("Invalid option type. Choose 'call' or 'put'.")
        
        total_pnl += pnl

    return total_pnl

# Settings
ticker = 'XRX'
start_date = '2023-01-01'
end_date = '2025-01-01'
strike_price = 0.5  
premium = 1.0  

# Fetch and save data
#fetch_and_save_data(ticker, start_date, end_date)

# Run backtest using the CSV file
csv_file_path = f"{ticker}_data.csv"
if not pd.read_csv(csv_file_path).empty:
    pnl = backtest_options_strategy_from_csv(csv_file_path, strike_price, option_type='put', premium=premium)
    if pnl is not None:
        print(f"Total Profit/Loss from the strategy: ${pnl:.2f}")
else:
    print("No data available in the CSV file.")