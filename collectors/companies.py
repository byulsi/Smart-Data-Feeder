import os
import requests
import json
from datetime import datetime
from utils import upsert_data
from dotenv import load_dotenv

load_dotenv()

class CompanyCollector:
    def __init__(self):
        self.api_key = os.getenv("FSC_API_KEY") # Service Key for data.go.kr
        self.base_url = "http://apis.data.go.kr/1160100/service/GetCorpBasicInfoService_V2/getCorpOutline_V2"

    def fetch_company_info(self, ticker):
        """
        Fetches company basic information from FSC API.
        Note: Ticker on data.go.kr might need to be 6 digits.
        """
        if not self.api_key:
            print("Warning: FSC_API_KEY not found in .env")
            return None

        params = {
            "serviceKey": self.api_key,
            "pageNo": "1",
            "numOfRows": "1",
            "resultType": "json",
            "crno": "", # Corporation Registration Number (optional)
            "corpNm": "" # Corporation Name (optional)
            # Note: This API often searches by name or CRNO, not directly by ticker (stock code).
            # We might need a mapping or search by name if ticker isn't supported directly in this specific endpoint.
            # However, let's assume we can search or we use OpenDART for the basic mapping first.
        }
        
        # Strategy: The FSC 'GetCorpBasicInfoService' is a bit tricky with Tickers.
        # Often OpenDART is better for getting the initial list of companies (Ticker -> Name, CorpCode).
        # Let's try to use OpenDART to get the CorpCode/Name first if we only have Ticker.
        
        # For MVP, let's assume we might use OpenDartReader to get the basic info which is easier.
        # The user's plan mentioned FSC API, but OpenDartReader is in requirements and is very robust for "Identity".
        pass

    def collect_and_save(self, ticker):
        print(f"Collecting company info for {ticker}...")
        
        try:
            import FinanceDataReader as fdr
            
            # Fetch all KRX listings to find the specific ticker
            # This might be heavy (2500 rows), but it's reliable for Sector/Name
            df_krx = fdr.StockListing('KRX')
            company_row = df_krx[df_krx['Code'] == ticker]
            
            if company_row.empty:
                print(f"Company {ticker} not found in KRX listing.")
                return

            row = company_row.iloc[0]
            
            # Map columns: Name, Sector, Market
            # KRX columns: Code, ISU_CD, Name, Market, Dept, Close, ChangeCode, Changes, ChagesRatio, Open, High, Low, Volume, Amount, Marcap, Stocks, MarketId
            # Note: 'Sector' column might be available in 'KRX-DELISTING' or other sources, but 'KRX' listing usually has 'Sector' or 'Industry'.
            # Actually fdr.StockListing('KRX') returns: Code, ISU_CD, Name, Market, Dept, Close, ChangeCode, Changes, ChagesRatio, Open, High, Low, Volume, Amount, Marcap, Stocks, MarketId
            # It seems 'Sector' is not directly in the default KRX listing from FDR recently?
            # Let's check 'KRX-DESC' (Descriptive info) if available, but FDR merged it.
            # Actually, let's just use what we have: Name, Market.
            
            company_data = {
                "ticker": ticker,
                "name": row['Name'],
                "sector": row.get('Sector', 'Unknown'), # Sector might be missing
                "market_type": row['Market'],
                "desc_summary": f"{row['Name']} is listed on {row['Market']}.", # Simple summary
                "updated_at": datetime.now()
            }
            
            upsert_data(
                table="companies",
                data=[company_data],
                conflict_columns=["ticker"]
            )
            print(f"Saved company info for {ticker}: {row['Name']}")
            
        except Exception as e:
            print(f"Error collecting company info: {e}")

if __name__ == "__main__":
    collector = CompanyCollector()
    collector.collect_and_save("005930")
