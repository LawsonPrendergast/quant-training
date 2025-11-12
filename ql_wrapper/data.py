import pandas as pd
import yfinance as yf

class OptionChainReader:
    @staticmethod
    def from_csv(path: str) -> pd.DataFrame:
        return pd.read_csv(path)
    
    @staticmethod
    def from_api(ticker: str, expiry: str=None) -> pd.DataFrame:
        '''
        Fetch an option chain for ticker via yfinance.
        If expiry is None \, use the earliest available expiry.
        Returns DataFrame with columns: expiry, strike, type ('C'/'P'), impliedVol'''

        tk = yf.Ticker(ticker.strip().upper())
        exps = tk.options
        if not exps:
            raise ValueError(f"No expirations available for ticker {ticker}")
        if expiry is None:
            expiry = exps[0]
        chain = tk.option_chain(expiry)
        calls = chain.calls.copy()
        calls['type'] = 'C'
        puts = chain.puts.copy()
        puts['type'] = 'P'
        # yfinance option frames do not carry an expiry column; add it explicitly
        calls['expiry'] = expiry
        puts['expiry'] = expiry
        df = pd.concat([calls, puts], ignore_index=True)
        # select and normalize schema
        df = df[['expiry', 'strike', 'type', 'impliedVolatility']].copy()
        df =  df.rename(columns={'impliedVolatility': 'implied_vol'})
        # Coerce numeric types and drop rows with missing values
        df['strike'] = pd.to_numeric(df['strike'], errors='coerce')
        df['implied_vol'] = pd.to_numeric(df['implied_vol'], errors='coerce')
        df = df.dropna(subset=['strike', 'implied_vol'])
        df['expiry'] = pd.to_datetime(df['expiry']).dt.date
        return df