# PortfolioLab

A complete financial analysis and portfolio tracking web application built with FastAPI and Streamlit.

## Features

- **Portfolio Tracking**: Add and remove stocks with quantity and cost basis
- **Real-Time Data**: Live prices and financial data via Yahoo Finance (yfinance)
- **Financial Metrics**: P/E ratio, EV/EBITDA, PEG, ROE, revenue growth, margins, free cash flow
- **Risk Analysis**: Volatility, Sharpe ratio, max drawdown, correlation matrix
- **Interactive Charts**: Plotly-powered visualizations including pie charts, line charts, heatmaps
- **Performance Benchmarking**: Compare portfolio against S&P 500 (SPY)

## Architecture

```
PortfolioLab/
├── backend/          # FastAPI backend
│   ├── main.py       # API endpoints
│   ├── data/         # Data providers (Yahoo Finance)
│   ├── models/       # Pydantic data models
│   └── services/     # Business logic (portfolio, financial, risk)
├── frontend/         # Streamlit frontend
│   ├── app.py        # Main application
│   └── dashboard/    # Dashboard components (overview, metrics, risk)
└── requirements.txt
```

## Prerequisites

- Python 3.9+
- pip

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/PortfolioLab.git
   cd PortfolioLab
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the environment file:
   ```bash
   cp .env.example .env
   ```

## Running the Application

### Start the Backend

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.
API documentation is available at `http://localhost:8000/docs`.

### Start the Frontend

In a separate terminal:

```bash
streamlit run frontend/app.py
```

The dashboard will open at `http://localhost:8501`.

## Example Usage

1. Open the Streamlit dashboard at `http://localhost:8501`
2. In the sidebar, add stocks to your portfolio:
   - **AAPL** — 10 shares @ $150.00
   - **MSFT** — 5 shares @ $280.00
   - **SPY** — 20 shares @ $420.00
3. Explore the three dashboard tabs:
   - **Portfolio Overview**: Allocation pie chart, total returns, benchmark comparison
   - **Financial Metrics**: Valuation multiples, revenue growth, margins, FCF
   - **Risk Analysis**: Volatility, Sharpe ratio, drawdown, correlation heatmap

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/api/portfolio` | Get all portfolio items |
| POST | `/api/portfolio/add` | Add a stock to the portfolio |
| DELETE | `/api/portfolio/{ticker}` | Remove a stock |
| GET | `/api/portfolio/summary` | Portfolio summary with returns |
| GET | `/api/metrics/{ticker}` | Financial metrics for a ticker |
| GET | `/api/risk` | Portfolio risk metrics |
| GET | `/api/prices/{ticker}` | Historical prices |
| GET | `/api/benchmark` | S&P 500 benchmark data |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_URL` | `http://localhost:8000` | FastAPI backend URL |
| `ALPHA_VANTAGE_API_KEY` | *(optional)* | Alpha Vantage API key for additional data |

## License

MIT