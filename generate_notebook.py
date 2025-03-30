import nbformat as nbf

# Create a new notebook
nb = nbf.v4.new_notebook()

# Import libraries cell
imports = """
# Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import glob
from datetime import datetime

# Set plot style
plt.style.use('default')
plt.rcParams['figure.figsize'] = [12, 6]
sns.set()

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')
"""

# Load data cell
load_data = """
# Find the most recent combined data file
combined_files = glob.glob("data/cleaned/combined_sales_data_*.csv")

if not combined_files:
    print("No combined dataset found. Run the main analysis script first.")
else:
    # Load the most recent file
    latest_file = max(combined_files, key=os.path.getmtime)
    print(f"Loading dataset: {latest_file}")
    
    # Load the dataset
    df = pd.read_csv(latest_file)
    
    # Convert date to datetime
    if 'invoicedate' in df.columns:
        df['invoicedate'] = pd.to_datetime(df['invoicedate'])
        # Extract date components
        df['year'] = df['invoicedate'].dt.year
        df['month'] = df['invoicedate'].dt.month
        df['day'] = df['invoicedate'].dt.day
        df['dayofweek'] = df['invoicedate'].dt.dayofweek
        df['dayname'] = df['invoicedate'].dt.day_name()
        df['year_month'] = df['invoicedate'].dt.strftime('%Y-%m')
    
    # Preview the data
    print("Data preview:")
    display(df.head())
    print(f"Shape: {df.shape}")
"""

# Sales overview cell
sales_overview = """
if 'df' in globals():
    # Calculate key metrics
    total_sales = df['totalprice'].sum()
    total_orders = df['invoiceno'].nunique()
    
    # Display metrics
    print(f"Total Sales: ${total_sales:,.2f}")
    print(f"Number of Orders: {total_orders:,}")
    
    if 'customerid' in df.columns:
        total_customers = df['customerid'].nunique()
        print(f"Number of Customers: {total_customers:,}")
    
    # Monthly sales trend
    if 'year_month' in df.columns:
        monthly_sales = df.groupby('year_month')['totalprice'].sum().reset_index()
        monthly_sales = monthly_sales.sort_values('year_month')
        
        plt.figure(figsize=(14, 6))
        plt.plot(monthly_sales['year_month'], monthly_sales['totalprice'], marker='o')
        plt.title("Monthly Sales Trend", fontsize=16)
        plt.xlabel("Month")
        plt.ylabel("Sales ($)")
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
"""

# Product analysis cell
product_analysis = """
if 'df' in globals() and 'description' in df.columns:
    # Top products by revenue
    top_products = df.groupby('description')['totalprice'].sum().reset_index()
    top_products = top_products.sort_values('totalprice', ascending=False).head(10)
    
    plt.figure(figsize=(12, 8))
    plt.barh(top_products['description'], top_products['totalprice'])
    plt.title("Top 10 Products by Revenue", fontsize=16)
    plt.xlabel("Revenue ($)")
    plt.ylabel("Product")
    plt.gca().invert_yaxis()  # Highest at top
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    # Display top products
    display(top_products)
"""

# Country analysis cell
country_analysis = """
if 'df' in globals() and 'country' in df.columns:
    # Sales by country
    country_sales = df.groupby('country')['totalprice'].sum().reset_index()
    country_sales = country_sales.sort_values('totalprice', ascending=False).head(10)
    
    plt.figure(figsize=(12, 6))
    plt.bar(country_sales['country'], country_sales['totalprice'])
    plt.title("Top 10 Countries by Sales", fontsize=16)
    plt.xlabel("Country")
    plt.ylabel("Sales ($)")
    plt.xticks(rotation=45)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    # Display country sales
    display(country_sales)
"""

# Add cells to the notebook
nb.cells.append(nbf.v4.new_markdown_cell("# Online Store Sales Analysis\n\nThis notebook analyzes e-commerce sales data from the cleaned dataset."))
nb.cells.append(nbf.v4.new_code_cell(imports))
nb.cells.append(nbf.v4.new_markdown_cell("## Load and Prepare Data"))
nb.cells.append(nbf.v4.new_code_cell(load_data))
nb.cells.append(nbf.v4.new_markdown_cell("## Sales Overview"))
nb.cells.append(nbf.v4.new_code_cell(sales_overview))
nb.cells.append(nbf.v4.new_markdown_cell("## Product Analysis"))
nb.cells.append(nbf.v4.new_code_cell(product_analysis))
nb.cells.append(nbf.v4.new_markdown_cell("## Geographic Analysis"))
nb.cells.append(nbf.v4.new_code_cell(country_analysis))

# Write the notebook to a file
notebook_filename = 'sales_analysis.ipynb'
with open(notebook_filename, 'w') as f:
    nbf.write(nb, f)

print(f"Notebook created: {notebook_filename}")
print("To open it, run: jupyter notebook sales_analysis.ipynb")