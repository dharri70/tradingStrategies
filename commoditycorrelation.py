import pandas as pd
import numpy as np

# Load data
xauusd_data = pd.read_csv('XAUUSD_D1.csv', parse_dates=True, index_col='Date')
dxy_data = pd.read_csv('Download Data - INDEX_US_IFUS_DXY (1).csv', parse_dates=True, index_col='Date')

# Ensure both datasets are aligned on dates
data = pd.merge(xauusd_data, dxy_data, left_index=True, right_index=True, suffixes=('_XAU', '_DXY'))

# Calculate ATR manually
high = data['High_XAU']
low = data['Low_XAU']
close = data['Close_XAU']

# True range is the maximum of (High - Low), (High - Previous Close), (Previous Close - Low)
tr = pd.DataFrame({
    'High-Low': high - low,
    'High-Prev Close': abs(high - close.shift(1)),
    'Low-Prev Close': abs(low - close.shift(1))
})

# Calculate ATR (14-period moving average of true range)
data['ATR'] = tr.max(axis=1).rolling(window=14).mean()

# Define entry conditions for XAU/USD based on Dollar Index (DXY)
data['Long_Entry'] = (data['Close_DXY'] < data['Low_DXY'].shift(1))  # DXY closes below support
data['Short_Entry'] = (data['Close_DXY'] > data['High_DXY'].shift(1))  # DXY closes above resistance

# Define risk-to-reward ratio (1:3)
risk_to_reward_ratio = 5

# Calculate stop loss and take profit dynamically based on ATR
data['Stop_Loss_Long'] = data['Close_XAU'] - data['ATR']
data['Take_Profit_Long'] = data['Close_XAU'] + (data['ATR'] * risk_to_reward_ratio)

data['Stop_Loss_Short'] = data['Close_XAU'] + data['ATR']
data['Take_Profit_Short'] = data['Close_XAU'] - (data['ATR'] * risk_to_reward_ratio)

# Prepare a list to store trade details
trade_details = []

# Simulate trades
for i in range(1, len(data)):
    if data['Long_Entry'].iloc[i]:
        # Long trade: Entry at the close of the next candle
        entry_price = data['Close_XAU'].iloc[i]
        stop_loss = data['Stop_Loss_Long'].iloc[i]
        take_profit = data['Take_Profit_Long'].iloc[i]
        for j in range(i + 1, len(data)):
            if data['Close_XAU'].iloc[j] <= stop_loss:  # Stop loss hit
                trade_details.append({
                    'Trade Type': 'Long',
                    'Entry Date': data.index[i],
                    'Entry Price': entry_price,
                    'Stop Loss': stop_loss,
                    'Take Profit': take_profit,
                    'Exit Date': data.index[j],
                    'Exit Price': data['Close_XAU'].iloc[j],
                    'Profit/Loss (PIP)': (stop_loss - entry_price) * 1000
                })
                break
            elif data['Close_XAU'].iloc[j] >= take_profit:  # Take profit hit
                trade_details.append({
                    'Trade Type': 'Long',
                    'Entry Date': data.index[i],
                    'Entry Price': entry_price,
                    'Stop Loss': stop_loss,
                    'Take Profit': take_profit,
                    'Exit Date': data.index[j],
                    'Exit Price': data['Close_XAU'].iloc[j],
                    'Profit/Loss (PIP)': (take_profit - entry_price) * 1000
                })
                break
    elif data['Short_Entry'].iloc[i]:
        # Short trade: Entry at the close of the next candle
        entry_price = data['Close_XAU'].iloc[i]
        stop_loss = data['Stop_Loss_Short'].iloc[i]
        take_profit = data['Take_Profit_Short'].iloc[i]
        for j in range(i + 1, len(data)):
            if data['Close_XAU'].iloc[j] >= stop_loss:  # Stop loss hit
                trade_details.append({
                    'Trade Type': 'Short',
                    'Entry Date': data.index[i],
                    'Entry Price': entry_price,
                    'Stop Loss': stop_loss,
                    'Take Profit': take_profit,
                    'Exit Date': data.index[j],
                    'Exit Price': data['Close_XAU'].iloc[j],
                    'Profit/Loss (PIP)': (entry_price - stop_loss) * 1000
                })
                break
            elif data['Close_XAU'].iloc[j] <= take_profit:  # Take profit hit
                trade_details.append({
                    'Trade Type': 'Short',
                    'Entry Date': data.index[i],
                    'Entry Price': entry_price,
                    'Stop Loss': stop_loss,
                    'Take Profit': take_profit,
                    'Exit Date': data.index[j],
                    'Exit Price': data['Close_XAU'].iloc[j],
                    'Profit/Loss (PIP)': (entry_price - take_profit) * 1000
                })
                break

# Save trade details to CSV
trade_df = pd.DataFrame(trade_details)
trade_df.to_csv('trade_results.csv', index=False)

# Output results
print(f'Total Trades: {len(trade_details)}')
print(f'Trades saved to "trade_results.csv".')