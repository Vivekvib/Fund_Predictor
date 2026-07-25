import pandas as pd
import yfinance as yf
import numpy as np
import os
import time

def guess_nse_ticker(company_name):
    """
    A heuristic function to guess the Yahoo Finance NSE ticker from a raw company name.
    In a production environment, this is usually replaced by a paid ISIN/Ticker mapping database.
    """
    name = str(company_name).upper()
    
    # Hardcode a few very common large-caps that have tricky acronyms
    overrides = {
        "HDFC BANK": "HDFCBANK.NS",
        "ICICI BANK": "ICICIBANK.NS",
        "STATE BANK OF INDIA": "SBIN.NS",
        "RELIANCE INDUSTRIES": "RELIANCE.NS",
        "LARSEN & TOUBRO": "LT.NS",
        "MAHINDRA & MAHINDRA": "M&M.NS",
        "TCS": "TCS.NS",
        "INFOSYS": "INFY.NS",
        "ITC": "ITC.NS",
        "BHARTI AIRTEL": "BHARTIARTL.NS",
        # --- NEW OVERRIDES FROM AUDIT REPORT ---
        "AXIS BANK": "AXISBANK.NS",
        "KOTAK MAHINDRA": "KOTAKBANK.NS",
        "SUN PHARM": "SUNPHARMA.NS",
        "ULTRATECH": "ULTRACEMCO.NS",
        "BAJAJ FINANCE": "BAJFINANCE.NS",
        "INTERGLOBE": "INDIGO.NS",
        "SHRIRAM FINANCE": "SHRIRAMFIN.NS",
        "TATA STEEL": "TATASTEEL.NS",
        "SBI LIFE": "SBILIFE.NS",
        "HINDUSTAN UNILEVER": "HINDUNILVR.NS",
        "TORRENT PHARM": "TORNTPHARM.NS",
        "SAMVARDHANA": "MOTHERSON.NS",
        "DIVI'S": "DIVISLAB.NS",
        "CHOLAMANDALAM INV": "CHOLAFIN.NS",
        "BHARAT ELECTRONICS": "BEL.NS",
        
        # --- NEW OVERRIDES FROM AUDIT REPORT 2 ---
        "TATA CONSULTANCY": "TCS.NS",
        "VARUN BEVERAGES": "VBL.NS",
        "MAX HEALTHCARE": "MAXHEALTH.NS",
        "TVS MOTOR": "TVSMOTOR.NS",
        "CUMMINS INDIA": "CUMMINSIND.NS",
        "AVENUE SUPERMARTS": "DMART.NS",
        "HDFC LIFE": "HDFCLIFE.NS",
        "EICHER MOTORS": "EICHERMOT.NS",
        "UNITED SPIRITS": "UNITDSPR.NS",
        "ADANI PORTS": "ADANIPORTS.NS",
        "ASIAN PAINTS": "ASIANPAINT.NS",
        "INDIAN HOTELS": "INDHOTEL.NS",
        "ICICI PRUDENTIAL": "ICICIPRULI.NS",
        "CG POWER": "CGPOWER.NS",
        "VEDANTA": "VEDL.NS",
        
        # --- NEW OVERRIDES FROM AUDIT REPORT 3 ---
        "TATA MOTORS": "TATAMOTORS.NS",
        "BAJAJ AUTO": "BAJAJ-AUTO.NS",
        "HINDUSTAN AERONAUTICS": "HAL.NS",
        "SOLAR INDUSTRIES": "SOLARINDS.NS",
        "TATA CONSUMER": "TATACONSUM.NS",
        "LG ELECTRONICS": "",
        "TATA POWER": "TATAPOWER.NS",
        "BHARAT PETROLEUM": "BPCL.NS",
        "JSW STEEL": "JSWSTEEL.NS",
        "POWER GRID": "POWERGRID.NS",
        "BAJAJ FINSERV": "BAJAJFINSV.NS",
        "DR. REDDY": "DRREDDY.NS",
        "HCL TECHNOLOGIES": "HCLTECH.NS",
        "POWER FINANCE": "PFC.NS",
        "NESTLE INDIA": "NESTLEIND.NS",
        
        # --- NEW OVERRIDES (FIXING THE PENNY STOCK ANOMALIES) ---
        "TECH MAHINDRA": "TECHM.NS",
        "BALKRISHNA INDUSTRIES": "BALKRISIND.NS",
        "SUPREME INDUSTRIES": "SUPREMEIND.NS",
        "GLOBAL HEALTH": "MEDANTA.NS",
        "KALPATARU": "KPIL.NS",
        "WESTLIFE": "WESTLIFE.NS",
        "V-GUARD": "VGUARD.NS",
        "FLAIR WRITING": "FLAIR.NS",
        
        # --- NEW OVERRIDES FROM AUDIT REPORT 4 (The Long Tail) ---
        "TATA MOTORS PASSENGER": "",  # Unlisted Subsidiary
        "VISHAL MEGA MART": "",       # Unlisted / Pre-IPO
        "TATA CAPITAL": "",           # Unlisted
        "AMBUJA CEMENT": "AMBUJACEM.NS",
        "PIDILITE": "PIDILITIND.NS",
        "HDFC ASSET": "HDFCAMC.NS",
        "ICICI LOMBARD": "ICICIGI.NS",
        "ADANI ENERGY": "ADANIENSOL.NS",
        "GODREJ CONSUMER": "GODREJCP.NS",
        "INFO EDGE": "NAUKRI.NS",
        "PB FINTECH": "POLICYBZR.NS",
        "COAL INDIA": "COALINDIA.NS",
        "INDUSIND BANK": "INDUSINDBK.NS"
    }
    
    for key, ticker in overrides.items():
        if key in name:
            return ticker
            
    # Generic cleaning for the rest
    clean_name = name.replace('LTD.', '').replace('LIMITED', '').replace('(INDIA)', '').replace('COMPANY', '').strip()
    
    # Grab the first continuous block of text as the best guess for the ticker
    first_word = clean_name.split()[0]
    
    # Strip any lingering punctuation
    first_word = ''.join(e for e in first_word if e.isalnum())
    
    return first_word + ".NS"

def run_risk_engine(input_csv, output_csv):
    print("🚀 Initializing Phase 2: Liquidity Risk Engine...")
    
    if not os.path.exists(input_csv):
        print(f"❌ Error: Cannot find {input_csv}. Run Phase 1 first.")
        return
        
    df = pd.read_csv(input_csv)
    print(f"📊 Loaded {len(df)} overlapping stocks. Generating tickers...")
    
    df['Yahoo_Ticker'] = df['Company Name'].apply(guess_nse_ticker)
    
    tickers_to_download = df['Yahoo_Ticker'].unique().tolist()
    print(f"📡 Requesting 90-day market data for {len(tickers_to_download)} tickers from Yahoo Finance...")
    
    # We download all at once because it is much faster than looping one by one
    raw_data = yf.download(tickers_to_download, period="3mo", group_by='ticker', threads=True)
    
    # Dictionaries to hold our calculated metrics
    adv_dict = {}
    price_dict = {}
    amihud_dict = {}
    
    print("🧮 Calculating ADV and Amihud Liquidity measures...")
    
    for ticker in tickers_to_download:
        try:
            # If we only asked for 1 ticker, yfinance returns a normal dataframe.
            # If we asked for many, it returns a MultiIndex dataframe.
            if len(tickers_to_download) == 1:
                stock_df = raw_data
            else:
                stock_df = raw_data[ticker]
                
            # Drop days where the market was closed or data is missing
            stock_df = stock_df.dropna(subset=['Close', 'Volume'])
            
            if len(stock_df) < 10: # If we have almost no data, the ticker guess was probably wrong
                continue
                
            # 1. Current Price
            current_price = stock_df['Close'].iloc[-1]
            
            # 2. 90-Day Average Daily Volume (ADV)
            adv = stock_df['Volume'].mean()
            
            # 3. Amihud Illiquidity Measure
            # Formula: Average of ( |Daily Return| / (Daily Volume * Daily Price) )
            # This calculates how much the stock price moves per $1 (or 1 INR) of trading volume.
            # Higher Amihud score = Highly illiquid (dangerous during a selloff)
            daily_returns = stock_df['Close'].pct_change().abs()
            daily_rupee_volume = stock_df['Volume'] * stock_df['Close']
            
            # Avoid division by zero on days with 0 volume
            amihud_daily = daily_returns / daily_rupee_volume.replace(0, np.nan) 
            amihud_score = amihud_daily.mean()
            
            # Store successful calculations
            price_dict[ticker] = round(current_price, 2)
            adv_dict[ticker] = int(adv)
            amihud_dict[ticker] = amihud_score
            
        except Exception as e:
            # Ticker wasn't found or data was corrupted
            pass

    print("💾 Mapping metrics back to the portfolio dataset...")
    df['Current Price (INR)'] = df['Yahoo_Ticker'].map(price_dict)
    df['90-Day ADV (Shares)'] = df['Yahoo_Ticker'].map(adv_dict)
    df['Amihud Measure'] = df['Yahoo_Ticker'].map(amihud_dict)
    
    # Filter out the rows where our ticker guess failed to find real data
    success_df = df.dropna(subset=['Current Price (INR)'])
    failed_df = df[df['Current Price (INR)'].isna()]
    
    success_rate = len(success_df)
    total_rows = len(df)
    
    df.to_csv(output_csv, index=False)
    
    print("\n" + "="*50)
    print("✅ QUANTITATIVE ENGINE COMPLETE ✅")
    print("="*50)
    print(f"Successfully fetched live data for {success_rate} out of {total_rows} stocks.")
    
    if not failed_df.empty:
        print("\n⚠️ AUDIT REPORT: TICKERS NOT FOUND")
        print("We need to add these to the 'overrides' dictionary at the top of the script:")
        # Print the top 15 failures so you know exactly what to fix
        print(failed_df[['Company Name', 'Yahoo_Ticker']].head(15).to_string(index=False))
        
    print(f"\nThe liquidity metrics have been saved to: {output_csv}")
    print("="*50)

if __name__ == "__main__":
    # Get the exact directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Build absolute paths pointing to the Database folder
    INPUT_FILE = os.path.join(script_dir, "../Database/stock_overlap_report.csv")
    OUTPUT_FILE = os.path.join(script_dir, "../Database/liquidity_risk_report.csv")
    
    run_risk_engine(INPUT_FILE, OUTPUT_FILE)