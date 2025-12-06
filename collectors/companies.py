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
            sector = 'Unknown'
            market_type = 'Unknown'
            final_name = corp_name if corp_name else ticker
            
            try:
                df_krx = fdr.StockListing('KRX')
                company_row = df_krx[df_krx['Code'] == ticker]
                
                if not company_row.empty:
                    row = company_row.iloc[0]
                    final_name = row['Name']
                    market_type = row['Market']
                    sector = row.get('Sector', 'Unknown')
                    
                    # Listing Date from KRX if available
                    if 'ListingDate' in row:
                        listing_dt = str(row['ListingDate'])
                        if hasattr(row['ListingDate'], 'strftime'):
                            listing_dt = row['ListingDate'].strftime('%Y%m%d')
                        else:
                            listing_dt = str(row['ListingDate']).replace('-', '')

                    # Market Cap and Shares
                    market_cap = int(row.get('Marcap', 0))
                    shares_outstanding = int(row.get('Stocks', 0))
            except Exception as e:
                print(f"Warning: FDR market info fetch failed: {e}")
                
            # 3. Fallback: Naver Finance for Sector (if Unknown)
            if sector == 'Unknown':
                try:
                    import requests
                    from bs4 import BeautifulSoup
                    
                    url = f"https://finance.naver.com/item/main.nhn?code={ticker}"
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    res = requests.get(url, headers=headers)
                    soup = BeautifulSoup(res.text, 'html.parser')
                    
                    # Sector is usually in <h4 class="h_sub sub_tit7"> or similar
                    # Actually, it's often in the 'Trade Info' or 'Analysis' section.
                    # A reliable place: <h4 class="h_sub sub_tit7"><span>업종명</span></h4>
                    # But simpler: look for the sector link
                    # <a href="/sise/sise_group_detail.nhn?type=upjong&no=...">SectorName</a>
                    
                    # Try to find the sector link in the 'Trade Compare' section
                    # <div class="section trade_compare"> ... <a href="...">SectorName</a>
                    
                    trade_compare = soup.find('div', {'class': 'section trade_compare'})
                    if trade_compare:
                        h4 = trade_compare.find('h4')
                        if h4:
                            em = h4.find('em')
                            if em:
                                a_tag = em.find('a')
                                if a_tag:
                                    sector = a_tag.text.strip()
                                    print(f"Fetched Sector from Naver: {sector}")
                                    
                except Exception as e:
                    print(f"Naver Finance sector fetch failed: {e}")

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
                "market_cap": locals().get('market_cap', 0),
                "shares_outstanding": locals().get('shares_outstanding', 0),
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

    def resolve_ticker(self, name_or_ticker):
        """
        Resolves a company name to a ticker symbol using FinanceDataReader.
        If input is already a 6-digit ticker, returns it as is.
        """
        # Check if it's a ticker (6 digits)
        if name_or_ticker.isdigit() and len(name_or_ticker) == 6:
            return name_or_ticker
            
        print(f"Resolving ticker for '{name_or_ticker}'...")
        
        # 1. Try OpenDartReader first (More reliable for API key holders)
        if self.dart:
            try:
                # print("Attempting resolution using OpenDartReader...")
                corp_code = self.dart.find_corp_code(name_or_ticker)
                if corp_code:
                    info = self.dart.company(corp_code)
                    if info and info.get('stock_code'):
                        stock_code = info.get('stock_code')
                        if stock_code and stock_code.strip():
                            print(f"Resolved via OpenDart: {stock_code.strip()}")
                            return stock_code.strip()
            except Exception as e:
                print(f"OpenDart resolution failed: {e}")

        # 2. Fallback: FinanceDataReader (KRX)
        # Note: FDR might hang in some environments
        try:
            print("Attempting fallback resolution using FinanceDataReader...")
            # Download stock listing
            df = fdr.StockListing('KRX')
            
            # Search by name
            # Exact match first
            match = df[df['Name'] == name_or_ticker]
            if not match.empty:
                return match.iloc[0]['Code']
                
            # Contains match
            match = df[df['Name'].str.contains(name_or_ticker)]
            if not match.empty:
                found_name = match.iloc[0]['Name']
                found_code = match.iloc[0]['Code']
                print(f"Found '{found_name}' ({found_code})")
                return found_code
                
        except Exception as e:
            print(f"FinanceDataReader resolution failed: {e}")

        print(f"Could not resolve ticker for '{name_or_ticker}'")
        return None

    def fetch_shareholders(self, ticker):
        """
        Fetches major shareholders using OpenDART.
        """
        if not self.dart:
            return

        print(f"Fetching shareholders for {ticker}...")
        try:
            # OpenDartReader's major_shareholders
            # Note: OpenDartReader might not have a direct wrapper for 'major_shareholders' in all versions.
            # If it does, it's usually .major_shareholders(corp_code)
            # Let's check if we can use it. If not, we might need to use .list() with specific code?
            # Actually, OpenDartReader has `major_shareholders`.
            
            corp_code = self.dart.find_corp_code(ticker)
            if not corp_code:
                return

            df = self.dart.major_shareholders(corp_code)
            if df is None or df.empty:
                print(f"No shareholder data found for {ticker}")
                return

            shareholders_data = []

            for _, row in df.iterrows():
                # Columns based on debug output: 
                # ['rcept_no', 'rcept_dt', 'corp_code', 'corp_name', 'report_tp', 'repror', 'stkqy', 'stkqy_irds', 'stkrt', 'stkrt_irds', 'ctr_stkqy', 'ctr_stkrt', 'report_resn']
                
                name = row.get('repror', '')
                # Rel type is not explicitly provided in this API response, defaulting to 'Major Shareholder'
                rel_type = '주요주주' 
                
                count_str = str(row.get('stkqy', '0'))
                ratio_str = str(row.get('stkrt', '0'))
                
                # Clean numbers
                try:
                    count = int(count_str.replace(',', ''))
                    ratio = float(ratio_str.replace(',', ''))
                except:
                    count = 0
                    ratio = 0.0
                
                if name:
                    shareholders_data.append({
                        "ticker": ticker,
                        "holder_name": name,
                        "rel_type": rel_type,
                        "share_count": count,
                        "share_ratio": ratio
                    })

            if shareholders_data:
                upsert_data(
                    table="shareholders",
                    data=shareholders_data,
                    conflict_columns=["ticker", "holder_name"]
                )
                print(f"Saved {len(shareholders_data)} shareholders for {ticker}")

        except Exception as e:
            print(f"Error fetching shareholders: {e}")

if __name__ == "__main__":
    collector = CompanyCollector()
    # Test resolution
    # print(collector.resolve_ticker("삼성전자"))
    collector.collect_and_save("005930")
    collector.fetch_shareholders("005930")
