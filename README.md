# Smart Data Feeder (MVP)

Smart Data Feeder is a Python-based data collection and processing pipeline designed to feed high-quality financial data into LLMs (Large Language Models) like Gemini. It fetches data from DART (OpenDART) and FinanceDataReader, processes it into structured formats (Markdown, CSV), and provides a simple web interface for easy access.

## Key Features

- **Automated Data Collection**: Fetches company info, financial statements, disclosures, and market data.
- **Deep Text Extraction**: Extracts full text from "Business Overview" sections of DART reports for qualitative analysis.
- **Segment Data Parsing**: Extracts "Sales by Business Division" (e.g., DX, DS, SDC) from unstructured HTML tables in reports.
- **LLM-Ready Output**: Generates `[Ticker]_Overview.md` and `[Ticker]_Narratives.md` optimized for RAG (Retrieval-Augmented Generation).
- **Web Dashboard**: A Next.js-based UI to search companies, view key metrics (Est. Date, Listing Date), and download processed data.

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

The easiest way to use the Smart Data Feeder is via the Web UI.

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
