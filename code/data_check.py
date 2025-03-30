import pandas as pd
import os

# Create directories if they don't exist
os.makedirs("data/cleaned", exist_ok=True)

# Function to display dataset information
def examine_dataset(file_path, file_name):
    print(f"\n{'='*50}")
    print(f"Examining: {file_name}")
    print(f"{'='*50}")
    
    # Read the dataset with appropriate method
    if file_name.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path, encoding='latin1')
    
    # Display basic information
    print(f"\nShape: {df.shape}")
    print("\nColumn names:")
    for col in df.columns:
        print(f"- {col}")
    
    print("\nData types:")
    print(df.dtypes)
    
    print("\nSample data (first 5 rows):")
    print(df.head())
    
    print("\nMissing values:")
    print(df.isnull().sum())
    
    print("\nBasic statistics:")
    print(df.describe())
    
    return df

# List of datasets
datasets = [
    {"path": "data/raw/e_commerce_data.csv", "name": "e-commerce-data.csv"},
    {"path": "data/raw/online-retail.xlsx", "name": "online_retail.xlsx"},
    {"path": "data/raw/online_retail_II.csv", "name": "online_retail_II.csv"}
]

# Examine each dataset
for dataset in datasets:
    try:
        examine_dataset(dataset["path"], dataset["name"])
    except Exception as e:
        print(f"\nError processing {dataset['name']}: {e}")

print("\nExamination complete!")