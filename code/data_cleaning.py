import pandas as pd
import numpy as np
import os
from datetime import datetime

# Create directories if they don't exist
os.makedirs("data/cleaned", exist_ok=True)

# Function to clean e-commerce datasets
def clean_dataset(df, dataset_name):
    print(f"\n{'='*50}")
    print(f"Cleaning: {dataset_name}")
    print(f"{'='*50}")
    
    # Make a copy of the dataframe to avoid modifying the original
    df_clean = df.copy()
    
    print(f"Original shape: {df_clean.shape}")
    
    # 1. Handle missing values
    # Check if CustomerID exists in the dataframe
    if 'CustomerID' in df_clean.columns:
        # Convert CustomerID to string if it's not already
        df_clean['CustomerID'] = df_clean['CustomerID'].astype(str)
        # Replace 'nan' strings with np.nan
        df_clean['CustomerID'] = df_clean['CustomerID'].replace('nan', np.nan)
        # Drop rows with missing CustomerID (important for customer analysis)
        missing_customer_id = df_clean['CustomerID'].isna().sum()
        df_clean.dropna(subset=['CustomerID'], inplace=True)
        print(f"Dropped {missing_customer_id} rows with missing CustomerID")
    
    # 2. Handle quantity and price issues
    if 'Quantity' in df_clean.columns:
        # Remove negative or zero quantities
        negative_qty = (df_clean['Quantity'] <= 0).sum()
        df_clean = df_clean[df_clean['Quantity'] > 0]
        print(f"Removed {negative_qty} rows with negative or zero Quantity")
    
    if 'UnitPrice' in df_clean.columns:
        # Remove negative or zero prices
        negative_price = (df_clean['UnitPrice'] <= 0).sum()
        df_clean = df_clean[df_clean['UnitPrice'] > 0]
        print(f"Removed {negative_price} rows with negative or zero UnitPrice")
    
    # 3. Handle canceled transactions (InvoiceNo starting with 'C')
    if 'InvoiceNo' in df_clean.columns:
        # Convert InvoiceNo to string if it's not already
        df_clean['InvoiceNo'] = df_clean['InvoiceNo'].astype(str)
        # Count and remove canceled transactions
        canceled = df_clean['InvoiceNo'].str.startswith('C', na=False).sum()
        df_clean = df_clean[~df_clean['InvoiceNo'].str.startswith('C', na=False)]
        print(f"Removed {canceled} canceled transactions (InvoiceNo starting with 'C')")
    
    # 4. Convert InvoiceDate to datetime format
    if 'InvoiceDate' in df_clean.columns:
        try:
            df_clean['InvoiceDate'] = pd.to_datetime(df_clean['InvoiceDate'])
        except Exception as e:
            print(f"Error converting InvoiceDate to datetime: {e}")
            print("Trying alternative date format...")
            try:
                df_clean['InvoiceDate'] = pd.to_datetime(df_clean['InvoiceDate'], format='%m/%d/%Y %H:%M')
            except Exception as e2:
                print(f"Still couldn't convert date: {e2}")
                print("Will keep original format.")
    
    # 5. Add derived columns for analysis
    if all(col in df_clean.columns for col in ['Quantity', 'UnitPrice']):
        # Calculate total price per transaction line
        df_clean['TotalPrice'] = df_clean['Quantity'] * df_clean['UnitPrice']
        print("Added TotalPrice column (Quantity * UnitPrice)")
    
    if 'InvoiceDate' in df_clean.columns and pd.api.types.is_datetime64_dtype(df_clean['InvoiceDate']):
        # Add year, month, day, hour for time-based analysis
        df_clean['Year'] = df_clean['InvoiceDate'].dt.year
        df_clean['Month'] = df_clean['InvoiceDate'].dt.month
        df_clean['Day'] = df_clean['InvoiceDate'].dt.day
        df_clean['Hour'] = df_clean['InvoiceDate'].dt.hour
        print("Added Year, Month, Day, Hour columns from InvoiceDate")
    
    # 6. Drop remaining rows with missing data in key columns
    key_columns = [col for col in ['Description', 'Quantity', 'UnitPrice'] if col in df_clean.columns]
    if key_columns:
        missing_key = df_clean[key_columns].isna().any(axis=1).sum()
        df_clean.dropna(subset=key_columns, inplace=True)
        print(f"Dropped {missing_key} rows with missing data in key columns: {key_columns}")
    
    print(f"Final shape after cleaning: {df_clean.shape}")
    
    return df_clean

# Main processing
def main():
    # List of datasets
    datasets = [
        {"path": "data/raw/e_commerce_data.csv", "name": "e-commerce-data"},
        {"path": "data/raw/online-retail.xlsx", "name": "online_retail_xlsx"},
        {"path": "data/raw/online_retail_II.csv", "name": "online_retail_II"}
    ]
    
    cleaned_dfs = []
    
    # Clean each dataset
    for dataset in datasets:
        try:
            print(f"\nProcessing {dataset['name']}...")
            
            # Read the dataset
            if dataset["path"].endswith('.xlsx'):
                df = pd.read_excel(dataset["path"])
            else:
                df = pd.read_csv(dataset["path"], encoding='latin1')
            
            # Clean the dataset
            df_clean = clean_dataset(df, dataset["name"])
            
            # Save cleaned dataset
            output_path = f"data/cleaned/{dataset['name']}_clean.csv"
            df_clean.to_csv(output_path, index=False)
            print(f"Saved cleaned dataset to {output_path}")
            
            # Add to list of cleaned dataframes for merging
            cleaned_dfs.append(df_clean)
            
        except Exception as e:
            print(f"\nError processing {dataset['name']}: {e}")
    
    print("\nCleaning process completed!")
    return cleaned_dfs

if __name__ == "__main__":
    main()