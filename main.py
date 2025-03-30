import os
import sys
import time
import glob
from datetime import datetime

def print_separator():
    print("\n" + "=" * 80 + "\n")

def print_header(title):
    print_separator()
    print(f"  {title}  ".center(80, "*"))
    print_separator()

def run_script(script_path, script_title):
    """Run a Python script and capture its output"""
    print_header(script_title)
    
    start_time = time.time()
    
    try:
        # Execute the script
        print(f"Running {script_path}...")
        result = os.system(f"python {script_path}")
        
        if result == 0:
            print(f"\n✅ {script_title} completed successfully!")
        else:
            print(f"\n❌ {script_title} failed with exit code {result}")
            return False
    
    except Exception as e:
        print(f"\n❌ Error running {script_title}: {e}")
        return False
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken: {elapsed_time:.2f} seconds")
    
    return True

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        "data/raw",
        "data/cleaned",
        "reports",
        "visualizations"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def find_data_files():
    """Find available data files and update scripts accordingly"""
    # Check what retail data files actually exist
    retail_files = glob.glob("data/raw/*retail*.csv") + glob.glob("data/raw/*retail*.xlsx")
    ecommerce_files = glob.glob("data/raw/*commerce*.csv")
    
    # Print what we found
    print("\nData files found:")
    
    print("\nRetail files:")
    for file in retail_files:
        print(f"- {file}")
    
    print("\nE-commerce files:")
    for file in ecommerce_files:
        print(f"- {file}")
    
    # Update analysis.py to use the files we found
    if os.path.exists("code/analysis.py"):
        print("\nUpdating analysis.py with the correct file paths...")
        
        with open("code/analysis.py", "r") as f:
            content = f.read()
        
        # Replace hardcoded paths with the files we found
        if retail_files and "online_retail" in content:
            retail_path = retail_files[0].replace("\\", "/")
            content = content.replace("../data/raw/online_retail.xlsx", f"../{retail_path}")
            content = content.replace("../data/raw/online_retail_II.csv", f"../{retail_path}")
        
        if ecommerce_files and "e-commerce-data.csv" in content:
            ecommerce_path = ecommerce_files[0].replace("\\", "/")
            content = content.replace("../data/raw/e-commerce-data.csv", f"../{ecommerce_path}")
        
        with open("code/analysis.py", "w") as f:
            f.write(content)
        
        print("✅ analysis.py updated successfully.")
    else:
        print("⚠️ code/analysis.py not found. Cannot update file paths.")
    
    return len(retail_files) > 0 and len(ecommerce_files) > 0

def main():
    """Main function to run the analysis"""
    print_header("ONLINE STORE SALES ANALYSIS")
    
    # Create necessary directories
    create_directories()
    
    # Find and update data file paths
    files_found = find_data_files()
    
    if not files_found:
        print("\n⚠️ Not all required data files were found.")
        print("Please make sure you have at least one retail file (online_retail*.csv/xlsx)")
        print("and one e-commerce file (e_commerce*.csv) in the data/raw directory.")
        return
    
    # Run the analysis script
    run_script("code/analysis.py", "DATA ANALYSIS")
    
    print_header("ANALYSIS COMPLETED")
    print("Check the 'reports' and 'visualizations' directories for results.")

if __name__ == "__main__":
    main()