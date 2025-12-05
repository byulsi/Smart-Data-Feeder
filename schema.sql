-- 1. Companies Table
create table if not exists companies (
  ticker varchar(10) primary key,
  name varchar(100) not null,
  sector varchar(100),
  market_type varchar(10),
  est_dt varchar(8), -- Establishment Date (YYYYMMDD)
  listing_dt varchar(8), -- Listing Date (YYYYMMDD)
  market_cap bigint, -- Market Capitalization
  shares_outstanding bigint, -- Total Shares Outstanding
  desc_summary text,
  updated_at datetime default current_timestamp
);

-- 2. Financials Table
create table if not exists financials (
  id integer primary key autoincrement,
  ticker varchar(10) references companies(ticker) not null,
  year int not null,
  quarter int not null, -- 0: Yearly, 1-4: Quarterly
  revenue bigint,
  op_profit bigint,
  net_income bigint,
  assets bigint,
  liabilities bigint,
  equity bigint,
  current_assets bigint, -- New
  current_liabilities bigint, -- New
  ocf bigint, -- Operating Cash Flow
  eps float, -- Earnings Per Share
  bps float, -- Book Value Per Share
  dps float, -- Dividend Per Share
  roe float, -- Return on Equity
  roa float, -- Return on Assets
  debt_ratio float, -- Liabilities / Equity
  current_ratio float, -- Current Assets / Current Liabilities
  per float, -- Price Earnings Ratio
  pbr float, -- Price Book-value Ratio
  rnd_expenses bigint, -- Research & Development Expenses
  is_estimated boolean default false,
  created_at datetime default current_timestamp,
  unique(ticker, year, quarter)
);

-- 3. Disclosures Table
create table if not exists disclosures (
  rcept_no varchar(20) primary key,
  ticker varchar(10) references companies(ticker) not null,
  report_nm varchar(255) not null,
  rcept_dt date not null,
  flr_nm varchar(100),
  url varchar(255),
  summary_body text, -- Parsed text content
  created_at datetime default current_timestamp
);

-- 4. Market Daily Table
create table if not exists market_daily (
  id integer primary key autoincrement,
  ticker varchar(10) references companies(ticker) not null,
  date date not null,
  close float,
  open float,
  high float,
  low float,
  volume bigint,
  ma5 float,
  ma20 float,
  ma60 float,
  created_at datetime default current_timestamp,
  unique(ticker, date)
);

-- 5. Company Segments Table (NEW)
create table if not exists company_segments (
  id integer primary key autoincrement,
  ticker varchar(10) references companies(ticker) not null,
  period varchar(20) not null, -- e.g., '2025.3Q'
  division varchar(100) not null, -- e.g., 'DS', 'DX'
  revenue varchar(50), -- Storing as string for flexibility with units like '33.1T' or raw numbers
  op_profit varchar(50),
  insight text,
  created_at datetime default current_timestamp,
  unique(ticker, period, division)
);

-- 6. Company Narratives Table (NEW)
create table if not exists company_narratives (
  id integer primary key autoincrement,
  ticker varchar(10) references companies(ticker) not null,
  period varchar(20) not null, -- e.g., '2025.09'
  section_type varchar(50) not null, -- 'Market', 'Strategy', 'Business', 'MD&A', 'News'
  title varchar(255), -- Optional title for the section
  content text not null,
  created_at datetime default current_timestamp,
  unique(ticker, period, section_type)
);

-- 7. Shareholders Table (NEW)
create table if not exists shareholders (
  id integer primary key autoincrement,
  ticker varchar(10) references companies(ticker) not null,
  holder_name varchar(100) not null,
  rel_type varchar(50), -- Relation (e.g., 본인, 특수관계인)
  share_count bigint,
  share_ratio float, -- Percentage
  created_at datetime default current_timestamp,
  unique(ticker, holder_name)
);

-- Indexing for Performance
create index if not exists idx_financials_ticker on financials(ticker);
create index if not exists idx_disclosures_ticker on disclosures(ticker);
create index if not exists idx_market_daily_ticker on market_daily(ticker);
create index if not exists idx_company_segments_ticker on company_segments(ticker);
create index if not exists idx_company_narratives_ticker on company_narratives(ticker);

-- 8. Feedbacks Table (NEW)
create table if not exists feedbacks (
  id integer primary key autoincrement,
  type varchar(50) not null, -- 'bug', 'suggestion', 'other'
  content text not null,
  contact varchar(100),
  created_at datetime default current_timestamp
);
