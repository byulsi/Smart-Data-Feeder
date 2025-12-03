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

    def fetch_disclosures(self, ticker, days=365):
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
            
            # Fetch list
            df = self.dart.list(ticker, start=start_date, end=end_date)
            
            if df is None or df.empty:
                print(f"No disclosures found for {ticker}")
                return

            disclosures_data = []
            for _, row in df.iterrows():
                # Extract relevant fields
                # Columns: corp_code, corp_name, stock_code, corp_cls, report_nm, rcept_no, flr_nm, rcept_dt, rm
                
                # We need to parse the date properly
                rcept_dt_str = row['rcept_dt'] # YYYYMMDD
                rcept_dt = datetime.strptime(rcept_dt_str, "%Y%m%d").date()
                
                disclosures_data.append({
                    "rcept_no": row['rcept_no'],
                    "ticker": ticker, # Use the ticker we queried with
                    "report_nm": row['report_nm'],
                    "rcept_dt": rcept_dt,
                    "flr_nm": row['flr_nm'],
                    "url": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={row['rcept_no']}", # Construct URL
                    "summary_body": None # We will parse this later in a separate step or Deep Dive
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
