🌊 Systemic Liquidity Contagion & Fund Herding Engine

📌 The Business Problem

In the mutual fund space, specifically within Small and Mid-Cap domains, traditional performance metrics often mask underlying structural risks. When multiple funds pile into the same thinly-traded stocks ("herding"), it creates a Systemic Liquidity Contagion Risk. If a macroeconomic shock triggers mass redemptions, funds are forced to liquidate overlapping positions simultaneously. This crushes the underlying stock price, creating a downward spiral that destroys Net Asset Value (NAV) across the board.

This project was built to empirically measure, track, and visualize this hidden liquidity risk and profile the behavioral tendencies of fund managers.

⚙️ The Solution Architecture

This project is divided into a robust Python data-engineering pipeline and an interactive web-based dashboard.

Phase 1: Data Engineering & Pipeline (Codes/)

Processing raw financial disclosures is notoriously messy. The pipeline cleans and structures disparate data:

duplicate_cleaner.py: Uses SHA-256 cryptographic hashing to scan directories and eliminate duplicate portfolio files regardless of file name.

fund_consolidator.py: Merges disparate portfolio CSVs into a master dataset. Features include:

Fuzzy String Matching (difflib) to map irregular fund names to a master AUM screener.

Custom Text Parsing to bypass corrupted CSV footers and disclaimers that break standard Pandas parsers.

Dynamic calculation of absolute Investment Value (in Crores) based on Asset % and Fund AUM.

stock_universe_checker.py: A cross-sectional analysis tool that strips out non-equity instruments (T-Bills, GOI bonds) and aggregates the exact fund overlap and sector mapping for every stock.

Phase 2: Quantitative Risk Engine (Upcoming)

To be integrated: Applying rigorous academic and financial models to the raw data:

Days to Liquidate (DTL): Calculating how many days a fund needs to exit a position based on Average Daily Volume (ADV).

Amihud Market Impact Measure: Estimating the exact percentage the stock price will drop predicting real-world slippage during a redemption shock.

Phase 3: Interactive Dashboard (fund_overlap_dashboard.html)

A front-end visualization tool designed for Portfolio Managers and Risk Officers.

Dynamic Overlap Matrix: Visualizes which stocks are the most "crowded" trades in the industry using dynamic linear gradients.

Behavioral Profiling: The JavaScript engine reverse-engineers the dataset to grade fund managers:

🐑 The Herd Follower: The fund with the highest average stock overlap (buying what everyone else buys).

🦅 The Contrarian: The fund with the lowest average overlap (avoiding crowded trades).

💎 Unique Bets: Tracks funds holding "orphaned" stocks that no other fund holds.

🛠️ Tech Stack

Data Processing: Python, Pandas, NumPy, Hashlib, Difflib.

Front-End Visualization: HTML5, JavaScript, TailwindCSS, Chart.js, PapaParse.

🚀 How to Run Locally

Clone the repository.

Ensure you have the required Python libraries installed: pip install pandas openpyxl

Maintain the following folder structure:

FUND_PREDICTOR/
├── Codes/
│   ├── duplicate_cleaner.py
│   ├── fund_consolidator.py
│   ├── stock_universe_checker.py
│   └── fund_overlap_dashboard.html
└── Database/
    ├── Small_Cap_Funds/ (Place raw CSVs here)
    ├── screener.csv
    └── Master_Consolidated_Funds.xlsx


Navigate to the Codes folder and run the Python pipeline in order:

python duplicate_cleaner.py
python fund_consolidator.py
python stock_universe_checker.py


Open fund_overlap_dashboard.html using a local server (e.g., VS Code "Live Server" extension) to explore the interactive visualizations.

Open this url to see the Dashboard: https://fund-predictor-git-main-vivek-nishads-projects.vercel.app/

📈 Future Scope

Liquidity-Adjusted VaR (L-VaR): Upgrading standard Value at Risk models to penalize illiquid portfolios.

Live Market Integration: Pulling live 90-day ADV and price data via the yfinance API to simulate real-time liquidity shocks.