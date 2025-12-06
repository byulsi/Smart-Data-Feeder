# Antz (MVP)

Antz is a Python-based data collection and processing pipeline designed to feed high-quality financial data into LLMs (Large Language Models) like Gemini. It fetches data from DART (OpenDART) and FinanceDataReader, processes it into structured formats (Markdown, CSV), and provides a simple web interface for easy access.

## 🚀 Key Features

*   **Automated Data Collection**: Fetches data from multiple sources:
    *   **OpenDART**: Financial statements (Revenue, Profit, Assets, Liabilities), Business Reports (R&D Expenses), Major Shareholders.
    *   **FinanceDataReader**: Market Cap, Shares Outstanding, Sector Info, Daily Price Data.
*   **Comprehensive Financial Analysis**:
    *   **Growth**: Revenue, Operating Profit, Net Income growth rates.
    *   **Profitability**: OPM, NPM, ROE, ROA.
    *   **Stability**: Debt Ratio, Current Ratio.
    *   **Valuation**: PER, PBR, EPS, BPS.
    *   **Investment**: R&D Expenses, Dividend Yield (planned).
*   **Deep Business Insights**:
    *   **Segment Analysis**: Revenue and profit breakdown by business division.
    *   **R&D Investment**: Track research and development spending trends.
    *   **Shareholding**: Major shareholder structure and ownership ratios.
*   **AI-Ready Output**:
    *   Generates structured Markdown reports (`Overview.md`, `Narratives.md`) optimized for LLM ingestion (RAG).
    *   Stores raw data in SQLite for easy querying.
*   **Web Dashboard**:
    *   Search companies by Ticker or Name.
    *   View key metrics and charts.
    *   Download reports directly from the browser.
*   **Dockerized Deployment**: Easy setup with Docker Compose.d data.

## Tech Stack

- **Backend**: Python 3.9+
    - `OpenDartReader`: DART API integration
    - `FinanceDataReader`: Market data
    - `BeautifulSoup4`: HTML/XML parsing
    - `SQLite`: Local database
- **Frontend**: Next.js 14 (App Router), Tailwind CSS
- **Deployment**: Localhost (MVP)

## Setup & Usage

### Prerequisites
1.  Python 3.9+
2.  Node.js 18+
3.  DART API Key (Get it from [OpenDART](https://opendart.fss.or.kr/))

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/byulsi/Smart-Data-Feeder.git
    cd Smart-Data-Feeder
    ```

2.  **Install Python dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Environment Variables**
    Create a `.env` file in the root directory:
    ```env
    DART_API_KEY=your_api_key_here
    ```

4.  **Install Frontend dependencies**
    ```bash
    cd web
    npm install
    cd ..
    ```

### Running the Web App (Recommended)

The easiest way to use Antz is via the Web UI.

```bash
cd web
npm run dev
```

1.  Visit `http://localhost:3000`.
2.  **Search**: Enter a ticker (e.g., `005930` for Samsung, `000660` for SK Hynix).
3.  **Collect**: If data is missing, click the **"Collect Data Now"** button. The system will automatically run the Python collector in the background.
4.  **Download**: Once data is ready, download the `Overview.md` report.

### Running the Collector Manually (Optional)

You can still run the collector via terminal if preferred:

```bash
python3 collector.py 005930
```

## Project Structure

- `collectors/`: Modules for fetching data (companies, financials, disclosures, market).
- `processors/`: Logic for processing data and generating Markdown.
- `web/`: Next.js frontend application.
- `schema.sql`: Database schema definition.
- `utils.py`: Database utility functions.
- `collector.py`: Main entry point for data collection.

## Deployment (Docker)

This application is containerized for easy deployment on any server (VPS, AWS, etc.).

### Prerequisites
- Docker & Docker Compose installed.
- Valid `DART_API_KEY` in `.env` file.

### Steps
1.  **Build and Run**:
    ```bash
    docker-compose up -d --build
    ```
2.  **Access**: Open `http://localhost:3000`.
3.  **Persistence**:
    - `data.db` is mounted as a volume, so data survives container restarts.
    - `output/` is mounted to access generated Markdown files directly if needed.

### Stopping
```bash
docker-compose down
```
