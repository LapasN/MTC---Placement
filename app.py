import requests
import pandas as pd
import streamlit as st

def get_underlying_asset_price(symbol, API_KEY):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}"
    response = requests.get(url)
    
    try:
        response.raise_for_status()
        data = response.json()
        
        if 'Time Series (Daily)' not in data:
            st.error("Data not available for this symbol or API call limit reached.")
            return None
        
        daily_data = data['Time Series (Daily)']
        df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close'])
        
        for date, values in daily_data.items():
            row = {'Date': date, 'Open': float(values['1. open']), 'High': float(values['2. high']),
                   'Low': float(values['3. low']), 'Close': float(values['4. close'])}
            df = df.append(row, ignore_index=True)
        
        df['Date'] = pd.to_datetime(df['Date'])
        df.sort_values('Date', inplace=True, ascending=False)  # Sort descending to get the most recent date first
        
        most_recent_close = df.iloc[0]['Close']  # Get the most recent closing price
        return most_recent_close
    
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        st.error(f"Request error occurred: {req_err}")
    except KeyError as key_err:
        st.error(f"Key error: {key_err}")
    except Exception as err:
        st.error(f"An error occurred: {err}")

    return None

# Example usage
API_KEY = st.secrets["API_KEY"]["key"]
symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "SPY", "QQQ", "DIA", "META", "NFLX", "NVDA", "TSLA", "AMD"]

# Streamlit app layout
st.title('Options Strategy Visualizer')

selected_symbol = st.selectbox("Select Stock Symbol", symbols)

if st.button("Fetch Data"):
    stock_data = get_underlying_asset_price(selected_symbol, API_KEY)
    if stock_data:
        st.write(f"Most recent close price for {selected_symbol}: ${stock_data:.2f}")
    else:
        st.write("Failed to fetch data")

# Strategy selection
strategy = st.selectbox("Select Strategy", ["Call", "Put", "Straddle", "Covered Call", "Married Put","Bull Call Spread","Bull Put Spread",
                                            "Protective Collar","Long Call Butterfly Spread","Iron Butterfly","Iron Condor"])

# Strategy parameters
expiration = st.date_input('Expiration Date', key=f'expiry_{strategy}')
asset_price = st.number_input('Underlying Asset Price', value=stock_data if stock_data else 0.0, key=f'asset_price_{strategy}')
premium = st.number_input('Premium',value=10, key=f'premium_{strategy}')
strike_price = st.number_input('Strike Price', value= asset_price if stock_data else 0.0, key=f'strike_{strategy}')

# Additional strategy-specific inputs
if strategy == "Covered Call":
    purchase_price = st.number_input('Purchase Price of Underlying Asset', value=100.0, key='purchase_price')
elif strategy == "Married Put":
    purchase_price = st.number_input('Purchase Price of Underlying Asset', value=100.0, key='purchase_price')
    premium_paid = st.number_input('Premium Paid for Put Option', value=10.0, key='premium_paid')
elif strategy == "Straddle":
    strike_price = st.number_input('Strike Price for Both Call and Put', min_value=0, value=100, key='strike_price_straddle')
    premium_call = st.number_input('Premium Paid for Call Option', min_value=0.0, value=5.0, key='premium_call_straddle')
    premium_put = st.number_input('Premium Paid for Put Option', min_value=0.0, value=5.0, key='premium_put_straddle')
elif strategy == "Bull Call Spread":
    strike_price_long_call = st.number_input('Strike Price for Long Call', min_value=0, value=100, key='strike_price_long_call')
    premium_long_call = st.number_input('Premium for Long Call', min_value=0.0, value=10.0, key='premium_long_call')
    strike_price_short_call = st.number_input('Strike Price for Short Call', min_value=0, value=110, key='strike_price_short_call')
    premium_short_call = st.number_input('Premium for Short Call', min_value=0.0, value=5.0, key='premium_short_call')
elif strategy == "Bull Put Spread":
    strike_price_short_put = st.number_input('Strike Price for Short Put', min_value=0, value=100, key='strike_price_short_put')
    premium_short_put = st.number_input('Premium for Short Put', min_value=0.0, value=10.0, key='premium_short_put')
    strike_price_long_put = st.number_input('Strike Price for Long Put', min_value=0, value=90, key='strike_price_long_put')
    premium_long_put = st.number_input('Premium for Long Put', min_value=0.0, value=5.0, key='premium_long_put')
elif strategy == "Protective Collar":
    purchase_price = st.number_input('Purchase Price of Underlying Asset', value=100.0, key='purchase_price_collar')
    strike_price_put = st.number_input('Strike Price for Long Put', min_value=0, value=95, key='strike_price_put')
    premium_put = st.number_input('Premium for Long Put', min_value=0.0, value=5.0, key='premium_put')
    strike_price_call = st.number_input('Strike Price for Short Call', min_value=0, value=110, key='strike_price_call')
    premium_call = st.number_input('Premium for Short Call', min_value=0.0, value=5.0, key='premium_call')
elif strategy == "Long Call Butterfly Spread":
    strike_price_low = st.number_input('Strike Price for Low Call', min_value=0, value=90, key='strike_price_low')
    premium_low = st.number_input('Premium for Low Call', min_value=0.0, value=3.0, key='premium_low')
    strike_price_mid = st.number_input('Strike Price for Mid Call', min_value=0, value=100, key='strike_price_mid')
    premium_mid = st.number_input('Premium for Mid Call', min_value=0.0, value=4.0, key='premium_mid')
    strike_price_high = st.number_input('Strike Price for High Call', min_value=0, value=110, key='strike_price_high')
    premium_high = st.number_input('Premium for High Call', min_value=0.0, value=8.0, key='premium_high')
elif strategy == "Iron Butterfly":
    strike_price_atm = st.number_input('Strike Price for ATM Options', min_value=0, value=100, key='strike_price_atm')
    premium_atm = st.number_input('Premium for ATM Options', min_value=0.0, value=10.0, key='premium_atm')
    strike_price_otm_put = st.number_input('Strike Price for OTM Put', min_value=0, value=90, key='strike_price_otm_put')
    premium_otm_put = st.number_input('Premium for OTM Put', min_value=0.0, value=10.0, key='premium_otm_put')
    strike_price_otm_call = st.number_input('Strike Price for OTM Call', min_value=0, value=110, key='strike_price_otm_call')
    premium_otm_call = st.number_input('Premium for OTM Call', min_value=0.0, value=3.0, key='premium_otm_call')
elif strategy == "Iron Condor":
    strike_price_put_buy = st.number_input('Strike Price for Buy Put', min_value=0, value=80, key='strike_price_put_buy')
    premium_put_buy = st.number_input('Premium for Buy Put', min_value=0.0, value=1.0, key='premium_put_buy')
    strike_price_put_sell = st.number_input('Strike Price for Sell Put', min_value=0, value=90, key='strike_price_put_sell')
    premium_put_sell = st.number_input('Premium for Sell Put', min_value=0.0, value=2.0, key='premium_put_sell')
    strike_price_call_sell = st.number_input('Strike Price for Sell Call', min_value=0, value=110, key='strike_price_call_sell')
    premium_call_sell = st.number_input('Premium for Sell Call', min_value=0.0, value=2.0, key='premium_call_sell')
    strike_price_call_buy = st.number_input('Strike Price for Buy Call', min_value=0, value=120, key='strike_price_call_buy')
    premium_call_buy = st.number_input('Premium for Buy Call', min_value=0.0, value=1.0, key='premium_call_buy')

if st.button("Calculate Strategy"):
    st.write("Calculating strategy payoff... (implementation needed)")
