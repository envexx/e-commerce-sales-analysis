import pandas as pd
import os
from datetime import datetime

# Create directories if they don't exist
os.makedirs("data/cleaned", exist_ok=True)

def standardize_columns(df, dataset_name):
    """Standardize column names and formats across datasets"""
    print(f"Standardizing columns for {dataset_name}...")
    
    # Make a copy to avoid modifying the original
    std_df = df.copy()
    
    # Standardize column names (lowercase and replace spaces with underscores)
    std_df.columns = [col.lower().replace(' ', '_') for col in std_df.columns]
    
    # Convert column types as needed
    if 'customerid' in std_df.columns:
        std_df['customerid'] = std_df['customerid'].astype(str)
    
    if 'invoiceno' in std_df.columns:
        std_df['invoiceno'] = std_df['invoiceno'].astype(str)
    
    # Add source column to track which dataset the row came from
    std_df['data_source'] = dataset_name
    
    # Print the standardized columns
    print(f"Standardized columns: {list(std_df.columns)}")
    
    return std_df

def merge_datasets():
    """Merge the cleaned datasets"""
    # List of cleaned datasets
    datasets = [
        {"path": "data/cleaned/e-commerce-data_clean.csv", "name": "e-commerce"},
        {"path": "data/cleaned/online_retail_xlsx_clean.csv", "name": "online_retail_xlsx"},
        {"path": "data/cleaned/online_retail_II_clean.csv", "name": "online_retail_II"}
    ]
    
    all_dfs = []
    
    # Read and standardize each dataset
    for dataset in datasets:
        try:
            print(f"\nProcessing {dataset['name']}...")
            
            # Read the cleaned dataset
            df = pd.read_csv(dataset["path"])
            print(f"Shape: {df.shape}")
            
            # Standardize column names and formats
            std_df = standardize_columns(df, dataset["name"])
            
            # Add to list for merging
            all_dfs.append(std_df)
            
        except Exception as e:
            print(f"\nError processing {dataset['name']}: {e}")
    
    if not all_dfs:
        print("No dataframes to merge. Check if cleaned files exist.")
        return None
    
    print("\n\nMerging datasets...")
    
    # Check the columns in each dataframe to identify common columns
    common_columns = set.intersection(*[set(df.columns) for df in all_dfs])
    common_columns.discard('data_source')  # Remove the source column from consideration
    
    print(f"Common columns across all datasets: {common_columns}")
    
    # Define essential columns that should be present in the merged dataset
    essential_columns = ['invoiceno', 'invoicedate', 'customerid', 'quantity', 'unitprice', 'country']
    
    # Check which essential columns are missing from common columns
    missing_cols = [col for col in essential_columns if col not in common_columns]
    if missing_cols:
        print(f"Warning: The following essential columns are not common across all datasets: {missing_cols}")
        print("Will attempt to include them in the merged dataset where available.")
    
    # Create a merged dataset
    # Strategy: Include all columns from all datasets, even if they don't appear in all datasets
    # This will result in NaN values for rows from datasets that don't have certain columns
    
    # Get a list of all unique columns across all dataframes
    all_columns = set()
    for df in all_dfs:
        all_columns.update(df.columns)
    
    print(f"All columns across datasets: {all_columns}")
    
    # For each dataframe, add missing columns with NaN values
    for i, df in enumerate(all_dfs):
        missing = all_columns - set(df.columns)
        for col in missing:
            all_dfs[i][col] = pd.NA
    
    # Concatenate all dataframes
    merged_df = pd.concat(all_dfs, ignore_index=True)
    
    print(f"Shape of merged dataset: {merged_df.shape}")
    
    # Save the merged dataset
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"data/cleaned/combined_sales_data_{timestamp}.csv"
    merged_df.to_csv(output_path, index=False)
    
    print(f"Merged dataset saved to: {output_path}")
    
    return merged_df

if __name__ == "__main__":
    merge_datasets()