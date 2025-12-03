import os
import pandas as pd
from utils import get_db_connection

class CsvGenerator:
    def __init__(self, ticker):
        self.ticker = ticker
        self.conn = get_db_connection()

    def generate_chart_csv(self, output_dir="output"):
        """Generates [Ticker]_Chart.csv"""
        query = """
            SELECT date, open, high, low, close, volume, ma5, ma20, ma60
            FROM market_daily 
            WHERE ticker = %s 
            ORDER BY date ASC
        """
        df = pd.read_sql(query, self.conn, params=(self.ticker,))
        
        if df.empty:
            print(f"No market data found for {self.ticker}")
            return

        os.makedirs(output_dir, exist_ok=True)
        output_path = f"{output_dir}/{self.ticker}_Chart.csv"
        df.to_csv(output_path, index=False)
        print(f"Generated CSV for {self.ticker} at {output_path}")

if __name__ == "__main__":
    generator = CsvGenerator("005930")
    generator.generate_chart_csv()
