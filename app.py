import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import requests
import pandas as pd
import plotly.express as px 

# Function definitions
@st.cache_data(ttl=300)
def get_stock_data(symbol, API_KEY):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()['Time Series (Daily)']
    df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close'])
    
    for date, values in data.items():
        row = {'Date': date, 'Open': float(values['1. open']), 'High': float(values['2. high']),
               'Low': float(values['3. low']), 'Close': float(values['4. close'])}
        row_df = pd.DataFrame([row])  # Convert a single-row dict to DataFrame
        df = pd.concat([df, row_df], ignore_index=True)
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date', inplace=True)
    return df

# Function to calculate the payoff for a call option
def calculate_call_payoff(prices, strike, asset_price):
    return np.maximum(prices - strike, 0) - asset_price

# Function to calculate the payoff for a put option
def calculate_put_payoff(prices, strike, asset_price):
    return np.maximum(strike - prices, 0) - asset_price

# Function to calculate the payoff for a straddle option
def calculate_straddle_payoff(asset_prices, strike, premium):
    call_payoff = np.maximum(asset_prices - strike, 0) - premium
    put_payoff = np.maximum(strike - asset_prices, 0) - premium
    return call_payoff + put_payoff

# Function to calculate the payoff for a covered call option
def calculate_covered_call_payoff(asset_prices, purchase_price, strike_price, premium_received):
    long_asset_payoff = asset_prices - purchase_price
    short_call_payoff = np.where(asset_prices > strike_price, strike_price - asset_prices + premium_received, premium_received)
    return long_asset_payoff + short_call_payoff

def calculate_married_put_payoff(asset_prices, purchase_price, strike_price, premium_paid):
    # Profit or loss from holding the stock
    stock_payoff = asset_prices - purchase_price
    # Payoff from the put option
    put_payoff = np.maximum(strike_price - asset_prices, 0) - premium_paid
    # The married put payoff is the sum of the stock and put option payoffs
    married_put_payoff = stock_payoff + put_payoff
    return married_put_payoff

# Function to calculate the payoff for a Bull Call Spread option
def calculate_bull_call_spread_payoff(asset_prices, strike_price_long_call, strike_price_short_call, premium_long_call, premium_short_call):
    # Payoff from the long call position
    long_call_payoff = np.maximum(asset_prices - strike_price_long_call, 0) - premium_long_call
    # Payoff from the short call position (negative because it's short)
    short_call_payoff = premium_short_call - np.maximum(asset_prices - strike_price_short_call, 0)
    # The bull call spread payoff is the sum of the long call and short call payoffs
    bull_call_spread_payoff = long_call_payoff + short_call_payoff
    return bull_call_spread_payoff

# Function to calculate the payoff for a Bull Put Spread option
def calculate_bull_put_spread_payoff(asset_prices, strike_price_short_put, strike_price_long_put, premium_short_put, premium_long_put):
    # Payoff from the short put position
    short_put_payoff = premium_short_put - np.maximum(strike_price_short_put - asset_prices, 0)
    # Payoff from the long put position (negative because we're buying it)
    long_put_payoff = np.maximum(strike_price_long_put - asset_prices, 0) - premium_long_put
    # The bull put spread payoff is the sum of the short put and long put payoffs
    bull_put_spread_payoff = short_put_payoff + long_put_payoff
    return bull_put_spread_payoff

# Function to calculate the payoff for a Protective Collar option
def calculate_protective_collar_payoff(asset_prices, purchase_price, strike_price_put, premium_put, strike_price_call, premium_call):
    # Profit or loss from holding the stock
    stock_payoff = asset_prices - purchase_price

    # Payoff from the long put position
    long_put_payoff = np.maximum(strike_price_put - asset_prices, 0) - premium_put

    # Payoff from the short call position (negative because it's short)
    short_call_payoff = premium_call - np.maximum(asset_prices - strike_price_call, 0)

    # The protective collar payoff is the sum of the stock, put, and call payoffs
    protective_collar_payoff = stock_payoff + long_put_payoff + short_call_payoff
    return protective_collar_payoff

# Function to calculate the payoff for a Long Call Butterfly Spread option
def calculate_long_call_butterfly_payoff(asset_prices, strike_price_low, strike_price_mid, strike_price_high, premium_low, premium_mid, premium_high):
    # Buying one low strike call
    long_call_low_payoff = np.maximum(asset_prices - strike_price_low, 0) - premium_low
    # Selling two mid strike calls
    short_call_mid_payoff = 2 * (premium_mid - np.maximum(asset_prices - strike_price_mid, 0))
    # Buying one high strike call
    long_call_high_payoff = np.maximum(asset_prices - strike_price_high, 0) - premium_high

    # Total payoff for the butterfly spread
    butterfly_payoff = long_call_low_payoff + short_call_mid_payoff + long_call_high_payoff
    return butterfly_payoff

# Function to calculate the payoff for an Iron Butterfly option
def calculate_iron_butterfly_payoff(asset_prices, strike_price_put, premium_put, strike_price_call, premium_call, premium_atm, strike_price_atm):
    # Payoff from the long out-of-the-money put
    long_put_payoff = np.maximum(strike_price_put - asset_prices, 0) - premium_put
    # Payoff from the short at-the-money put
    short_atm_put_payoff = premium_atm - np.maximum(strike_price_atm - asset_prices, 0)
    # Payoff from the short at-the-money call
    short_atm_call_payoff = premium_atm - np.maximum(asset_prices - strike_price_atm, 0)
    # Payoff from the long out-of-the-money call
    long_call_payoff = np.maximum(asset_prices - strike_price_call, 0) - premium_call
    # Total payoff for the Iron Butterfly
    iron_butterfly_payoff = long_put_payoff + short_atm_put_payoff + short_atm_call_payoff + long_call_payoff
    return iron_butterfly_payoff

# Function to calculate the payoff for an Iron Condor option
def calculate_iron_condor_payoff(asset_prices, strike_price_put_buy, premium_put_buy, strike_price_put_sell, premium_put_sell, strike_price_call_sell, premium_call_sell, strike_price_call_buy, premium_call_buy):
    # Payoff from the long put
    long_put_payoff = np.maximum(strike_price_put_buy - asset_prices, 0) - premium_put_buy
    # Payoff from the short put
    short_put_payoff = premium_put_sell - np.maximum(strike_price_put_sell - asset_prices, 0)
    # Payoff from the short call
    short_call_payoff = premium_call_sell - np.maximum(asset_prices - strike_price_call_sell, 0)
    # Payoff from the long call
    long_call_payoff = np.maximum(asset_prices - strike_price_call_buy, 0) - premium_call_buy

    # The iron condor payoff is the sum of the individual option payoffs
    iron_condor_payoff = long_put_payoff + short_put_payoff + short_call_payoff + long_call_payoff
    return iron_condor_payoff

# Streamlit app layout
st.title('Options Strategy Visualizer')

# API data fetch
API_KEY = st.secrets["API_KEY"]["key"]
symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "SPY", "QQQ", "DIA", "META", "NFLX", "NVDA", "TSLA", "AMD"]
selected_symbol = st.selectbox("Select Stock Symbol", symbols)

# Fetch stock data
df = get_stock_data(selected_symbol, API_KEY)

st.subheader("Stock Data")
st.write(df.tail())

# Display stock closing prices
fig = px.line(df, x='Date', y='Close', title=f'{selected_symbol} Closing Prices')
st.plotly_chart(fig)

# Option strategy selection
strategies = [
    "Call Option", "Put Option", "Straddle", "Covered Call", "Married Put", 
    "Bull Call Spread", "Bull Put Spread", "Protective Collar", 
    "Long Call Butterfly Spread", "Iron Butterfly", "Iron Condor"
]
selected_strategy = st.selectbox("Select Option Strategy", strategies)

# Collecting inputs for each strategy
if selected_strategy == "Call Option":
    strike = st.number_input("Strike Price")
    premium = st.number_input("Premium Paid")
    payoffs = calculate_call_payoff(df['Close'], strike, premium)

elif selected_strategy == "Put Option":
    strike = st.number_input("Strike Price")
    premium = st.number_input("Premium Paid")
    payoffs = calculate_put_payoff(df['Close'], strike, premium)

elif selected_strategy == "Straddle":
    strike = st.number_input("Strike Price")
    premium = st.number_input("Premium Paid")
    payoffs = calculate_straddle_payoff(df['Close'], strike, premium)

elif selected_strategy == "Covered Call":
    purchase_price = st.number_input("Purchase Price of Asset")
    strike_price = st.number_input("Strike Price")
    premium_received = st.number_input("Premium Received")
    payoffs = calculate_covered_call_payoff(df['Close'], purchase_price, strike_price, premium_received)

elif selected_strategy == "Married Put":
    purchase_price = st.number_input("Purchase Price of Asset")
    strike_price = st.number_input("Strike Price")
    premium_paid = st.number_input("Premium Paid")
    payoffs = calculate_married_put_payoff(df['Close'], purchase_price, strike_price, premium_paid)

elif selected_strategy == "Bull Call Spread":
    strike_price_long_call = st.number_input("Strike Price of Long Call")
    strike_price_short_call = st.number_input("Strike Price of Short Call")
    premium_long_call = st.number_input("Premium Paid for Long Call")
    premium_short_call = st.number_input("Premium Received for Short Call")
    payoffs = calculate_bull_call_spread_payoff(df['Close'], strike_price_long_call, strike_price_short_call, premium_long_call, premium_short_call)

elif selected_strategy == "Bull Put Spread":
    strike_price_short_put = st.number_input("Strike Price of Short Put")
    strike_price_long_put = st.number_input("Strike Price of Long Put")
    premium_short_put = st.number_input("Premium Received for Short Put")
    premium_long_put = st.number_input("Premium Paid for Long Put")
    payoffs = calculate_bull_put_spread_payoff(df['Close'], strike_price_short_put, strike_price_long_put, premium_short_put, premium_long_put)

elif selected_strategy == "Protective Collar":
    purchase_price = st.number_input("Purchase Price of Asset")
    strike_price_put = st.number_input("Strike Price of Long Put")
    premium_put = st.number_input("Premium Paid for Long Put")
    strike_price_call = st.number_input("Strike Price of Short Call")
    premium_call = st.number_input("Premium Received for Short Call")
    payoffs = calculate_protective_collar_payoff(df['Close'], purchase_price, strike_price_put, premium_put, strike_price_call, premium_call)

elif selected_strategy == "Long Call Butterfly Spread":
    strike_price_low = st.number_input("Strike Price of Low Strike Call")
    strike_price_mid = st.number_input("Strike Price of Mid Strike Call")
    strike_price_high = st.number_input("Strike Price of High Strike Call")
    premium_low = st.number_input("Premium Paid for Low Strike Call")
    premium_mid = st.number_input("Premium Received for Mid Strike Call")
    premium_high = st.number_input("Premium Paid for High Strike Call")
    payoffs = calculate_long_call_butterfly_payoff(df['Close'], strike_price_low, strike_price_mid, strike_price_high, premium_low, premium_mid, premium_high)

elif selected_strategy == "Iron Butterfly":
    strike_price_put = st.number_input("Strike Price of Long Put")
    premium_put = st.number_input("Premium Paid for Long Put")
    strike_price_call = st.number_input("Strike Price of Long Call")
    premium_call = st.number_input("Premium Paid for Long Call")
    premium_atm = st.number_input("Premium Received for ATM Options")
    strike_price_atm = st.number_input("Strike Price of ATM Options")
    payoffs = calculate_iron_butterfly_payoff(df['Close'], strike_price_put, premium_put, strike_price_call, premium_call, premium_atm, strike_price_atm)

elif selected_strategy == "Iron Condor":
    strike_price_put_buy = st.number_input("Strike Price of Long Put")
    premium_put_buy = st.number_input("Premium Paid for Long Put")
    strike_price_put_sell = st.number_input("Strike Price of Short Put")
    premium_put_sell = st.number_input("Premium Received for Short Put")
    strike_price_call_sell = st.number_input("Strike Price of Short Call")
    premium_call_sell = st.number_input("Premium Received for Short Call")
    strike_price_call_buy = st.number_input("Strike Price of Long Call")
    premium_call_buy = st.number_input("Premium Paid for Long Call")
    payoffs = calculate_iron_condor_payoff(df['Close'], strike_price_put_buy, premium_put_buy, strike_price_put_sell, premium_put_sell, strike_price_call_sell, premium_call_sell, strike_price_call_buy, premium_call_buy)

# Displaying the payoff plot
st.subheader("Payoff Diagram")
fig, ax = plt.subplots()
ax.plot(df['Close'], payoffs, label='Payoff')
ax.axhline(0, color='black', linewidth=1, linestyle='--')
ax.set_xlabel('Stock Price at Expiration')
ax.set_ylabel('Payoff')
ax.set_title(f'{selected_strategy} Payoff Diagram')
ax.legend()
st.pyplot(fig)
