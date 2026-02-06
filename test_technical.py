from utils.technical import fetch_history, calculate_indicators, analyze_buy_signal, analyze_sell_signal

ticker = "TCS"
print(f"Testing Technical Analysis for {ticker}...")

df = fetch_history(ticker)
if not df.empty:
    print(f"Fetched {len(df)} rows.")
    df = calculate_indicators(df)
    print("Indicators calculated.")
    print(df[['Close', 'RSI', 'EMA_50', 'EMA_200']].tail())
    
    buy_analysis = analyze_buy_signal(df)
    print(f"Buy Analysis: {buy_analysis}")
    
    sell_analysis = analyze_sell_signal(df, avg_price=3200) # Assuming bought at 3200
    print(f"Sell Analysis (Avg: 3200): {sell_analysis}")
else:
    print("Failed to fetch data.")
