import pandas as pd
import os
from collections import defaultdict

def is_equity(asset_name):
    """Filters out debt, government securities, and cash equivalents."""
    if not isinstance(asset_name, str):
        return False
        
    # Keywords that usually indicate non-stock assets
    exclusions = [
        "GOI", "Treasury Bill", "T-Bill", "State Government", "SDL",
        "CBLO", "TREPS", "Net Current Asset", "Cash Margin", "Repo",
        "Clearing Corporation", "Debenture", "Bonds", "Liquid", "0.",
        "Grand Total", "Instrument", "Total", "Net Asset"
    ]
    
    name_upper = asset_name.upper()
    for word in exclusions:
        if word.upper() in name_upper:
            return False
    return True

def get_unique_stocks(excel_path):
    if not os.path.exists(excel_path):
        print(f"❌ Error: Could not find the master file at {excel_path}")
        return

    print(f"📂 Loading {excel_path}... This might take a few seconds.")
    
    # Read ALL sheets into a dictionary of DataFrames
    # skiprows=2 tells Pandas to ignore our custom A1/A2 headers and look at the real table headers
    all_sheets = pd.read_excel(excel_path, sheet_name=None, skiprows=2)
    
    # Dictionary to hold Stock -> List of Funds
    stock_fund_map = defaultdict(list)
    stock_sector_map = {} # NEW: Dictionary to hold Stock -> Sector
    total_holdings_parsed = 0
    
    for sheet_name, df in all_sheets.items():
        # Ensure the sheet isn't completely empty and has at least 2 columns (for Company & Sector)
        if not df.empty and len(df.columns) >= 2:
            
            # Iterate through row by row to get both company and sector
            for index, row in df.iterrows():
                stock_str = str(row.iloc[0]).strip()
                sector_str = str(row.iloc[1]).strip()
                
                # Only add to our list if it passes our equity filter
                if len(stock_str) > 1 and is_equity(stock_str):
                    # Check to avoid duplicates if a fund listed a stock twice somehow
                    if sheet_name not in stock_fund_map[stock_str]:
                        stock_fund_map[stock_str].append(sheet_name)
                        
                    # Save the sector if we haven't mapped it yet
                    if stock_str not in stock_sector_map and sector_str.lower() not in ['nan', 'none', '']:
                        stock_sector_map[stock_str] = sector_str
                        
            total_holdings_parsed += len(df)
            
    # --- Create the Overlap Report ---
    report_data = []
    for stock, funds in stock_fund_map.items():
        report_data.append({
            "Company Name": stock,
            "Sector": stock_sector_map.get(stock, "Unknown Sector"), # NEW: Add the Sector
            "Number of Funds": len(funds),
            "Funds Holding This Stock": ", ".join(funds) # Comma separated list of funds
        })
        
    # Convert to DataFrame and sort by most widely held stock (descending)
    report_df = pd.DataFrame(report_data)
    report_df = report_df.sort_values(by="Number of Funds", ascending=False)
            
    print("\n" + "="*50)
    print("📊 STOCK UNIVERSE & OVERLAP AUDIT 📊")
    print("="*50)
    print(f"Total individual rows parsed across funds: {total_holdings_parsed}")
    print(f"🎯 TOTAL UNIQUE PURE EQUITIES: {len(report_df)}")
    print("="*50)
    
    output_dir = os.path.dirname(excel_path)
    output_file = os.path.join(output_dir, "stock_overlap_report.csv")
    
    # Save the detailed report
    report_df.to_csv(output_file, index=False)
    print(f"\n💾 Saved the detailed Stock Overlap Report to: {output_file}")
    
    print("\n🏆 Top 5 most widely held stocks in your universe:")
    print(report_df.head(5).to_string(index=False, columns=["Company Name", "Number of Funds"]))

if __name__ == "__main__":
    # ⚠️ IMPORTANT: Update this to match exactly where you saved the master file yesterday
    MASTER_EXCEL_FILE = "../Database/Master_Consolidated_Funds.xlsx"
    
    get_unique_stocks(MASTER_EXCEL_FILE)