import os
import requests
import json
from datetime import datetime
from utils import upsert_data
from dotenv import load_dotenv

load_dotenv()

class FinancialsCollector:
    def __init__(self):
        self.api_key = os.getenv("FSC_API_KEY")
        self.base_url = "http://apis.data.go.kr/1160100/service/GetFinaStatInfoService_V2/getSummFinaStat_V2"

    def fetch_financials(self, ticker, year, quarter=0):
        """
        Fetches financial data.
        quarter: 0 for Yearly, 1-4 for Quarterly.
        """
        if not self.api_key:
            print("Warning: FSC_API_KEY not found")
            return

        # Note: FSC API parameters might differ. 
        # Usually 'bsns_year' (Business Year), 'reprt_code' (Report Code: 11011=Business Report, etc.)
        
        # Mapping quarter to report code
        report_codes = {
            0: "11011", # Business Report (Yearly)
            1: "11013", # 1Q
            2: "11012", # Half-year
            3: "11014"  # 3Q
        }
        
        reprt_code = report_codes.get(quarter, "11011")

        params = {
            "serviceKey": self.api_key,
            "numOfRows": "100",
            "pageNo": "1",
            "resultType": "json",
            "crno": "", # Need to map Ticker -> CRNO if API requires CRNO
            "bsns_year": str(year),
            "reprt_code": reprt_code
        }
        
        print(f"Fetching financials for {ticker} ({year} Q{quarter})...")
        
        # Placeholder for API call
        # response = requests.get(self.base_url, params=params)
        
        # Mock data for MVP structure
        financial_data = {
            "ticker": ticker,
            "year": year,
            "quarter": quarter,
            "revenue": 100000000000,
            "op_profit": 10000000000,
            "net_income": 8000000000,
            "assets": 500000000000,
            "liabilities": 200000000000,
            "equity": 300000000000,
            "ocf": 15000000000,
            "is_estimated": False
        }
        
        upsert_data(
            table="financials",
            data=[financial_data],
            conflict_columns=["ticker", "year", "quarter"]
        )
        print(f"Saved financials for {ticker} ({year} Q{quarter})")

if __name__ == "__main__":
    collector = FinancialsCollector()
    collector.fetch_financials("005930", 2023, 0)
