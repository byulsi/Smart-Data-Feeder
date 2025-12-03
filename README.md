# Smart Data Feeder (스마트 개미를 위한 백데이터 생성기)

**Smart Data Feeder**는 투자 분석에 필요한 방대한 금융 정보(재무제표, 공시, 주가 등)를 수집하여, AI(Gemini, ChatGPT 등)가 이해하기 쉬운 **Markdown** 및 **CSV** 형식으로 변환해주는 도구입니다.

흩어진 정보를 일일이 찾는 수고를 덜고, AI를 활용한 데이터 기반의 합리적인 투자를 돕기 위해 만들어졌습니다.

## 🚀 주요 기능

1.  **기업 종합 스냅샷 (Corporate Overview)**
    *   기업 개요, 주요 사업 요약
    *   최근 3년/분기 핵심 재무제표 (매출, 영업이익, 순이익, 부채비율 등)
    *   최근 공시 목록 요약
    *   **결과물:** `[종목명]_Overview.md`

2.  **심층 분석 텍스트 (Deep Dive Narratives)**
    *   주요 공시(사업보고서 등) 원문 링크 및 요약
    *   **결과물:** `[종목명]_Narratives.md`

3.  **주가 데이터 (Market Data)**
    *   최근 1년 일봉 데이터 (OHLCV) 및 이동평균선(5, 20, 60일)
    *   **결과물:** `[종목명]_Chart.csv`

## 🛠 기술 스택

*   **Backend:** Python 3.8+
    *   `FinanceDataReader`: 주가 및 기업 기본 정보 수집
    *   `OpenDartReader`: DART 공시 정보 수집
    *   `requests`: 공공데이터포털(금융위) API 연동
    *   `pandas`, `polars`: 데이터 가공
*   **Database:** PostgreSQL (Supabase)
*   **Frontend:** Next.js 14 (App Router), Tailwind CSS
    *   데이터 조회 및 다운로드 대시보드

## ⚙️ 설치 및 실행 방법

### 1. 사전 준비 (Prerequisites)
*   Python 3.8 이상
*   Node.js 18 이상
*   **Supabase** 프로젝트 (PostgreSQL)
*   **API 키 발급**:
    *   [DART Open API](https://opendart.fss.or.kr/) (API Key)
    *   [공공데이터포털](https://www.data.go.kr/) (금융위원회 기업기본정보/재무정보 서비스키)

### 2. 환경 변수 설정 (.env)
프로젝트 루트에 `.env` 파일을 생성하고 아래 내용을 입력하세요.

```ini
# OpenDART API Key
DART_API_KEY=your_dart_api_key

# 공공데이터포털 (금융위원회) API Key
FSC_API_KEY=your_fsc_service_key

# Supabase 설정
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
DATABASE_URL=postgresql://postgres:password@db.supabase.co:5432/postgres
```

### 3. 백엔드 설정 및 데이터 수집
```bash
# 가상환경 생성 및 패키지 설치
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 데이터베이스 테이블 생성 (Supabase SQL Editor에서 schema.sql 실행 권장)
# 또는 별도 DB 툴 사용

# 데이터 수집 실행 (예: 삼성전자 005930)
python collector.py 005930
```

### 4. 웹 애플리케이션 실행
```bash
cd web
npm install
npm run dev
```
브라우저에서 `http://localhost:3000` 접속.

## 📂 프로젝트 구조

```
.
├── collector.py          # 데이터 수집 메인 스크립트
├── collectors/           # 데이터 소스별 수집 모듈
│   ├── companies.py      # 기업 개요
│   ├── financials.py     # 재무 정보
│   ├── disclosures.py    # 공시 목록
│   └── market.py         # 주가 데이터
├── processors/           # 데이터 가공 및 파일 생성 모듈
├── web/                  # Next.js 프론트엔드
├── utils.py              # DB 연결 유틸리티
├── requirements.txt      # Python 의존성
└── schema.sql            # DB 스키마
```

## 📝 라이선스
MIT License
