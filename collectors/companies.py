import os
import OpenDartReader
import FinanceDataReader as fdr
from datetime import datetime
from utils import upsert_data
from dotenv import load_dotenv

load_dotenv()

class CompanyCollector:
    def __init__(self):
        self.api_key = os.getenv("DART_API_KEY")
        if self.api_key:
            self.dart = OpenDartReader(self.api_key)
        else:
            print("Warning: DART_API_KEY not found in .env")
            self.dart = None

    def collect_and_save(self, ticker):
        print(f"Collecting company info for {ticker}...")
        
        try:
            # 1. Basic Info from OpenDART (Identity)
            # OpenDartReader usually takes corp_code, but can handle ticker if we use the right method or conversion.
            # 'company' method returns basic info including establishment date.
            
            est_dt = None
            listing_dt = None
            corp_name = None
            
            if self.dart:
                try:
                    # OpenDartReader's company() uses 'corp_code' usually. 
                    # We need to find corp_code from ticker first.
                    # self.dart.find_corp_code(ticker) returns corp_code
                    corp_code = self.dart.find_corp_code(ticker)
                    if corp_code:
                        info = self.dart.company(corp_code)
                        if info:
                            # info is a dict
                            corp_name = info.get('corp_name')
                            est_dt = info.get('est_dt') # YYYYMMDD
                            # listing_dt is not always in basic 'company' info, sometimes in other places.
                            # But let's check what we get.
                            # Actually OpenDart 'company' returns: status, message, corp_code, corp_name, corp_name_eng, stock_name, stock_code, ceo_nm, corp_cls, jurir_no, bizr_no, adres, hm_url, ir_url, phn_no, fax_no, induty_code, est_dt, acc_mt
                except Exception as e:
                    print(f"OpenDART fetch failed: {e}")

            # 2. Market Info from FinanceDataReader (Sector, Market Type)
            # This is robust for listed companies.
            df_krx = fdr.StockListing('KRX')
            company_row = df_krx[df_krx['Code'] == ticker]
            
            if company_row.empty:
                print(f"Company {ticker} not found in KRX listing.")
                return

            row = company_row.iloc[0]
            
            # Use KRX data for name if OpenDART failed or to be consistent with market data
            final_name = row['Name']
            market_type = row['Market']
            sector = row.get('Sector', 'Unknown')
            
            # Listing Date from KRX if available
            if 'ListingDate' in row:
                listing_dt = str(row['ListingDate']) # Usually YYYY-MM-DD or datetime
                # Format to YYYYMMDD if needed, or keep as is. Let's keep YYYYMMDD for consistency.
                if hasattr(row['ListingDate'], 'strftime'):
                    listing_dt = row['ListingDate'].strftime('%Y%m%d')
                else:
                    listing_dt = str(row['ListingDate']).replace('-', '')

            # Summary
            summary = f"{final_name} is a {market_type} listed company in the {sector} sector."
            if est_dt:
                summary += f" Established on {est_dt}."
            
            company_data = {
                "ticker": ticker,
                "name": final_name,
                "sector": sector,
                "market_type": market_type,
                "est_dt": est_dt,
                "listing_dt": listing_dt,
                "desc_summary": summary,
                "updated_at": datetime.now()
            }
            
            upsert_data(
                table="companies",
                data=[company_data],
                conflict_columns=["ticker"]
            )
            print(f"Saved company info for {ticker}: {final_name}")
            
        except Exception as e:
            print(f"Error collecting company info: {e}")

if __name__ == "__main__":
    collector = CompanyCollector()
    collector.collect_and_save("005930")
