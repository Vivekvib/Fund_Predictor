import os
import hashlib

def get_file_hash(filepath):
    """
    Reads the actual contents of the file and generates a unique SHA-256 fingerprint.
    """
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as file:
        # Read in chunks just in case the files are large
        buf = file.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = file.read(65536)
    return hasher.hexdigest()

def clean_duplicates(folder_path):
    if not os.path.exists(folder_path):
        print(f"Error: The folder '{folder_path}' does not exist.")
        print("Please update the TARGET_FOLDER variable with your actual folder path.")
        return

    seen_hashes = {}
    deleted_files = []
    
    print(f"Scanning folder: {folder_path}\n")

    # Loop through every item in the folder
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        
        # Ensure we are only checking files, not sub-folders
        if os.path.isfile(filepath):
            file_hash = get_file_hash(filepath)
            
            if file_hash in seen_hashes:
                # We found a matching fingerprint! It's a duplicate.
                original_file = seen_hashes[file_hash]
                print(f"🗑️ Deleting duplicate: '{filename}' (Matches: '{os.path.basename(original_file)}')")
                
                # Delete the duplicate file
                os.remove(filepath)
                deleted_files.append(filename)
            else:
                # This is a unique file. Save its fingerprint and path.
                seen_hashes[file_hash] = filepath

    # --- Post-Cleanup Audit ---
    remaining_files = len(seen_hashes)
    print("\n" + "="*50)
    print("🧹 CLEANUP COMPLETE 🧹")
    print("="*50)
    print(f"Total duplicate files deleted: {len(deleted_files)}")
    print(f"Unique files remaining: {remaining_files}")
    
    # Check against your target of 34 funds
    if remaining_files == 34:
        print("\n✅ TARGET REACHED: You have exactly 34 unique files left. You didn't miss any!")
    elif remaining_files < 34:
        missing_count = 34 - remaining_files
        print(f"\n⚠️ SHORTFALL: You only have {remaining_files} unique files.")
        print(f"You actually missed {missing_count} fund(s) during your initial download.")
    else:
        print(f"\n⚠️ OVERSHOOT: You have {remaining_files} unique files.")
        print("This means you downloaded more than 34 unique funds, or some files are entirely different datasets.")

if __name__ == "__main__":
    # ⚠️ IMPORTANT: Change this string to the exact path where your 39 files are located
    # For Windows, it might look like: r"C:\Users\YourName\Downloads\FundPortfolios"
    # For Mac/Linux, it might look like: "/Users/YourName/Downloads/FundPortfolios"
    TARGET_FOLDER = "../DatabaseSmall_Cap_Funds" 
    
    clean_duplicates(TARGET_FOLDER)