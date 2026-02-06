import pandas as pd
import io

def load_stock_list(file) -> list:
    """
    Reads a file (CSV or Excel) and returns a list of stock symbols.
    Expects a column named 'Symbol' or 'Ticker'.
    """
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file)
        else:
            return []
        
        # Normalize column names to uppercase
        df.columns = [c.strip() for c in df.columns]
        
        possible_names = ['Symbol', 'Ticker', 'Stock', 'SYMBOL', 'TICKER']
        target_col = None
        for col in df.columns:
            if col in possible_names:
                target_col = col
                break
        
        if target_col:
            # Ensure symbols are strings and stripped of whitespace
            return df[target_col].astype(str).str.strip().tolist()
        else:
            return []
    except Exception as e:
        print(f"Error loading file: {e}")
        return []

def load_holdings(file) -> pd.DataFrame:
    """
    Reads a file (CSV or Excel) and returns a DataFrame with 'Symbol' and 'Avg Price'.
    """
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file)
        else:
            return pd.DataFrame()
            
        # Normalize: Symbol and Avg Price
        df.columns = [c.strip() for c in df.columns]
        
        # Simple mapping for flexibility
        rename_map = {}
        for col in df.columns:
            if col.lower() in ['symbol', 'ticker', 'stock']:
                rename_map[col] = 'Symbol'
            if col.lower() in ['avg price', 'buy price', 'cost', 'average']:
                rename_map[col] = 'Avg Price'
        
        df = df.rename(columns=rename_map)
        
        if 'Symbol' in df.columns and 'Avg Price' in df.columns:
            df['Symbol'] = df['Symbol'].astype(str).str.strip()
            df['Avg Price'] = pd.to_numeric(df['Avg Price'], errors='coerce')
            return df[['Symbol', 'Avg Price']].dropna()
        else:
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error loading holdings: {e}")
        return pd.DataFrame()
