import pandas as pd
import numpy as np

# Load your CSV data
def load_data(file_path):
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    return df

# Calculate indicators
def calculate_indicators(df):
    # ATR Calculation
    df['H-L'] = df['High'] - df['Low']
    df['H-C'] = abs(df['High'] - df['Close'].shift(1))
    df['L-C'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['H-L', 'H-C', 'L-C']].max(axis=1)
    df['ATR'] = df['TR'].rolling(window=14).mean()

    # Bollinger Bands
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['STD20'] = df['Close'].rolling(window=20).std()
    df['UpperBand'] = df['SMA20'] + (df['STD20'] * 2)
    df['LowerBand'] = df['SMA20'] - (df['STD20'] * 2)

    # RSI Calculation
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    return df

# Backtest strategy
def backtest_strategy(df, stop_loss_multiplier=0.5, take_profit_multiplier=0.5):
    initial_balance = 10000
    balance = initial_balance
    position = 0
    stop_loss = 0
    take_profit = 0
    trades = []

    for i in range(1, len(df)):
        # Check for entry
        if position == 0:
            if (
                df['Close'].iloc[i] <= df['LowerBand'].iloc[i] and
                df['RSI'].iloc[i] < 30
            ):
                position = 1  # Long position
                entry_price = df['Close'].iloc[i]
                stop_loss = entry_price - (stop_loss_multiplier * df['ATR'].iloc[i])
                take_profit = entry_price + (take_profit_multiplier * df['ATR'].iloc[i])
                trades.append({'type': 'buy', 'price': entry_price, 'date': df.index[i], 'profit_loss': 0})

            elif (
                df['Close'].iloc[i] >= df['UpperBand'].iloc[i] and
                df['RSI'].iloc[i] > 70
            ):
                position = -1  # Short position
                entry_price = df['Close'].iloc[i]
                stop_loss = entry_price + (stop_loss_multiplier * df['ATR'].iloc[i])
                take_profit = entry_price - (take_profit_multiplier * df['ATR'].iloc[i])
                trades.append({'type': 'sell', 'price': entry_price, 'date': df.index[i], 'profit_loss': 0})

        # Check for exit
        elif position == 1:
            if df['Close'].iloc[i] <= stop_loss or df['Close'].iloc[i] >= take_profit:
                profit_loss = (df['Close'].iloc[i] - entry_price) / 0.0001 * 10
                balance += profit_loss
                trades[-1]['profit_loss'] = profit_loss
                position = 0
                trades.append({'type': 'sell', 'price': df['Close'].iloc[i], 'date': df.index[i], 'profit_loss': profit_loss})

        elif position == -1:
            if df['Close'].iloc[i] >= stop_loss or df['Close'].iloc[i] <= take_profit:
                profit_loss = (entry_price - df['Close'].iloc[i]) / 0.0001 * 10
                balance += profit_loss
                trades[-1]['profit_loss'] = profit_loss
                position = 0
                trades.append({'type': 'buy', 'price': df['Close'].iloc[i], 'date': df.index[i], 'profit_loss': profit_loss})

    # Summary
    profit = balance - initial_balance
    print(f"Initial Balance: ${initial_balance}")
    print(f"Final Balance: ${balance}")
    print(f"Net Profit: ${profit}")

    # Save trades to CSV
    trades_df = pd.DataFrame(trades)
    trades_df.to_csv('low_risk_trades.csv', index=False)
    print("Trades saved to low_risk_trades.csv")

    return trades

# Main function
def main():
    file_path = 'USDCHF_M30_xsb (1).csv'  # Replace with your file path
    df = load_data(file_path)
    df = calculate_indicators(df)
    backtest_strategy(df)

if __name__ == "__main__":
    main()