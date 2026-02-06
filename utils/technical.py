import yfinance as yf
import pandas as pd
import ta

def fetch_history(ticker: str, period='1y') -> pd.DataFrame:
    """
    Fetches historical data for a ticker using yfinance.
    Appends '.NS' if not present (assuming NSE for Indian context based on Screener.in usage).
    """
    if not ticker.endswith('.NS') and not ticker.endswith('.BO'):
        ticker += '.NS'
    
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        if df.empty:
            return pd.DataFrame()
        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds technical indicators to the DataFrame.
    """
    if df.empty:
        return df
    
    df = df.copy()
    
    # RSI
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    
    # EMAs
    df['EMA_50'] = ta.trend.EMAIndicator(df['Close'], window=50).ema_indicator()
    df['EMA_200'] = ta.trend.EMAIndicator(df['Close'], window=200).ema_indicator()
    
    # MACD
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_Signal'] = macd.macd_signal()
    
    return df

def analyze_buy_signal(df: pd.DataFrame) -> dict:
    """
    Analyzes the latest data point for buy signals.
    """
    if df.empty or len(df) < 200:
        return {'Signal': 'Insufficient Data', 'Reason': 'Not enough data'}
    
    latest = df.iloc[-1]
    
    signal = 'Neutral'
    reasons = []
    
    # RSI Oversold
    if latest['RSI'] < 30:
        signal = 'Strong Buy'
        reasons.append('RSI Oversold (<30)')
    elif latest['RSI'] < 40:
        signal = 'Buy'
        reasons.append('RSI Approaching Oversold')
        
    # Golden Cross (Need to check recent history, simplified here to current state)
    if latest['EMA_50'] > latest['EMA_200']:
        reasons.append('Trend is Bullish (EMA50 > EMA200)')
    else:
        reasons.append('Trend is Bearish (EMA50 < EMA200)')
        
    if latest['MACD'] > latest['MACD_Signal']:
        if signal == 'Neutral': signal = 'Buy'
        reasons.append('MACD Bullish Crossover')
        
    return {'Signal': signal, 'Reason': ', '.join(reasons), 'Latest_Close': latest['Close'], 'RSI': latest['RSI']}

def analyze_sell_signal(df: pd.DataFrame, avg_price: float) -> dict:
    """
    Analyzes for Sell or Hold signals based on technicals and avg price.
    """
    if df.empty:
        return {'Signal': 'Unknown', 'Reason': 'No Data'}
        
    latest = df.iloc[-1]
    current_price = latest['Close']
    
    signal = 'Hold'
    reasons = []
    
    # Profit/Loss
    pnl_pct = ((current_price - avg_price) / avg_price) * 100
    reasons.append(f"PnL: {pnl_pct:.2f}%")
    
    # RSI Overbought
    if latest['RSI'] > 70:
        signal = 'Sell'
        reasons.append('RSI Overbought (>70)')
        
    # Stop Loss (e.g., -10%)
    if pnl_pct < -10:
        signal = 'Sell'
        reasons.append('Stop Loss Hit (-10%)')
        
    # Trend Breakdown
    if latest['EMA_50'] < latest['EMA_200']:
        reasons.append('Trend Bearish (EMA50 < EMA200)')
        
    # MACD Bearish
    if latest['MACD'] < latest['MACD_Signal']:
        reasons.append('MACD Bearish')
        
    return {'Signal': signal, 'Reason': ', '.join(reasons), 'Latest_Close': current_price, 'RSI': latest['RSI']}
