# 🌊 Systemic Liquidity Contagion & Fund Herding Engine

[![Live Dashboard](https://img.shields.io/badge/Live%20Demo-fund--predictor.vercel.app-blue?style=for-the-badge)](http://fund-predictor.vercel.app/)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Engineering-150458?style=flat&logo=pandas&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-Visualization-FF6384?style=flat&logo=chart.js&logoColor=white)
![Deployment](https://img.shields.io/badge/Deployed%20on-Vercel-000000?style=flat&logo=vercel&logoColor=white)

**Live Interactive Dashboard:** [fund-predictor.vercel.app](http://fund-predictor.vercel.app/)

---

## 📌 The Business Problem

In the mutual fund space, specifically within **Small and Mid-Cap** domains, traditional performance metrics often mask underlying structural risks. When multiple funds pile into the same thinly-traded stocks ("herding"), it creates a **Systemic Liquidity Contagion Risk**.

If a macroeconomic shock triggers mass redemptions, funds are forced to liquidate overlapping positions simultaneously. This crushes the underlying stock price, creating a downward spiral that destroys Net Asset Value (NAV) across the board.

This project was built to empirically measure, track, and visualize this hidden liquidity risk and profile the behavioral tendencies of fund managers.

---

## ⚙️ The Solution Architecture

This project is divided into a robust Python data-engineering pipeline and an interactive web-based dashboard, simulating the workflow of a Quantitative Risk Analyst.

### Phase 1: Data Engineering & Pipeline (`Codes/`)

Processing raw financial disclosures is notoriously messy. The pipeline cleans and structures disparate data:

- **`duplicate_cleaner.py`** — Uses **SHA-256 cryptographic hashing** to scan directories and eliminate duplicate portfolio files regardless of file name.
- **`fund_consolidator.py`** — Merges disparate portfolio CSVs into a master dataset. Features include:
  - **Fuzzy String Matching** (`difflib`) to map irregular fund names to a master AUM screener.
  - **Custom Text Parsing** to bypass corrupted CSV footers and disclaimers that break standard Pandas parsers.
  - Dynamic calculation of absolute Investment Value (in Crores) based on Asset % and Fund AUM.
- **`stock_universe_checker.py`** — A cross-sectional analysis tool that strips out non-equity instruments (T-Bills, GOI bonds) and aggregates the exact fund overlap and sector mapping for every stock.

### Phase 2: Quantitative Risk Engine (`Codes/liquidity_risk_engine.py`)

Applies rigorous academic and financial models to the raw data using live market feeds:

- **Automated Data Ingestion:** Uses a heuristic string-matching algorithm to map fund holdings to `.NS` (National Stock Exchange) tickers, querying the `yfinance` API for 90 days of historical market data.
  > *Note: A heuristic mapper with an override dictionary was built for this POC. In a production environment, this would integrate with an institutional ISIN master feed like Bloomberg/Refinitiv.*
- **Days to Liquidate (DTL):** Calculates how many days a fund needs to exit a position based on Average Daily Volume (ADV) and participation caps.
- **Amihud Market Impact Measure:** Estimates the exact percentage the stock price will drop, predicting real-world slippage during a redemption shock.

### Phase 3: Interactive Dashboard

A front-end visualization tool designed for Portfolio Managers and Risk Officers.

- **Fund Overlap Map** (`fund_overlap_dashboard.html`): Visualizes which stocks are the most "crowded" trades in the industry using dynamic linear gradients. Features behavioral profiling to grade fund managers (identifying "Herd Followers" vs. "Contrarians").
- **Liquidity Stress Test** (`stress_test_dashboard.html`): An interactive command center. Users can adjust fund AUM, allocation percentages, and shock severity to simulate a market crash and instantly see the resulting DTL and Price Impact on the most vulnerable stocks.

---

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| **Data Processing** | Python, Pandas, NumPy, Hashlib, Difflib, yfinance |
| **Front-End Visualization** | HTML5, JavaScript, TailwindCSS, Chart.js, PapaParse |
| **Deployment** | Vercel |

---

## 🚀 How to Run Locally

1. Clone the repository.

2. Ensure you have the required Python libraries installed:
   ```bash
   pip install pandas openpyxl yfinance
   ```

3. Maintain the following folder structure:

   ```
   FUND PREDICTOR/
   ├── index.html (Vercel Redirect)
   ├── Codes/
   │   ├── duplicate_cleaner.py
   │   ├── fund_consolidator.py
   │   ├── stock_universe_checker.py
   │   ├── liquidity_risk_engine.py
   │   ├── fund_overlap_dashboard.html
   │   └── stress_test_dashboard.html
   └── Database/
       ├── Small Cap Funds/ (Place raw CSVs here)
       ├── screener.csv
       ├── Master Consolidated Funds.xlsx
       ├── stock_overlap_report.csv
       └── liquidity_risk_report.csv
   ```

4. Navigate to the `Codes` folder and run the Python pipeline in order:

   ```bash
   cd Codes
   python duplicate_cleaner.py
   python fund_consolidator.py
   python stock_universe_checker.py
   python liquidity_risk_engine.py
   ```

5. Open `Codes/fund_overlap_dashboard.html` using a local server (e.g., VS Code "Live Server" extension) to explore the interactive visualizations locally.

---

## 📈 Future Scope

- **Liquidity-Adjusted VaR (L-VaR):** Upgrading standard Value at Risk models to penalize illiquid portfolios.
- **Live Automated Scheduling:** Setting up a CRON job or AWS Lambda function to run the Python pipeline daily and update the Vercel deployment automatically.

---

## 🔗 Live Demo

👉 **[fund-predictor.vercel.app](http://fund-predictor.vercel.app/)**
