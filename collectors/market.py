import FinanceDataReader as fdr
from datetime import datetime, timedelta
from utils import upsert_data
import pandas as pd
import numpy as np

class MarketCollector:
    def __init__(self):
        pass

    def fetch_daily_data(self, ticker, days=365):
        """
        Fetches daily market data (OHLCV) for the past 'days'.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        print(f"Fetching market data for {ticker} from {start_date.date()} to {end_date.date()}...")
        
        try:
            # FinanceDataReader
            # Note: KRX tickers are just numbers, but FDR handles them well.
            df = fdr.DataReader(ticker, start_date, end_date)
            
            if df is None or df.empty:
                print(f"No market data found for {ticker}")
                return

            # Calculate Moving Averages
            df['MA5'] = df['Close'].rolling(window=5).mean()
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['MA60'] = df['Close'].rolling(window=60).mean()
            
            # Prepare data for DB
            market_data = []
            for date, row in df.iterrows():
                # Handle NaN values for MAs
                ma5 = row['MA5'] if not pd.isna(row['MA5']) else None
                ma20 = row['MA20'] if not pd.isna(row['MA20']) else None
                ma60 = row['MA60'] if not pd.isna(row['MA60']) else None
                
                market_data.append({
                    "ticker": ticker,
                    "date": date.date(),
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "volume": int(row['Volume']),
                    "ma5": float(ma5) if ma5 else None,
                    "ma20": float(ma20) if ma20 else None,
                    "ma60": float(ma60) if ma60 else None
                })
            
            upsert_data(
                table="market_daily",
                data=market_data,
                conflict_columns=["ticker", "date"]
            )
            print(f"Saved {len(market_data)} market records for {ticker}")
            
        except Exception as e:
            print(f"Error fetching market data: {e}")

if __name__ == "__main__":
    collector = MarketCollector()
    collector.fetch_daily_data("005930")
