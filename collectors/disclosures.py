import os
import OpenDartReader
from datetime import datetime, timedelta
from utils import upsert_data
from dotenv import load_dotenv

load_dotenv()

class DisclosuresCollector:
    def __init__(self):
        self.api_key = os.getenv("DART_API_KEY")
        if self.api_key:
            self.dart = OpenDartReader(self.api_key)
        else:
            print("Warning: DART_API_KEY not found")
            self.dart = None

    def fetch_disclosures(self, ticker, days=1095):
        """
        Fetches disclosure list for the past 'days'.
        """
        if not self.dart:
            return

        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
        
        print(f"Fetching disclosures for {ticker} from {start_date} to {end_date}...")
        
        try:
            # OpenDartReader list method
            # Note: OpenDartReader uses 'corp_code' internally but can accept stock code usually if initialized properly.
            # However, it's safer to get the corp_code first or rely on the library's handling.
            # The library handles stock_code -> corp_code conversion automatically if updated.
            
            # Fetch list - Periodic Reports (kind='A') for last 3 years to cover Annual Reports
            # We will filter Quarterly/Semi-annual to 1 year in the loop
            df = self.dart.list(ticker, start=start_date, end=end_date, kind='A')
            
            if df is None or df.empty:
                print(f"No periodic disclosures found for {ticker}")
                return

            disclosures_data = []
            cutoff_1yr = datetime.now().date() - timedelta(days=365)

            for _, row in df.iterrows():
                # Extract relevant fields
                report_nm = row['report_nm']
                rcept_dt_str = row['rcept_dt'] # YYYYMMDD
                rcept_dt = datetime.strptime(rcept_dt_str, "%Y%m%d").date()
                
                # Filtering Logic
                is_annual = "사업보고서" in report_nm
                is_quarterly = "분기보고서" in report_nm or "반기보고서" in report_nm
                
                # 1. Annual Reports: Keep all (since we fetched 3 years)
                # 2. Quarterly/Semi: Keep only if within last 1 year
                if is_quarterly and rcept_dt < cutoff_1yr:
                    continue
                
                # If it's neither (unlikely with kind='A' but possible), skip or keep? 
                # kind='A' is strictly periodic. Let's keep if it matches our keywords.
                if not (is_annual or is_quarterly):
                    continue

                disclosures_data.append({
                    "rcept_no": row['rcept_no'],
                    "ticker": ticker,
                    "report_nm": report_nm,
                    "rcept_dt": rcept_dt,
                    "flr_nm": row['flr_nm'],
                    "url": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={row['rcept_no']}",
                    "summary_body": None
                })
            
            upsert_data(
                table="disclosures",
                data=disclosures_data,
                conflict_columns=["rcept_no"]
            )
            print(f"Saved {len(disclosures_data)} disclosures for {ticker}")
            
        except Exception as e:
            print(f"Error fetching disclosures: {e}")

if __name__ == "__main__":
    collector = DisclosuresCollector()
    collector.fetch_disclosures("005930")
