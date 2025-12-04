import os
import requests
import json
from dotenv import load_dotenv
import OpenDartReader

load_dotenv()

def debug_financials(ticker, year, quarter=0):
    api_key = os.getenv("FSC_API_KEY")
    dart_api_key = os.getenv("DART_API_KEY")
    
    print(f"FSC_API_KEY: {api_key[:5]}...")
    print(f"DART_API_KEY: {dart_api_key[:5]}...")
    
    # Get CRNO
    crno = None
    if dart_api_key:
        dart = OpenDartReader(dart_api_key)
        corp_code = dart.find_corp_code(ticker)
        print(f"Corp Code for {ticker}: {corp_code}")
        if corp_code:
            info = dart.company(corp_code)
            # print(f"Company Info: {info}")
            crno = info.get('jurir_no')
            print(f"CRNO: {crno}")

    if not crno:
        print("CRNO not found.")
        return

    # Try OpenDartReader finstate
    print("\n--- OpenDartReader finstate ---")
    if dart_api_key:
        try:
            dart = OpenDartReader(dart_api_key)
            # finstate(corp_code, bsns_year, reprt_code='11011')
            # 11011: Business Report (Annual)
            fs = dart.finstate(corp_code, 2023, reprt_code='11011')
            if fs is not None and not fs.empty:
                # Filter for Consolidated (fs_div='CFS') and Income Statement (sj_div='IS') or CIS (Comprehensive Income)
                # fs_div: CFS(연결), OFS(별도)
                # sj_div: BS(재무상태표), IS(손익계산서), CIS(포괄손익계산서)
                
                # Look for Net Income
                net_income_rows = fs[(fs['fs_div']=='CFS') & (fs['account_nm'].str.contains('당기순이익'))]
                print("OpenDART Net Income Rows:")
                if not net_income_rows.empty:
                    print(net_income_rows[['sj_nm', 'account_nm', 'thstrm_amount']])
                else:
                    print("No Net Income row found.")
                    print("Columns:", fs.columns)
                    print(fs.head())
            else:
                print("OpenDART finstate returned empty.")
        except Exception as e:
            print(f"OpenDART Error: {e}")

if __name__ == "__main__":
    debug_financials("005930", 2023)
