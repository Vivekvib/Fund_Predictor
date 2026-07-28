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

## 🧮 Quantitative Methodology & Mathematical Models

This project moves beyond standard portfolio tracking by implementing rigorous academic and institutional risk models to quantify exactly what happens during a market sell-off.

### 1. The Amihud Illiquidity Measure

To predict price slippage during a fire sale, the Python engine calculates the Amihud Illiquidity Measure for each stock using 90 days of live market data. This measures the price impact of every ₹1 of trading volume.

$$Illiquidity = \frac{1}{N} \sum_{i=1}^{N} \frac{|R_i|}{V_i \times P_i}$$

- $R_i$ = Daily Return (Absolute percentage change)
- $V_i$ = Daily Trading Volume (in shares)
- $P_i$ = Daily Closing Price (INR)
- $N$ = Number of trading days (90 days)

*Higher Amihud scores indicate highly illiquid stocks that will experience violent price drops if funds attempt to sell.*

### 2. Days to Liquidate (DTL)

In our Stress Test Engine, we calculate exactly how many days it will take a fund to exit their position without crashing the market. We assume a strict regulatory/market participation cap (e.g., a fund cannot account for more than 20% of the daily traded volume).

$$DTL = \frac{S_{held} \times \%_{shock}}{ADV \times \%_{participation}}$$

- $S_{held}$ = Total shares owned by the fund
- $\%_{shock}$ = The severity of the redemption shock (e.g., 20% of AUM withdrawn)
- $ADV$ = 90-Day Average Daily Volume
- $\%_{participation}$ = Maximum allowed participation in daily volume to avoid market crash

### 3. Estimated Price Impact

Finally, we combine the liquidation volume with the Amihud measure to estimate the total percentage drop in the stock's price caused directly by the fund's forced selling.

$$Impact_{Est} = (S_{sell} \times P_{current}) \times Amihud \times 100$$

---

## ⚙️ The Solution Architecture

This project is divided into a robust Python data-engineering pipeline and an interactive web-based dashboard, simulating the workflow of a Quantitative Risk Analyst.

### Phase 1: Data Engineering & Pipeline (`Codes/`)

Processing raw financial disclosures is notoriously messy. The pipeline cleans and structures disparate data:

- **`remove_duplicates.py`** — Uses **SHA-256 cryptographic hashing** to scan directories and eliminate duplicate portfolio files regardless of file name.
- **`consolidate_funds.py`** — Merges disparate portfolio CSVs into a master dataset. Features include:
  - **Fuzzy String Matching** (`difflib`) to map irregular fund names to a master AUM screener.
  - **Custom Text Parsing** to bypass corrupted CSV footers and disclaimers that break standard Pandas parsers.
  - Dynamic calculation of absolute Investment Value (in Crores) based on Asset % and Fund AUM.
- **`unique_stocks_checker.py`** — A cross-sectional analysis tool that strips out non-equity instruments (T-Bills, GOI bonds) and aggregates the exact fund overlap and sector mapping for every stock.

### Phase 2: Quantitative Risk Engine (`Codes/liquidity_risk_engine.py`)

Applies the mathematical models above to the raw data using live market feeds:

- **Automated Data Ingestion:** Uses a heuristic string-matching algorithm to map fund holdings to `.NS` (National Stock Exchange) tickers, querying the `yfinance` API for historical market data.
  > *Note: A heuristic mapper with an override dictionary was built for this POC. In a production environment, this would integrate with an institutional ISIN master feed like Bloomberg/Refinitiv.*
- **Risk Metric Generation:** Calculates the 90-Day ADV, Current Price, and Amihud score for every mapped stock and outputs a consolidated risk report.

### Phase 3: Interactive Dashboard

A front-end visualization tool designed for Portfolio Managers and Risk Officers.

- **Fund Overlap Map** (`fund_overlap_dashboard.html`): Visualizes which stocks are the most "crowded" trades in the industry using dynamic linear gradients. Features behavioral profiling to grade fund managers (identifying "Herd Followers" vs. "Contrarians").
- **Liquidity Stress Test** (`stress_test_dashboard.html`): An interactive command center. Users can adjust fund AUM, allocation percentages, and shock severity to simulate a market crash and instantly see the resulting DTL and Price Impact on the most vulnerable stocks.

---

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| **Quantitative & Data Engineering** | Python, Pandas, NumPy, Hashlib, Difflib, yfinance |
| **Front-End Visualization** | HTML5, JavaScript, TailwindCSS, Chart.js, PapaParse |
| **Deployment** | Vercel |

---

## 🚀 How to Run Locally

1. Clone the repository.

2. Ensure you have the required Python libraries installed:
   ```bash
   pip install pandas openpyxl yfinance numpy
   ```

3. Maintain the following folder structure:

   ```
   FUND_PREDICTOR/
   ├── index.html (Vercel Redirect)
   ├── Codes/
   │   ├── remove_duplicates.py
   │   ├── consolidate_funds.py
   │   ├── unique_stocks_checker.py
   │   ├── liquidity_risk_engine.py
   │   ├── fund_overlap_dashboard.html
   │   └── stress_test_dashboard.html
   └── Database/
       ├── Small_Cap_Funds/ (Place raw CSVs here)
       ├── screener.csv
       ├── Master_Consolidated_Funds.xlsx
       ├── stock_overlap_report.csv
       └── liquidity_risk_report.csv
   ```

4. Navigate to the `Codes` folder and run the Python pipeline in order:

   ```bash
   cd Codes
   python remove_duplicates.py
   python consolidate_funds.py
   python unique_stocks_checker.py
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
