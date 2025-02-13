import pandas as pd
import numpy as np

# Parameters
short_window = 50  # 50-hour SMA
long_window = 200  # 200-hour SMA
risk_reward_ratio = 2  # Reward-to-risk ratio for TP/SL
atr_period = 14  # Period for ATR calculation
#pip_value = 0.01  # Value of 1 pip for USD/JPY
#pip_worth = 7  # $10 per pip for a standard lot
pip_value = 0.0001  # Value of 1 pip for USD/CHF
pip_worth = 10  # $10 per pip for a standard lot

# Load CSV file
file_path = "EURUSD_M5_mt.csv"  # Adjust the file path if necessary
data = pd.read_csv(file_path)

# Ensure 'Date' column is in datetime format
data["Date"] = pd.to_datetime(data["Date"])

# Sort by date if not already sorted
data = data.sort_values(by="Date").reset_index(drop=True)

# Calculate Moving Averages
data["SMA_50"] = data["Close"].rolling(window=short_window).mean()
data["SMA_200"] = data["Close"].rolling(window=long_window).mean()

# Calculate Average True Range (ATR)
data["High-Low"] = data["High"] - data["Low"]
data["High-Close"] = abs(data["High"] - data["Close"].shift(1))
data["Low-Close"] = abs(data["Low"] - data["Close"].shift(1))
data["True Range"] = data[["High-Low", "High-Close", "Low-Close"]].max(axis=1)
data["ATR"] = data["True Range"].rolling(window=atr_period).mean()

# Define trade signals
data["Signal"] = 0
data.loc[data["SMA_50"] > data["SMA_200"], "Signal"] = 1  # Buy Signal
data.loc[data["SMA_50"] < data["SMA_200"], "Signal"] = -1  # Sell Signal

# Simulate trades
trades = []
for i in range(1, len(data)):
    if data["Signal"].iloc[i] == 1 and data["Signal"].iloc[i - 1] <= 0:  # Buy Signal
        entry_price = data["Close"].iloc[i]
        stop_loss = entry_price - data["ATR"].iloc[i]  # Stop Loss
        take_profit = entry_price + (data["ATR"].iloc[i] * risk_reward_ratio)  # Take Profit
        profit_loss_pips = (take_profit - entry_price) / pip_value  # P&L in pips
        trades.append({
            "Date": data["Date"].iloc[i],
            "Type": "Buy",
            "Entry": entry_price,
            "Stop Loss": stop_loss,
            "Take Profit": take_profit,
            "Profit/Loss ($)": profit_loss_pips * pip_worth  # P&L in USD
        })
    elif data["Signal"].iloc[i] == -1 and data["Signal"].iloc[i - 1] >= 0:  # Sell Signal
        entry_price = data["Close"].iloc[i]
        stop_loss = entry_price + data["ATR"].iloc[i]  # Stop Loss
        take_profit = entry_price - (data["ATR"].iloc[i] * risk_reward_ratio)  # Take Profit
        profit_loss_pips = (entry_price - take_profit) / pip_value  # P&L in pips
        trades.append({
            "Date": data["Date"].iloc[i],
            "Type": "Sell",
            "Entry": entry_price,
            "Stop Loss": stop_loss,
            "Take Profit": take_profit,
            "Profit/Loss ($)": profit_loss_pips * pip_worth  # P&L in USD
        })

# Output trades
trades_df = pd.DataFrame(trades)
print(trades_df)

# Save to CSV
trades_df.to_csv("EURUSD_M5_mt.csv_trades_with_profit_loss2.csv", index=False)
print("Trades saved to 'EURUSD_M5_mt.csv.csv_trades_with_profit_loss2.csv'")