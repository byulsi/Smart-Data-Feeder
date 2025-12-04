import os
import re
import OpenDartReader
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

def debug_segments(ticker):
    api_key = os.getenv("DART_API_KEY")
    if not api_key:
        print("DART_API_KEY not found")
        return

    dart = OpenDartReader(api_key)
    
    # Get recent annual/quarterly report
    print(f"Fetching recent reports for {ticker}...")
    df = dart.list(ticker, kind='A', start='20240101', end='20251231')
    
    if df is None or df.empty:
        print("No reports found.")
        return
        
    # Pick the first one (latest)
    target_report = df.iloc[0]
    rcept_no = target_report['rcept_no']
    report_nm = target_report['report_nm']
    print(f"Target Report: {report_nm} ({rcept_no})")
    
    try:
        # Fetch full XML
        print("\n--- Fetching Document XML ---")
        xml_text = dart.document(rcept_no)
        
        if not xml_text:
            print("Failed to fetch document XML.")
            return

        # Find "4. 매출 및 수주상황" section
        # Note: The section numbering might vary ("4.", "IV.", etc.) but "매출 및 수주상황" is standard.
        # Also need to be careful about "II. 사업의 내용" context.
        
        # Strategy: Find "매출 및 수주상황" and then look for the first table after it that contains "매출액" and "부문".
        
        # 1. Narrow down to "II. 사업의 내용" first to avoid other sections
        start_marker = "II. 사업의 내용"
        end_marker = "III. 재무에 관한 사항"
        
        start_idx = xml_text.find(start_marker)
        end_idx = xml_text.find(end_marker)
        
        if start_idx == -1 or end_idx == -1:
            print("Could not find 'Business Overview' section.")
            return
            
        business_section = xml_text[start_idx:end_idx]
        print(f"Business Section Length: {len(business_section)}")
        
        # 2. Find "매출 및 수주상황" within this section
        sales_marker = "매출 및 수주상황"
        sales_idx = business_section.find(sales_marker)
        
        if sales_idx == -1:
            print(f"Could not find '{sales_marker}' in Business Overview.")
            return
            
        print(f"Found '{sales_marker}' at index {sales_idx}")
        
        # 3. Look for tables after this marker
        sales_section_text = business_section[sales_idx:]
        
        # Use BeautifulSoup to parse tables
        soup = BeautifulSoup(sales_section_text, 'html.parser')
        tables = soup.find_all('table')
        
        print(f"Found {len(tables)} tables in Sales Section.")
        
        target_table = None
        for i, table in enumerate(tables):
            # Check headers
            text = table.get_text()
            if "부문" in text and "매출액" in text and "비중" in text:
                print(f"Table {i} looks like a candidate.")
                target_table = table
                break
        
        if target_table:
            print("\n--- Extracted Table Data ---")
            rows = target_table.find_all('tr')
            for row in rows:
                cols = row.find_all(['td', 'th'])
                cols_text = [ele.get_text(strip=True) for ele in cols]
                print(cols_text)
                
            # Try to parse rows into structured data
            # Expected columns: 부문 | ... | 매출액 | 비중
            # Samsung table structure usually: [부문, 주요제품, 매출액, 비중] or similar.
        else:
            print("No matching table found.")
            # Print first table to see what it looks like
            if tables:
                print("First table content:")
                print(tables[0].get_text()[:200])

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_segments("005930")
