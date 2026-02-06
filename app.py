import streamlit as st
import pandas as pd
from utils.data_loader import load_stock_list, load_holdings
from utils.screener import get_fundamentals, score_stock
from utils.technical import fetch_history, calculate_indicators, analyze_buy_signal, analyze_sell_signal
import time
import plotly.graph_objects as go

st.set_page_config(page_title="Quant Trader", layout="wide")

st.title("Manjunath's Algo-Trading Assistant 📈")

st.sidebar.header("Data Upload")

# Tabs
tab1, tab2 = st.tabs(["🚀 Stock Discovery (Buy)", "💼 Portfolio Review (Sell/Hold)"])

# --- Tab 1: Stock Discovery ---
with tab1:
    st.header("Stock Discovery & Fundamental Analysis")
    uploaded_watchlist = st.sidebar.file_uploader("Upload Watchlist (CSV/Excel)", type=['csv', 'xlsx'])
    
    if uploaded_watchlist:
        tickers = load_stock_list(uploaded_watchlist)
        st.write(f"Loaded {len(tickers)} stocks from watchlist.")
        
        if st.button("Run Analysis", key="run_buy"):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, ticker in enumerate(tickers):
                status_text.text(f"Analyzing {ticker}...")
                
                # 1. Fundamental Analysis
                fund_data = get_fundamentals(ticker)
                
                if fund_data:
                    is_strong, status_reason = score_stock(fund_data)
                    
                    tech_signal = "N/A"
                    tech_reason = status_reason
                    latest_price = fund_data.get('Current Price', 0)
                    rsi = "N/A"
                    
                    if is_strong:
                        # 2. Technical Analysis (Only for strong stocks)
                        hist_data = fetch_history(ticker)
                        if not hist_data.empty:
                            hist_data = calculate_indicators(hist_data)
                            buy_signal = analyze_buy_signal(hist_data)
                            
                            tech_signal = buy_signal['Signal']
                            tech_reason = buy_signal['Reason']
                            latest_price = buy_signal['Latest_Close']
                            rsi = buy_signal['RSI']
                    
                    row = {
                        'Symbol': ticker,
                        'Status': 'Selected' if is_strong else 'Rejected',
                        'Reason': tech_reason,
                        'Fundamental Score': 'Pass' if is_strong else 'Fail',
                        'Market Cap': fund_data.get('Market Cap'),
                        'P/E': fund_data.get('Stock P/E'),
                        'ROE': fund_data.get('ROE'),
                        'Tech Signal': tech_signal,
                        'Latest Price': latest_price,
                        'RSI': rsi
                    }
                    results.append(row)
                
                progress_bar.progress((i + 1) / len(tickers))
                
            status_text.text("Analysis Complete!")
            
            if results:
                df_results = pd.DataFrame(results)
                
                def color_status(val):
                    color = 'green' if val == 'Selected' else 'red'
                    return f'color: {color}'
                    
                st.dataframe(df_results.style.applymap(color_status, subset=['Status']))
                
                # Highlight Buy Recommendations
                buys = df_results[df_results['Tech Signal'].isin(['Buy', 'Strong Buy'])]
                if not buys.empty:
                    st.success(f"Recommended Buys: {len(buys)}")
                    st.dataframe(buys)
                else:
                    selected_count = df_results[df_results['Status'] == 'Selected'].shape[0]
                    if selected_count > 0:
                        st.warning("Stocks passed fundamental checks but have no Buy signal.")
                    else:
                        st.warning("No stocks passed the Fundamental filters.")
            else:
                st.warning("No data retrieved.")

# --- Tab 2: Portfolio Review ---
with tab2:
    st.header("Portfolio Sell/Hold Analysis")
    uploaded_portfolio = st.sidebar.file_uploader("Upload Portfolio (CSV/Excel)", type=['csv', 'xlsx'])
    
    if uploaded_portfolio:
        portfolio = load_holdings(uploaded_portfolio)
        st.write(f"Loaded {len(portfolio)} holdings.")
        st.dataframe(portfolio.head())
        
        if st.button("Run Portfolio Check", key="run_sell"):
            sell_results = []
            progress_bar_sell = st.progress(0)
            
            for i, row in portfolio.iterrows():
                ticker = row['Symbol']
                avg_price = row['Avg Price']
                
                hist_data = fetch_history(ticker)
                if not hist_data.empty:
                    hist_data = calculate_indicators(hist_data)
                    sell_signal = analyze_sell_signal(hist_data, avg_price)
                    
                    res_row = {
                        'Symbol': ticker,
                        'Avg Price': avg_price,
                        'Current Price': sell_signal['Latest_Close'],
                        'RSI': sell_signal['RSI'],
                        'Action': sell_signal['Signal'],
                        'Reason': sell_signal['Reason']
                    }
                    sell_results.append(res_row)
                
                progress_bar_sell.progress((i + 1) / len(portfolio))
            
            if sell_results:
                df_sell = pd.DataFrame(sell_results)
                
                # Styling
                def color_action(val):
                    color = 'red' if val == 'Sell' else 'green'
                    return f'color: {color}'
                
                st.dataframe(df_sell.style.applymap(color_action, subset=['Action']))
                
                sells = df_sell[df_sell['Action'] == 'Sell']
                if not sells.empty:
                    st.error(f"Action Required: Sell {len(sells)} stocks")
                    st.dataframe(sells)
                else:
                    st.success("Portfolio looks safe directly. Hold all positions.")
