import re
from bs4 import BeautifulSoup

class TextParser:
    def __init__(self):
        pass

    def parse_rnd_expenses(self, html_content):
        """
        Extracts R&D expenses from the HTML content.
        Looks for tables containing '연구개발비' or '경상연구개발비'.
        Returns the total R&D expense as an integer, or 0 if not found.
        """
        if not html_content:
            return 0
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all tables
        tables = soup.find_all('table')
        
        for table in tables:
            text = table.get_text()
            if '연구개발비' in text or '경상연구개발비' in text:
                # This table likely contains R&D data
                # Try to find the 'Total' or '계' row, or the specific '연구개발비' row
                
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    row_text = [col.get_text(strip=True) for col in cols]
                    
                    # Check if this row is about R&D expenses
                    # Common patterns: "연구개발비 계", "합계", "총계" inside a table that has "연구개발비" header
                    # Or a row specifically named "연구개발비"
                    
                    header_found = False
                    value_found = 0
                    
                    for i, cell_text in enumerate(row_text):
                        if '계' in cell_text or '합계' in cell_text or '연구개발비' in cell_text:
                            # Look for numbers in subsequent columns
                            for j in range(i + 1, len(row_text)):
                                val_text = row_text[j].replace(',', '').strip()
                                # Handle parenthesis for negative numbers (though R&D is usually positive)
                                if val_text.startswith('(') and val_text.endswith(')'):
                                    val_text = '-' + val_text[1:-1]
                                    
                                if val_text.replace('-', '').isdigit():
                                    try:
                                        val = int(val_text)
                                        
                                        # Unit Detection
                                        unit_mult = 1
                                        text_lower = text.lower()
                                        
                                        if "단위 : 백만원" in text or "단위: 백만원" in text or "단위:백만원" in text or "(백만원)" in text:
                                            unit_mult = 1_000_000
                                        elif "단위 : 천원" in text or "단위: 천원" in text or "단위:천원" in text or "(천원)" in text:
                                            unit_mult = 1_000
                                        elif "단위 : 원" in text or "단위: 원" in text or "(원)" in text:
                                            unit_mult = 1
                                        else:
                                            # Heuristic based on value magnitude
                                            temp_val_million = val * 1_000_000
                                            if temp_val_million > 20_000_000_000_000: # > 20 Trillion
                                                unit_mult = 1_000
                                            else:
                                                unit_mult = 1_000_000

                                        final_val = val * unit_mult
                                        
                                        # Sanity Check 2: If > 100 Trillion, it's probably wrong.
                                        if final_val > 100_000_000_000_000:
                                            if unit_mult > 1:
                                                final_val = val # Assume Won
                                        
                                        return final_val
                                    except:
                                        pass
                                        
        return 0

    def parse_narratives(self, html_content):
        """
        Extracts key narrative sections from the HTML content.
        Returns a list of dicts: [{'section_type': 'Business Overview', 'title': '...', 'content': '...'}]
        """
        if not html_content:
            return []
            
        soup = BeautifulSoup(html_content, 'html.parser')
        narratives = []
        
        # Helper to clean text
        def clean_text(text):
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            return text

        # 1. Business Overview (사업의 내용)
        # Strategy: Look for headers like "II. 사업의 내용" or "1. 사업의 개요"
        # Since DART HTML structure varies, we'll look for specific keywords in bold or headers
        
        # Simple heuristic: Find the section header and take the text until the next major header
        # This is tricky with raw HTML. For MVP, let's try to find specific sub-sections.
        
        # Try to find "1. 사업의 개요" or "가. 업계의 현황" etc.
        keywords = [
            {'type': 'Business Overview', 'pattern': r'1\.\s*사업의\s*개요', 'stop': r'2\.\s*주요\s*제품'},
            {'type': 'Business Overview', 'pattern': r'가\.\s*업계의\s*현황', 'stop': r'나\.\s*회사의\s*현황'},
            {'type': 'MD&A', 'pattern': r'이사의\s*경영진단\s*및\s*분석의견', 'stop': r'IV\.\s*이사의\s*경영진단'}, # Usually this is the header itself
        ]
        
        # Extract all text first to simplify regex search (losing structure but gaining simplicity)
        full_text = soup.get_text('\n')
        
        # 1. Business Overview - Summary
        # Often "1. 사업의 개요" contains the most important summary.
        match = re.search(r'(1\.\s*사업의\s*개요)(.*?)(2\.\s*주요\s*제품|3\.\s*주요\s*원재료)', full_text, re.DOTALL)
        if match:
            content = clean_text(match.group(2))
            if len(content) > 50: # Filter out empty matches
                narratives.append({
                    'section_type': 'Business Overview',
                    'title': '사업의 개요',
                    'content': content[:3000] + "..." if len(content) > 3000 else content # Truncate for DB
                })
        
        # 2. Key Takeaways (Synthetic)
        # If we can't find specific sections, let's try to grab the first few paragraphs of "II. 사업의 내용"
        # In DART, "II. 사업의 내용" is a major header.
        
        # For now, let's just use what we found.
        
        return narratives
