import os
import requests
import json
from datetime import datetime
from utils import upsert_data
from dotenv import load_dotenv
import OpenDartReader

load_dotenv()

class FinancialsCollector:
    def __init__(self):
        self.api_key = os.getenv("DART_API_KEY")
        if self.api_key:
            self.dart = OpenDartReader(self.api_key)
        else:
            print("Warning: DART_API_KEY not found")
            self.dart = None

    def fetch_financials(self, ticker, year, quarter=0):
        """
        Fetches financial data using OpenDartReader.
        quarter: 0 for Yearly, 1-4 for Quarterly.
        """
        if not self.dart:
            return

        # Mapping quarter to report code
        report_codes = {
            0: "11011", # Business Report (Yearly)
            1: "11013", # 1Q
            2: "11012", # Half-year
            3: "11014"  # 3Q
        }
        
        reprt_code = report_codes.get(quarter, "11011")
        
        print(f"Fetching financials for {ticker} ({year} Q{quarter})...")
        
        try:
            # Get corp_code
            corp_code = self.dart.find_corp_code(ticker)
            if not corp_code:
                print(f"Corp code not found for {ticker}")
                return

            # Fetch Financial Statement
            # fs_div: CFS(Consolidated), OFS(Separate)
            fs = self.dart.finstate(corp_code, year, reprt_code=reprt_code)
            
            if fs is None or fs.empty:
                print(f"No financial data found for {ticker} ({year} Q{quarter})")
                return

            # Initialize fields
            revenue = 0
            op_profit = 0
            net_income = 0
            assets = 0
            liabilities = 0
            equity = 0
            
            # Filter for Consolidated (CFS)
            # If CFS is not available, fallback to OFS? 
            # Usually we want Consolidated.
            fs_cfs = fs[fs['fs_div'] == 'CFS']
            if fs_cfs.empty:
                # Fallback to Separate if Consolidated is missing (e.g. some holding companies or smaller ones)
                # But for Samsung, CFS should exist.
                # Let's try OFS if CFS is empty.
                fs_cfs = fs[fs['fs_div'] == 'OFS']
            
            if fs_cfs.empty:
                 print(f"No Consolidated/Separate data found for {ticker}")
                 return

            # Extract Data
            # Account names can vary slightly, but OpenDart standardizes them mostly.
            # Revenue: 매출액, 수익(매출액)
            # Op Profit: 영업이익, 영업이익(손실)
            # Net Income: 당기순이익, 당기순이익(손실)
            # Assets: 자산총계
            # Liabilities: 부채총계
            # Equity: 자본총계
            
            def get_amount(df, account_names):
                for name in account_names:
                    row = df[df['account_nm'] == name]
                    if not row.empty:
                        amt_str = row.iloc[0]['thstrm_amount']
                        return int(amt_str.replace(',', '')) if amt_str else 0
                return 0

            revenue = get_amount(fs_cfs, ['매출액', '수익(매출액)'])
            op_profit = get_amount(fs_cfs, ['영업이익', '영업이익(손실)'])
            net_income = get_amount(fs_cfs, ['당기순이익', '당기순이익(손실)'])
            assets = get_amount(fs_cfs, ['자산총계'])
            liabilities = get_amount(fs_cfs, ['부채총계'])
            equity = get_amount(fs_cfs, ['자본총계'])

            financial_data = {
                "ticker": ticker,
                "year": year,
                "quarter": quarter,
                "revenue": revenue,
                "op_profit": op_profit,
                "net_income": net_income,
                "assets": assets,
                "liabilities": liabilities,
                "equity": equity,
                "ocf": 0, 
                "is_estimated": False
            }
            
            upsert_data(
                table="financials",
                data=[financial_data],
                conflict_columns=["ticker", "year", "quarter"]
            )
            print(f"Saved financials for {ticker} ({year} Q{quarter})")
            
        except Exception as e:
            print(f"Error fetching financials: {e}")

if __name__ == "__main__":
    collector = FinancialsCollector()
    collector.fetch_financials("005930", 2023, 0)
