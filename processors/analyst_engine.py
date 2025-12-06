import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import pandas as pd
from utils import get_db_connection

class AnalystEngine:
    PERSONAS = {
        "value_hunter": {
            "name": "가치투자 사냥꾼 (The Value Hunter)",
            "focus": ["저평가 여부 (PBR, PER)", "재무 건전성", "내재 가치"],
            "tone": "차분하고 분석적이며, 숫자에 근거함.",
            "emoji": "🛡️"
        },
        "growth_scout": {
            "name": "성장주 탐험가 (The Growth Scout)",
            "focus": ["매출 성장률", "미래 잠재력", "시장 점유율 확대"],
            "tone": "열정적이고 미래 지향적이며, 잠재력을 강조함.",
            "emoji": "🚀"
        },
        "safety_inspector": {
            "name": "안전 제일 감독관 (The Safety Inspector)",
            "focus": ["부채 비율", "유동성", "배당 안정성"],
            "tone": "보수적이고 신중하며, 리스크를 경고함.",
            "emoji": "👷"
        },
        "momentum_surfer": {
            "name": "모멘텀 서퍼 (The Momentum Surfer)",
            "focus": ["주가 추세", "거래량", "시장 심리"],
            "tone": "에너지 넘치고 트렌드에 민감함.",
            "emoji": "🏄"
        },
        "day_trader": {
            "name": "단타 승부사 (The Day Trader)",
            "focus": ["단기 변동성", "거래량 급증", "매수/매도 타이밍"],
            "tone": "빠르고 직관적이며, 핵심만 짧게 전달함.",
            "emoji": "⚡"
        },
        "dividend_investor": {
            "name": "배당금 수집가 (The Dividend Investor)",
            "focus": ["배당 수익률", "배당 성향", "현금 흐름"],
            "tone": "여유롭고 안정적이며, 복리 효과를 중시함.",
            "emoji": "💰"
        }
    }

    def __init__(self, ticker, persona_id="value_hunter"):
        self.ticker = ticker
        self.persona_id = persona_id
        self.persona = self.PERSONAS.get(persona_id, self.PERSONAS["value_hunter"])
        self.conn = get_db_connection()

    def _fetch_financials(self):
        query = """
            SELECT * FROM financials 
            WHERE ticker = ? 
            ORDER BY year DESC, quarter DESC
            LIMIT 4
        """
        return pd.read_sql(query, self.conn, params=(self.ticker,))

    def _fetch_company_info(self):
        query = "SELECT * FROM companies WHERE ticker = ?"
        return pd.read_sql(query, self.conn, params=(self.ticker,))
    
    def _fetch_market_data(self):
        query = "SELECT * FROM market_daily WHERE ticker = ? ORDER BY date DESC LIMIT 30"
        return pd.read_sql(query, self.conn, params=(self.ticker,))

    def generate_prompt(self):
        df = self._fetch_financials()
        info_df = self._fetch_company_info()
        market_df = self._fetch_market_data()
        
        if df.empty or info_df.empty:
            return f"Error: Not enough data to generate prompt for {self.ticker}."

        latest = df.iloc[0]
        info = info_df.iloc[0]
        
        # Construct Data Context
        data_context = f"Company: {info['name']} ({self.ticker})\n"
        data_context += f"Summary: {info['desc_summary']}\n\n"
        data_context += "Recent Financials:\n"
        data_context += df.to_markdown(index=False) + "\n\n"
        
        if not market_df.empty:
            data_context += "Recent Market Data (Last 30 days):\n"
            data_context += market_df.head(5).to_markdown(index=False) + "\n"
            data_context += f"(...and {len(market_df)-5} more rows)\n\n"

        # Generate Persona-Specific System Prompt
        prompt = f"### LLM 시스템 프롬프트\n\n"
        prompt += f"**역할**: 당신은 '{self.persona['name']}'입니다. 다음과 같은 특징을 가진 투자 애널리스트입니다:\n"
        prompt += f"- **중점 분석 항목**: {', '.join(self.persona['focus'])}\n"
        prompt += f"- **말투 및 톤**: {self.persona['tone']}\n"
        prompt += f"- **스타일**: 이모지를 사용하지 말고, 전문적인 투자 용어를 사용하되 초보자도 이해할 수 있도록 어려운 개념은 쉽게 풀어서 설명해주세요.\n\n"
        
        prompt += "**임무**: 사용자가 첨부한 재무 및 시장 데이터를 바탕으로 종목을 분석해주세요. "
        
        if self.persona_id == "value_hunter":
            prompt += "이 주식이 저평가되었는지 판단하세요. PER과 PBR을 계산하고, 재무상태표의 건전성을 확인하세요. '싸게 사서 비싸게 파는 것'이 목표입니다."
        elif self.persona_id == "growth_scout":
            prompt += "폭발적인 성장 징후를 찾으세요. 매출 추세와 R&D 투자를 눈여겨보세요. 단기적인 변동성은 무시하고, 미래의 텐배거(10루타) 가능성을 평가하세요."
        elif self.persona_id == "safety_inspector":
            prompt += "파산 위험을 평가하세요. 부채 비율과 유동성을 꼼꼼히 체크하세요. 조금이라도 위험한 신호(Red Flag)가 있다면 강력하게 경고하세요. '원금을 잃지 않는 것'이 최우선입니다."
        elif self.persona_id == "momentum_surfer":
            prompt += "주가 추세와 거래량을 분석하세요. 상승 모멘텀이 있는지, 지금이 올라탈 타이밍인지 판단하세요. '추세는 나의 친구'입니다."
        elif self.persona_id == "day_trader":
            prompt += "변동성과 유동성을 확인하세요. 최근 가격 움직임을 보고 단기적인 진입/청산 구간을 제안하세요. 길게 설명하지 말고, 핵심만 짧고 굵게(Bullet points) 전달하세요."
        elif self.persona_id == "dividend_investor":
            prompt += "배당의 지속 가능성을 평가하세요. 배당 성향이 안전한지, 현금 흐름이 배당을 지지하는지 확인하세요. '잠자는 동안에도 돈이 들어오는 시스템'을 선호합니다."
            
        prompt += "\n\n**주의사항**:\n"
        prompt += "1. 분석에 필요한 구체적인 수치는 사용자가 첨부한 파일에 있습니다. 해당 데이터를 참고하여 분석하세요.\n"
        prompt += "2. 전문 용어(예: PER, ROE, 유동비율 등)가 나올 경우, 주식 초보자도 이해할 수 있도록 괄호 안에 간단한 설명을 덧붙여주세요.\n"
        
        return prompt

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate investment analysis based on persona.')
    parser.add_argument('--ticker', required=True, help='Company ticker symbol')
    parser.add_argument('--persona', default='value_hunter', help='Analyst persona ID')
    
    args = parser.parse_args()
    
    engine = AnalystEngine(args.ticker, args.persona)
    print(engine.generate_prompt())
