import sqlite3
import os

def get_db_connection():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def seed_samsung_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    ticker = "005930"
    
    print(f"Seeding data for {ticker}...")
    
    # 1. Seed Company Segments
    segments = [
        ("2025.3Q", "DS Division (Semiconductor)", "29.27T KRW", "3.86T KRW", "Memory demand strong (HBM/DDR5), but one-off costs and legacy inventory valuation hit profits."),
        ("2025.3Q", "DX Division (Mobile/Appliances)", "44.99T KRW", "3.37T KRW", "S24 sales solid, but raw material costs and competition impacted margins."),
        ("2025.3Q", "SDC (Display)", "8.0T KRW", "1.51T KRW", "Strong flagship demand (Apple/Samsung) maintained profitability."),
        ("2025.3Q", "Harman", "3.53T KRW", "0.36T KRW", "Automotive demand stable.")
    ]
    
    for period, division, revenue, op_profit, insight in segments:
        try:
            cursor.execute("""
                INSERT INTO company_segments (ticker, period, division, revenue, op_profit, insight)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(ticker, period, division) DO UPDATE SET
                revenue=excluded.revenue,
                op_profit=excluded.op_profit,
                insight=excluded.insight
            """, (ticker, period, division, revenue, op_profit, insight))
        except Exception as e:
            print(f"Error inserting segment {division}: {e}")

    # 2. Seed Company Narratives
    narratives = [
        ("2025.09", "Key Takeaways", "Market Conditions", 
         "- **Memory:** Market is recovering due to AI server demand (HBM, DDR5), but legacy product demand remains weak due to mobile inventory adjustments.\n- **Foundry:** Focusing on 2nm GAA process competitiveness despite delayed mass production schedules."),
        
        ("2025.09", "Key Takeaways", "Strategic Focus", 
         "- **HBM Leadership:** Accelerating HBM3E 8-layer/12-layer qualification and mass production to capture AI demand.\n- **Premium Mobile:** Expanding Galaxy S24 AI features and foldable lineup to maintain premium market share."),
        
        ("2025.09", "Business Overview", "시장 여건", 
         "- **반도체 (DS):** AI 서버용 고성능 메모리 수요는 견조하나, 모바일/PC 등 소비자용 IT 수요 회복은 지연되고 있음. 중국발 레거시 D램 공급 과잉 우려 존재.\n- **모바일 (DX):** 스마트폰 시장은 프리미엄 중심으로 소폭 성장 중이나, 원자재 가격 상승 및 경쟁 심화로 수익성 확보가 중요해짐."),
        
        ("2025.09", "Business Overview", "주요 제품 현황", 
         "- **메모리:** D램/낸드 가격은 전분기 대비 상승세 둔화. HBM 비중 확대가 ASP 방어의 핵심.\n- **스마트폰:** S24 시리즈 판매 호조 지속, 폴더블 신제품 출시 효과 반영 예정."),
        
        ("2025.09", "Business Overview", "신규 사업", 
         "- **R&D:** 차세대 패키징 기술(AVP) 및 2nm 공정 개발에 역량 집중.\n- **투자:** 평택/테일러 팹 투자 속도 조절 중이나, HBM 전용 라인 투자는 확대."),
        
        ("2025.09", "MD&A", "실적 변동 원인", 
         "- **매출:** HBM 및 고부가 메모리 판매 확대로 전년 동기 대비 증가.\n- **영업이익:** DS 부문은 흑자 기조 유지했으나, 성과급 충당금 등 일회성 비용과 재고 평가손 환입 규모 축소로 전분기 대비 감소."),
        
        ("2025.09", "MD&A", "재무 상태", 
         "- **자산:** 설비 투자 및 현금성 자산 확보로 증가.\n- **부채:** 차입금 상환 등으로 안정적 수준 유지."),
        
        ("2025.09", "News", "3Q Conf Call Q&A", 
         "\"HBM3E 공급 지연에 대한 우려가 있으나, 주요 고객사 퀄 테스트 진행 중이며 4분기 내 유의미한 매출 기여 목표.\""),
        
        ("2025.09", "News", "Analyst View", 
         "\"4분기까지는 레거시 재고 조정 영향 불가피, 2025년 HBM 경쟁력 회복 여부가 주가 반등의 열쇠.\"")
    ]
    
    for period, section_type, title, content in narratives:
        try:
            # Check if exists to avoid duplicates if run multiple times (simple check)
            # For simplicity, we just insert. Ideally we'd have a unique constraint on (ticker, period, section_type, title)
            # but title is optional and section_type can have multiple entries.
            # Let's just delete existing for this period/section/title to be safe or just append.
            # Given the schema doesn't have unique constraint on title, let's delete first to avoid dupes on re-run
            cursor.execute("DELETE FROM company_narratives WHERE ticker=? AND period=? AND section_type=? AND title=?", (ticker, period, section_type, title))
            
            cursor.execute("""
                INSERT INTO company_narratives (ticker, period, section_type, title, content)
                VALUES (?, ?, ?, ?, ?)
            """, (ticker, period, section_type, title, content))
        except Exception as e:
            print(f"Error inserting narrative {section_type}/{title}: {e}")

    conn.commit()
    conn.close()
    print("Seeding completed.")

if __name__ == "__main__":
    seed_samsung_data()
