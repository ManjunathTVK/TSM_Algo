from utils.screener import get_fundamentals, score_stock

tickers = ['TCS', 'INFY']
for ticker in tickers:
    print(f"Fetching data for {ticker}...")
    data = get_fundamentals(ticker)
    if data:
        print(f"Data for {ticker}: {data}")
        is_good, reason = score_stock(data)
        print(f"Is {ticker} a good buy? {is_good} (Reason: {reason})")
    else:
        print(f"Failed to fetch data for {ticker}")
    print("-" * 20)
