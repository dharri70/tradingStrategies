import pandas as pd
import numpy as np

# Read historical data from the CSV file
data = pd.read_csv("USDCHF_M30_xsb (1).csv")

# Ensure the data has proper datetime and sorting
data["Date"] = pd.to_datetime(data["Date"])
data.sort_values("Date", inplace=True)

# Calculate moving averages and ATR for trend filtering and dynamic levels
def calculate_indicators(data):
    data["SMA_50"] = data["Close"].rolling(window=50).mean()
    data["ATR"] = (
        data[["High", "Low", "Close"]].apply(lambda x: max(x[0] - x[1], abs(x[0] - x[2]), abs(x[1] - x[2])), axis=1)
        .rolling(window=14)
        .mean()
    )
    return data

data = calculate_indicators(data)

# Identify support and resistance levels using a rolling window
def find_support_resistance(data, window=14):
    data["Support"] = data["Low"].rolling(window=window, center=True).min()
    data["Resistance"] = data["High"].rolling(window=window, center=True).max()
    return data

data = find_support_resistance(data)

# Initialize columns for trades
data["Type"] = None
data["Entry"] = None
data["Stop Loss"] = None
data["Take Profit"] = None
data["Profit/Loss ($)"] = None

# Define pip value and account settings
pip_value = 0.0001  # 1 pip = 0.0001 for EUR/USD
pip_in_dollars = 10  # 1 pip = $10 per standard lot
account_balance = 10000  # Starting account balance in dollars
risk_per_trade = 0.01  # Risk 1% of account balance per trade
spread = 1 * pip_value  # Fixed spread of 1 pip

# Simulate swing trading
for i in range(len(data)):
    # Skip rows where indicators are not yet calculated
    if pd.isna(data["SMA_50"].iloc[i]) or pd.isna(data["ATR"].iloc[i]):
        continue

    atr = data["ATR"].iloc[i]
    position_size = (account_balance * risk_per_trade) / (atr * pip_in_dollars)  # Lot size

    # Check for buy opportunity
    if data["Low"].iloc[i] <= data["Support"].iloc[i] and data["Close"].iloc[i] > data["SMA_50"].iloc[i]:
        entry_price = data["Close"].iloc[i] + spread  # Account for spread
        stop_loss = entry_price - 1.5 * atr  # 1.5 ATR below entry
        take_profit = entry_price + 3 * atr  # 3 ATR above entry

        # Simulate trade outcome
        future_prices = data.iloc[i + 1 :]
        if not future_prices.empty:
            stop_loss_hit = future_prices["Low"] <= stop_loss
            take_profit_hit = future_prices["High"] >= take_profit

            if stop_loss_hit.any() and take_profit_hit.any():
                first_stop_loss_hit = stop_loss_hit.idxmax()
                first_take_profit_hit = take_profit_hit.idxmax()
                outcome = (
                    stop_loss - entry_price if first_stop_loss_hit < first_take_profit_hit else take_profit - entry_price
                )
            elif stop_loss_hit.any():
                outcome = stop_loss - entry_price
            elif take_profit_hit.any():
                outcome = take_profit - entry_price
            else:
                outcome = 0

            data.at[i, "Type"] = "Buy"
            data.at[i, "Entry"] = entry_price
            data.at[i, "Stop Loss"] = stop_loss
            data.at[i, "Take Profit"] = take_profit
            data.at[i, "Profit/Loss ($)"] = outcome / pip_value * pip_in_dollars

    # Check for sell opportunity
    elif data["High"].iloc[i] >= data["Resistance"].iloc[i] and data["Close"].iloc[i] < data["SMA_50"].iloc[i]:
        entry_price = data["Close"].iloc[i] - spread  # Account for spread
        stop_loss = entry_price + 1.5 * atr  # 1.5 ATR above entry
        take_profit = entry_price - 3 * atr  # 3 ATR below entry

        # Simulate trade outcome
        future_prices = data.iloc[i + 1 :]
        if not future_prices.empty:
            stop_loss_hit = future_prices["High"] >= stop_loss
            take_profit_hit = future_prices["Low"] <= take_profit

            if stop_loss_hit.any() and take_profit_hit.any():
                first_stop_loss_hit = stop_loss_hit.idxmax()
                first_take_profit_hit = take_profit_hit.idxmax()
                outcome = (
                    stop_loss - entry_price if first_stop_loss_hit < first_take_profit_hit else take_profit - entry_price
                )
            elif stop_loss_hit.any():
                outcome = stop_loss - entry_price
            elif take_profit_hit.any():
                outcome = take_profit - entry_price
            else:
                outcome = 0

            data.at[i, "Type"] = "Sell"
            data.at[i, "Entry"] = entry_price
            data.at[i, "Stop Loss"] = stop_loss
            data.at[i, "Take Profit"] = take_profit
            data.at[i, "Profit/Loss ($)"] = outcome / pip_value * pip_in_dollars

# Filter rows with trades and save the results to a CSV file
results = data.dropna(subset=["Type"])[["Date", "Type", "Entry", "Stop Loss", "Take Profit", "Profit/Loss ($)"]]
results.to_csv("USDCHF_M30_xsb (1).csvSwing_Trading_Results.csv", index=False)

print("Swing trading backtest results saved to 'USDCHF_M30_xsb (1).csv")