import pandas as pd
import numpy as np

# Fetch historical data (1-hour timeframe for GBP/USD)
file_path = "USDCAD_H1_mt.csv"
data = pd.read_csv(file_path, skiprows=(1,21))

# Calculate EMA (Exponential Moving Average)
data['EMA9'] = data['Close'].ewm(span=9, adjust=False).mean()
data['EMA21'] = data['Close'].ewm(span=21, adjust=False).mean()

# Calculate ADX (Average Directional Index)
def calculate_adx(data, period=14):
    # Calculate True Range (TR)
    data['H-L'] = data['High'] - data['Low']
    data['H-PClose'] = abs(data['High'] - data['Close'].shift(1))
    data['L-PClose'] = abs(data['Low'] - data['Close'].shift(1))
    data['TR'] = data[['H-L', 'H-PClose', 'L-PClose']].max(axis=1)
    
    # Calculate +DM and -DM
    data['+DM'] = np.where(data['High'] > data['High'].shift(1), data['High'] - data['High'].shift(1), 0)
    data['-DM'] = np.where(data['Low'] < data['Low'].shift(1), data['Low'].shift(1) - data['Low'], 0)

    # Smooth TR, +DM, -DM over the period
    data['TR_smooth'] = data['TR'].rolling(window=period).sum()
    data['+DM_smooth'] = data['+DM'].rolling(window=period).sum()
    data['-DM_smooth'] = data['-DM'].rolling(window=period).sum()
    
    # Calculate +DI and -DI
    data['+DI'] = 100 * (data['+DM_smooth'] / data['TR_smooth'])
    data['-DI'] = 100 * (data['-DM_smooth'] / data['TR_smooth'])
    
    # Calculate ADX (Average Directional Index)
    data['ADX'] = 100 * (abs(data['+DI'] - data['-DI']) / (data['+DI'] + data['-DI']))

# Calculate ADX
calculate_adx(data)

# Strategy: EMA Crossover with ADX Filter
# Conditions for Buy: EMA9 > EMA21 and ADX > 25
# Conditions for Sell: EMA9 < EMA21 and ADX > 25

# Simulate trades
trade_details = []
in_position = False
entry_price = 0
stop_loss_pips = 0.0003
take_profit_pips = 0.0009
total_profit_loss = 0

for i in range(1, len(data)):
    if data['ADX'][i] > 25:  # Only trade when ADX is above 25 (strong trend)
        current_price = data['Close'][i]
        
        if not in_position:
            # Buy Signal
            if data['EMA9'][i] > data['EMA21'][i] and data['EMA9'][i-1] <= data['EMA21'][i-1]:
                entry_price = current_price
                stop_loss = entry_price - stop_loss_pips
                take_profit = entry_price + take_profit_pips
                in_position = True
                trade_details.append({
                    'Signal': 'Buy',
                    'Date': data.index[i],
                    'Entry Price': entry_price,
                    'Stop Loss': stop_loss,
                    'Take Profit': take_profit,
                    'Exit Price': None,
                    'Pip Change': None,
                    'Dollar P/L': None,
                })
        else:
            # Check for exit conditions including stop loss and take profit
            if current_price <= trade_details[-1]['Stop Loss'] or current_price >= trade_details[-1]['Take Profit']:
                exit_price = min(current_price, trade_details[-1]['Take Profit']) if current_price > entry_price else max(current_price, trade_details[-1]['Stop Loss'])
                pip_change = (exit_price - entry_price) * 10000  # Convert to pips (assuming GBP/USD)
                dollar_profit_loss = pip_change * 10  # Assume 1 pip = $0.01 for simplicity
                
                trade_details[-1]['Exit Price'] = exit_price
                trade_details[-1]['Pip Change'] = pip_change
                trade_details[-1]['Dollar P/L'] = dollar_profit_loss
                in_position = False
                total_profit_loss += dollar_profit_loss  # Add to total
            # Check for sell signal if stop loss or take profit not hit
            elif data['EMA9'][i] < data['EMA21'][i] and data['EMA9'][i-1] >= data['EMA21'][i-1]:
                exit_price = current_price
                pip_change = (exit_price - entry_price) * 10000  # Convert to pips
                dollar_profit_loss = pip_change * 10  # Assume 1 pip = $0.01 for simplicity
                
                trade_details[-1]['Exit Price'] = exit_price
                trade_details[-1]['Pip Change'] = pip_change
                trade_details[-1]['Dollar P/L'] = dollar_profit_loss
                in_position = False
                total_profit_loss += dollar_profit_loss  # Add to total

# Export trade details to a CSV file
trades_df = pd.DataFrame(trade_details)
trades_df.to_csv('isthisreal.csv', index=False)
#data.to_csv('dataframe.csv', index=False)

# Print total profit or loss
print(f"Total Profit/Loss: ${total_profit_loss:.2f}")