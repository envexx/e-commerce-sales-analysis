import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import glob
from datetime import datetime

# Set plot style - menggunakan style yang pasti tersedia
plt.style.use('default')  # Menggunakan default style alih-alih 'seaborn'
sns.set()  # Menggunakan pengaturan default seaborn

# Create directories if they don't exist
os.makedirs("../data/cleaned", exist_ok=True)
os.makedirs("../reports", exist_ok=True)
os.makedirs("../visualizations", exist_ok=True)

def print_separator():
    print("\n" + "=" * 80 + "\n")

def print_header(title):
    print_separator()
    print(f"  {title}  ".center(80, "*"))
    print_separator()

def find_data_files():
    """Find all available data files"""
    # Cari file data dengan path absolut (digunakan untuk debugging)
    current_dir = os.path.abspath(os.path.dirname(__file__))
    parent_dir = os.path.dirname(current_dir)
    raw_data_dir = os.path.join(parent_dir, "data", "raw")
    
    print(f"Looking for data files in: {raw_data_dir}")
    
    # Find retail files menggunakan path absolut
    retail_files = glob.glob(os.path.join(raw_data_dir, "*retail*.csv")) + \
                   glob.glob(os.path.join(raw_data_dir, "*retail*.xlsx"))
                   
    # Find e-commerce files menggunakan path absolut
    ecommerce_files = glob.glob(os.path.join(raw_data_dir, "*commerce*.csv"))
    
    files = []
    
    # Add retail files
    for file in retail_files:
        file_type = "xlsx" if file.endswith(".xlsx") else "csv"
        files.append({"path": file, "name": os.path.basename(file), "type": file_type})
    
    # Add e-commerce files
    for file in ecommerce_files:
        files.append({"path": file, "name": os.path.basename(file), "type": "csv"})
    
    return files

def examine_dataset(file_info):
    """Examine a dataset and display basic information"""
    print_header(f"EXAMINING: {file_info['name']}")
    
    try:
        # Read the dataset
        if file_info["type"] == "xlsx":
            df = pd.read_excel(file_info["path"])
        else:
            df = pd.read_csv(file_info["path"], encoding='latin1', on_bad_lines='skip')
        
        # Display basic information
        print(f"Shape: {df.shape}")
        
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
    
    except Exception as e:
        print(f"Error examining dataset: {e}")
        return None

def clean_dataset(df, dataset_name):
    """Clean and prepare the dataset for analysis"""
    print_header(f"CLEANING: {dataset_name}")
    
    if df is None:
        print("No dataset to clean.")
        return None
    
    # Make a copy to avoid modifying the original
    df_clean = df.copy()
    
    print(f"Original shape: {df_clean.shape}")
    
    # Standardize column names (lowercase)
    df_clean.columns = [str(col).lower().strip() for col in df_clean.columns]
    
    # Common column mappings for different dataset formats
    column_mappings = {
        'customer id': 'customerid',
        'customer_id': 'customerid',
        'invoice no': 'invoiceno', 
        'invoice_no': 'invoiceno',
        'invoice': 'invoiceno',
        'stock code': 'stockcode',
        'stock_code': 'stockcode',
        'unit price': 'unitprice',
        'unit_price': 'unitprice',
        'invoice date': 'invoicedate',
        'invoice_date': 'invoicedate',
        'order date': 'invoicedate',
        'order_date': 'invoicedate'
    }
    
    # Rename columns based on mappings
    df_clean = df_clean.rename(columns=lambda x: column_mappings.get(x.lower(), x.lower()))
    
    # Handle missing values
    if 'customerid' in df_clean.columns:
        # Handle CustomerID
        if df_clean['customerid'].dtype == 'object':
            df_clean['customerid'] = df_clean['customerid'].astype(str)
            df_clean['customerid'] = df_clean['customerid'].replace('nan', np.nan)
        
        missing_customer_id = df_clean['customerid'].isna().sum()
        if missing_customer_id > 0:
            print(f"Found {missing_customer_id} rows with missing CustomerID")
            # We'll keep rows with missing CustomerID for now
    
    # Handle quantity and price issues
    if 'quantity' in df_clean.columns:
        # Remove negative or zero quantities
        neg_qty = (df_clean['quantity'] <= 0).sum()
        if neg_qty > 0:
            print(f"Removing {neg_qty} rows with negative or zero Quantity")
            df_clean = df_clean[df_clean['quantity'] > 0]
    
    if 'unitprice' in df_clean.columns:
        # Remove negative or zero prices
        neg_price = (df_clean['unitprice'] <= 0).sum()
        if neg_price > 0:
            print(f"Removing {neg_price} rows with negative or zero UnitPrice")
            df_clean = df_clean[df_clean['unitprice'] > 0]
    
    # Handle canceled transactions
    if 'invoiceno' in df_clean.columns:
        # Convert to string if not already
        df_clean['invoiceno'] = df_clean['invoiceno'].astype(str)
        
        # Remove canceled transactions (usually start with 'C')
        canceled = df_clean['invoiceno'].str.startswith('C', na=False).sum()
        if canceled > 0:
            print(f"Removing {canceled} canceled transactions (InvoiceNo starting with 'C')")
            df_clean = df_clean[~df_clean['invoiceno'].str.startswith('C', na=False)]
    
    # Convert InvoiceDate to datetime
    if 'invoicedate' in df_clean.columns:
        try:
            df_clean['invoicedate'] = pd.to_datetime(df_clean['invoicedate'], errors='coerce')
            print("Converted InvoiceDate to datetime format")
        except:
            print("Failed to convert InvoiceDate to datetime")
    
    # Add derived columns
    if all(col in df_clean.columns for col in ['quantity', 'unitprice']):
        # Calculate total price
        df_clean['totalprice'] = df_clean['quantity'] * df_clean['unitprice']
        print("Added TotalPrice column (Quantity * UnitPrice)")
    
    # Add source column to track origin
    df_clean['data_source'] = dataset_name
    
    # Final shape
    print(f"Final shape after cleaning: {df_clean.shape}")
    
    # Mendapatkan path untuk file cleaned
    current_dir = os.path.abspath(os.path.dirname(__file__))
    parent_dir = os.path.dirname(current_dir)
    clean_file = os.path.join(parent_dir, "data", "cleaned", f"{dataset_name.split('.')[0]}_clean.csv")
    
    # Save cleaned dataset
    df_clean.to_csv(clean_file, index=False)
    print(f"Saved cleaned dataset to {clean_file}")
    
    return df_clean

def merge_datasets(cleaned_dfs):
    """Merge multiple cleaned datasets"""
    print_header("MERGING DATASETS")
    
    if not cleaned_dfs:
        print("No datasets to merge.")
        return None
    
    # Filter out None values
    cleaned_dfs = [df for df in cleaned_dfs if df is not None]
    
    if not cleaned_dfs:
        print("No valid datasets to merge.")
        return None
    
    # Find common columns
    all_columns = set()
    for df in cleaned_dfs:
        all_columns.update(df.columns)
    
    print(f"All columns across datasets: {all_columns}")
    
    # Ensure all dataframes have the same columns
    for i, df in enumerate(cleaned_dfs):
        for col in all_columns:
            if col not in df.columns:
                cleaned_dfs[i][col] = None
    
    # Concatenate all dataframes
    merged_df = pd.concat(cleaned_dfs, ignore_index=True)
    
    print(f"Shape of merged dataset: {merged_df.shape}")
    
    # Mendapatkan path untuk file merged
    current_dir = os.path.abspath(os.path.dirname(__file__))
    parent_dir = os.path.dirname(current_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    merged_file = os.path.join(parent_dir, "data", "cleaned", f"combined_sales_data_{timestamp}.csv")
    
    # Save merged dataset
    merged_df.to_csv(merged_file, index=False)
    print(f"Saved merged dataset to {merged_file}")
    
    return merged_df

def analyze_data(df):
    """Perform comprehensive analysis on the merged dataset"""
    print_header("ANALYZING DATA")
    
    if df is None:
        print("No dataset to analyze.")
        return
    
    # Mendapatkan paths untuk folder reports dan visualizations
    current_dir = os.path.abspath(os.path.dirname(__file__))
    parent_dir = os.path.dirname(current_dir)
    reports_dir = os.path.join(parent_dir, "reports")
    viz_dir = os.path.join(parent_dir, "visualizations")
    
    # Memastikan folder ada
    os.makedirs(reports_dir, exist_ok=True)
    os.makedirs(viz_dir, exist_ok=True)
    
    # Basic statistics
    print("\n=== Basic Statistics ===")
    
    # Total sales
    if 'totalprice' in df.columns:
        total_sales = df['totalprice'].sum()
        print(f"Total Sales: {total_sales:,.2f}")
    else:
        total_sales = 'N/A'
        print("TotalPrice column not found")
    
    # Number of transactions
    if 'invoiceno' in df.columns:
        num_transactions = df['invoiceno'].nunique()
        print(f"Number of Unique Transactions: {num_transactions:,}")
    else:
        num_transactions = 'N/A'
        print("InvoiceNo column not found")
    
    # Number of customers
    if 'customerid' in df.columns:
        num_customers = df['customerid'].nunique()
        print(f"Number of Unique Customers: {num_customers:,}")
    else:
        num_customers = 'N/A'
        print("CustomerID column not found")
    
    # Number of products
    if 'description' in df.columns:
        num_products = df['description'].nunique()
        print(f"Number of Unique Products: {num_products:,}")
    else:
        num_products = 'N/A'
        print("Description column not found")
    
    # Number of countries
    if 'country' in df.columns:
        num_countries = df['country'].nunique()
        print(f"Number of Countries: {num_countries}")
    else:
        num_countries = 'N/A'
        print("Country column not found")
    
    # Date range
    if 'invoicedate' in df.columns and pd.api.types.is_datetime64_dtype(df['invoicedate']):
        min_date = df['invoicedate'].min()
        max_date = df['invoicedate'].max()
        print(f"Date Range: {min_date} to {max_date}")
        date_range = f"{min_date} to {max_date}"
    else:
        date_range = 'N/A'
        print("InvoiceDate column not found or not in datetime format")
    
    # Save basic statistics to CSV
    stats = {
        'Metric': ['Total Sales', 'Transactions', 'Customers', 'Products', 'Countries', 'Date Range'],
        'Value': [
            f"{total_sales:,.2f}" if isinstance(total_sales, (int, float)) else total_sales,
            f"{num_transactions:,}" if isinstance(num_transactions, (int, float)) else num_transactions,
            f"{num_customers:,}" if isinstance(num_customers, (int, float)) else num_customers,
            f"{num_products:,}" if isinstance(num_products, (int, float)) else num_products,
            f"{num_countries}" if isinstance(num_countries, (int, float)) else num_countries,
            date_range
        ]
    }
    stats_file = os.path.join(reports_dir, "basic_statistics.csv")
    pd.DataFrame(stats).to_csv(stats_file, index=False)
    print(f"Saved basic statistics to {stats_file}")
    
    # Time-based analysis
    if 'invoicedate' in df.columns and pd.api.types.is_datetime64_dtype(df['invoicedate']):
        print("\n=== Time-Based Analysis ===")
        
        # Add time components
        df['year'] = df['invoicedate'].dt.year
        df['month'] = df['invoicedate'].dt.month
        df['day'] = df['invoicedate'].dt.day
        df['dayofweek'] = df['invoicedate'].dt.dayofweek
        if 'hour' not in df.columns and df['invoicedate'].dt.hour.nunique() > 1:
            df['hour'] = df['invoicedate'].dt.hour
        
        # Monthly sales
        if 'totalprice' in df.columns:
            monthly_sales = df.groupby([df['year'], df['month']])['totalprice'].sum().reset_index()
            monthly_sales['month_name'] = monthly_sales['month'].apply(lambda x: datetime(2000, x, 1).strftime('%b'))
            monthly_sales['period'] = monthly_sales['year'].astype(str) + '-' + monthly_sales['month_name']
            
            # Plot monthly sales
            plt.figure(figsize=(15, 6))
            plt.plot(monthly_sales['period'], monthly_sales['totalprice'], marker='o', linestyle='-')
            plt.title('Monthly Sales Trend', fontsize=16)
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Total Sales', fontsize=12)
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Save monthly sales chart
            monthly_sales_chart = os.path.join(viz_dir, "monthly_sales_trend.png")
            plt.savefig(monthly_sales_chart)
            print(f"Saved monthly sales trend chart to {monthly_sales_chart}")
            
            # Save monthly sales data
            monthly_sales_data = os.path.join(reports_dir, "monthly_sales.csv")
            monthly_sales.to_csv(monthly_sales_data, index=False)
            print(f"Saved monthly sales data to {monthly_sales_data}")
        
        # Day of week analysis
        if 'totalprice' in df.columns:
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            daily_sales = df.groupby('dayofweek')['totalprice'].sum().reset_index()
            daily_sales['day_name'] = daily_sales['dayofweek'].apply(lambda x: day_names[x])
            
            # Plot daily sales
            plt.figure(figsize=(12, 6))
            plt.bar(daily_sales['day_name'], daily_sales['totalprice'])
            plt.title('Sales by Day of Week', fontsize=16)
            plt.xlabel('Day', fontsize=12)
            plt.ylabel('Total Sales', fontsize=12)
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            
            # Save day of week chart
            daily_sales_chart = os.path.join(viz_dir, "sales_by_day.png")
            plt.savefig(daily_sales_chart)
            print(f"Saved day of week sales chart to {daily_sales_chart}")
            
            # Save daily sales data
            daily_sales_data = os.path.join(reports_dir, "daily_sales.csv")
            daily_sales.to_csv(daily_sales_data, index=False)
            print(f"Saved daily sales data to {daily_sales_data}")
    
    # Product analysis
    if all(col in df.columns for col in ['description', 'totalprice']):
        print("\n=== Product Analysis ===")
        
        # Top products by revenue
        top_products = df.groupby('description')['totalprice'].sum().reset_index()
        top_products = top_products.sort_values('totalprice', ascending=False).head(10)
        
        # Plot top products
        plt.figure(figsize=(14, 8))
        plt.barh(top_products['description'], top_products['totalprice'])
        plt.title('Top 10 Products by Revenue', fontsize=16)
        plt.xlabel('Total Revenue', fontsize=12)
        plt.ylabel('Product', fontsize=12)
        plt.gca().invert_yaxis()  # Highest value at top
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        
        # Save top products chart
        top_products_chart = os.path.join(viz_dir, "top_products.png")
        plt.savefig(top_products_chart)
        print(f"Saved top products chart to {top_products_chart}")
        
        # Save top products data
        top_products_data = os.path.join(reports_dir, "top_products.csv")
        top_products.to_csv(top_products_data, index=False)
        print(f"Saved top products data to {top_products_data}")
    
    # Country analysis
    if all(col in df.columns for col in ['country', 'totalprice']):
        print("\n=== Country Analysis ===")
        
        # Sales by country
        country_sales = df.groupby('country')['totalprice'].sum().reset_index()
        country_sales = country_sales.sort_values('totalprice', ascending=False).head(10)
        
        # Plot top countries
        plt.figure(figsize=(12, 6))
        plt.bar(country_sales['country'], country_sales['totalprice'])
        plt.title('Top 10 Countries by Sales', fontsize=16)
        plt.xlabel('Country', fontsize=12)
        plt.ylabel('Total Sales', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        # Save top countries chart
        country_sales_chart = os.path.join(viz_dir, "top_countries.png")
        plt.savefig(country_sales_chart)
        print(f"Saved top countries chart to {country_sales_chart}")
        
        # Save country data
        country_sales_data = os.path.join(reports_dir, "country_sales.csv")
        country_sales.to_csv(country_sales_data, index=False)
        print(f"Saved country sales data to {country_sales_data}")
    
    print("\nAnalysis completed successfully!")

def main():
    """Main function to run the complete analysis pipeline"""
    print_header("ONLINE STORE SALES ANALYSIS")
    
    # Find available data files
    data_files = find_data_files()
    
    if not data_files:
        print("No data files found. Please add data files to the data/raw directory.")
        return
    
    print(f"Found {len(data_files)} data files:")
    for file in data_files:
        print(f"- {file['name']} ({file['type']})")
    
    # Process each file
    cleaned_dfs = []
    
    for file in data_files:
        # Examine dataset
        df = examine_dataset(file)
        
        # Clean dataset
        if df is not None:
            df_clean = clean_dataset(df, file['name'])
            cleaned_dfs.append(df_clean)
    
    # Merge datasets
    merged_df = merge_datasets(cleaned_dfs)
    
    # Analyze data
    if merged_df is not None:
        analyze_data(merged_df)
    
    print_header("ANALYSIS COMPLETED")
    print("Check the 'reports' and 'visualizations' directories for results.")

if __name__ == "__main__":
    main()