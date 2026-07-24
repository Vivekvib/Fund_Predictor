import os
import re
import difflib
import pandas as pd
import csv

def consolidate_funds(folder_path, screener_path, output_filename):
    print("🚀 Starting the consolidation process...")

    # 1. Load the screener data
    try:
        screener_df = pd.read_csv(screener_path)
    except FileNotFoundError:
        print(f"❌ Error: Could not find the screener file at {screener_path}")
        return

    # Create a dictionary mapping cleaned fund names to their AUM
    aum_mapping = {}
    for index, row in screener_df.iterrows():
        raw_name = str(row.iloc[0]) # Column A: Funds
        aum_value = pd.to_numeric(row.iloc[1], errors='coerce') # Column B: AUM
        
        # Clean the screener name (remove '(G)' and extra spaces)
        clean_name = raw_name.replace('(G)', '').strip()
        aum_mapping[clean_name] = aum_value

    screener_fund_names = list(aum_mapping.keys())

    # 2. Find all CSV files first to prevent the "empty workbook" error
    csv_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.csv') and f.lower() != os.path.basename(screener_path).lower()]
    
    if len(csv_files) == 0:
        print(f"❌ Error: No fund CSV files found in:")
        print(f"   -> {os.path.abspath(folder_path)}")
        print("Please update the FOLDER_PATH variable at the bottom of the script with your actual folder path.")
        return
        
    # Sort files numerically based on the number at the start of the filename
    def extract_number(filename):
        match = re.match(r'^(\d+)_', filename)
        return int(match.group(1)) if match else 999999
        
    csv_files.sort(key=extract_number)
        
    print(f"📁 Found {len(csv_files)} fund files. Processing data in numerical order...")

    processed_sheets = {}
        
    # 3. Iterate through all valid files FIRST
    for filename in csv_files:
        filepath = os.path.join(folder_path, filename)
        print(f"\n⏳ Reading: {filename}")
        
        # Extract clean fund name from filename
        fund_name_from_file = re.sub(r'^\d+_', '', filename).replace('.csv', '').strip()
        
        # 4. Fuzzy Match the file name to the screener name
        best_match = difflib.get_close_matches(fund_name_from_file, screener_fund_names, n=1, cutoff=0.6)
        
        if best_match:
            matched_screener_name = best_match[0]
            fund_aum = aum_mapping[matched_screener_name]
            print(f"   ✅ Matched: '{matched_screener_name}' -> AUM: {fund_aum} Cr")
        else:
            print(f"   ⚠️ Warning: Could not find AUM match for '{fund_name_from_file}'. Defaulting to 0.")
            fund_aum = 0
            matched_screener_name = fund_name_from_file
            
        try:
            # 5. BULLETPROOF CSV READING
            # Read row by row, enforce a 4-column limit, and filter out the footer
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.reader(f)
                cleaned_data = []
                
                for row in reader:
                    # Combine row text to check for our stopping keywords
                    row_str = ' '.join(row).lower()
                    if 'disclaimer' in row_str or 'statutory details' in row_str:
                        break # We hit the footer, stop reading!
                        
                    # Skip completely empty rows
                    if not any(row):
                        continue
                        
                    cleaned_data.append(row)
            
            if len(cleaned_data) < 2:
                print(f"   ❌ Error: Skipping {filename}. File appears empty.")
                continue
                
            header = cleaned_data[0]
            if len(header) < 4:
                print(f"   ❌ Error: Skipping {filename}. Only found {len(header)} columns in header.")
                continue
                
            # Force every single row to be exactly 4 columns wide
            normalized_data = []
            for row in cleaned_data[1:]:
                # If a row has 9 items, this chops it to 4. 
                # If a row has 2 items, it pads it with 2 empty strings.
                padded_row = row[:4] + [''] * max(0, 4 - len(row))
                normalized_data.append(padded_row)
                
            # Create the DataFrame from our perfectly shaped grid
            fund_df = pd.DataFrame(normalized_data, columns=header[:4])
            
            # --- NEW STEP: Remove the completely empty 3rd column ---
            empty_col_name = fund_df.columns[2]
            fund_df.drop(columns=[empty_col_name], inplace=True)
            
            # 6. Clean up any completely empty rows left behind
            fund_df.dropna(how='all', inplace=True)
            
            # 7. Perform the AUM * Asset % Calculation
            # Since we dropped the empty column, Asset % shifted from index 3 to index 2
            asset_col_name = fund_df.columns[2]
            
            # Ensure the asset column is treated as a number (removes any accidental text/symbols)
            fund_df[asset_col_name] = pd.to_numeric(fund_df[asset_col_name], errors='coerce')
            
            # Math: AUM * (Asset % / 100) = Actual Value in Crores
            fund_df['Investment Value (Cr)'] = fund_aum * (fund_df[asset_col_name] / 100)
            fund_df['Investment Value (Cr)'] = fund_df['Investment Value (Cr)'].round(2)
            
            # 8. Sanitize sheet name
            sheet_name = fund_name_from_file[:31]
            sheet_name = re.sub(r'[\\/*?:\[\]]', '', sheet_name)
            
            # Store the dataframe, AUM, and the full fund name so we can format the Excel sheet later
            processed_sheets[sheet_name] = {'df': fund_df, 'aum': fund_aum, 'full_name': matched_screener_name}
            print(f"   👍 Success.")
            
        except Exception as e:
            print(f"   ❌ Crash while processing {filename}: {e}")
            
    # 9. Write all successful sheets to Excel safely
    if len(processed_sheets) == 0:
        print("\n❌ CRITICAL ERROR: No files were successfully processed. Excel file not created.")
        return
        
    # --- NEW SAVE LOCATION LOGIC ---
    # Determine the Database folder by looking at where screener_path is located
    output_dir = os.path.dirname(screener_path)
    output_path = os.path.join(output_dir, output_filename)
    
    print(f"\n💾 Saving {len(processed_sheets)} sheets to Excel...")
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for sheet_name, data in processed_sheets.items():
            df = data['df']
            aum = data['aum']
            fund_full_name = data['full_name']
            
            # Start writing the dataframe at row index 2 (which is Excel Row 3)
            # This leaves Row 1 and Row 2 completely blank for our custom headers
            df.to_excel(writer, sheet_name=sheet_name, startrow=2, index=False)
            
            # Grab the raw openpyxl worksheet object so we can write into specific cells
            worksheet = writer.sheets[sheet_name]
            
            # Inject the custom headers into A1, A2, and B2
            worksheet['A1'] = fund_full_name
            worksheet['A2'] = "Total AUM (in Cr)"
            worksheet['B2'] = aum
            
    print("\n" + "="*50)
    print("🎉 CONSOLIDATION COMPLETE 🎉")
    print("="*50)
    print(f"Your master file is saved at: {output_path}")

if __name__ == "__main__":
    # USING RELATIVE PATHS
    # These paths assume you are running the script from inside the 'Codes' folder.
    
    # 1. The folder where all 34 numbered CSV files are kept
    FOLDER_PATH = "../Database/Small_Cap_Funds" 
    
    # 2. The exact path to your screener file
    SCREENER_FILE = "../Database/screener.csv"
    
    # 3. The name of the final Excel file that will be generated
    OUTPUT_EXCEL = "Master_Consolidated_Funds.xlsx"
    
    consolidate_funds(FOLDER_PATH, SCREENER_FILE, OUTPUT_EXCEL)