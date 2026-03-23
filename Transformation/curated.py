import pyodbc
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

conn = pyodbc.connect(
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=.\SQLEXPRESS;"
    r"DATABASE=MyProjectDB;"
    r"Trusted_Connection=yes;"
)
conn.autocommit = True
cursor = conn.cursor()

# Create curated schema if it doesn't exist
cursor.execute("""
    IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'curated')
    BEGIN
        EXEC('CREATE SCHEMA curated');
    END
""")


# Load sources from transformation layer
customer_crm_df = pd.read_sql("SELECT * FROM transformation.crm_cust_info_transformed", con=conn)   # transformation1
customer_erp_df = pd.read_sql("SELECT * FROM transformation.erp_cust_az12", con=conn)          # transformation3
location_erp_df = pd.read_sql("SELECT * FROM transformation.erp_loc_a101", con=conn)            # transformation4




df= pd.merge(
    left= customer_crm_df,
    right= customer_erp_df,
    how= "left",
    left_on= "cst_key",
    right_on= "cid"
)



#join with location

df= pd.merge(
    left= df,
    right= location_erp_df,
    how= "left",
    left_on= "cst_key",
    right_on= "cid",
    suffixes= ("", "_loc")
)

# Resolve gender: normalize CRM cst_gndr (M/F) to full names, fall back to ERP gen if invalid
crm_gender = df["cst_gndr"].str.strip().str.upper().replace({"M": "Male", "F": "Female", "MALE": "Male", "FEMALE": "Female"})
df["resolved_gender"] = crm_gender
invalid_mask = ~df["resolved_gender"].isin(["Male", "Female"])
df.loc[invalid_mask, "resolved_gender"] = df.loc[invalid_mask, "gen"]

dim_customers = pd.DataFrame({
    "customer_id": df["cst_id"],
    "customer_number": df["cst_key"],
    "first_name": df["cst_firstname"],
    "last_name": df["cst_lastname"],
    "country": df["cntry"],
    "marital_status": df["cst_marital_status"],
    "gender": df["resolved_gender"],
    "birthdate": df["bdate"],
    "create_date": df["cst_create_date"]
})

dim_customers = dim_customers.sort_values("customer_id").reset_index(drop=True)
dim_customers.insert(0, "customer_key", dim_customers.index + 1)

print(dim_customers)

# -----------------------------------
# Create SQLAlchemy engine
# -----------------------------------
url = URL.create(
    drivername="mssql+pyodbc",
    host=r".\SQLEXPRESS",
    database="MyProjectDB",
    query={
        "driver": "ODBC Driver 17 for SQL Server",
        "Trusted_Connection": "yes",
    }
)

engine = create_engine(url)

# -----------------------------------
# Load into curated schema
# -----------------------------------
dim_customers.to_sql(
    name="dim_customers",
    con=engine,
    schema="curated",
    if_exists="replace",
    index=False
)

print("dim_customers loaded into curated.dim_customers")


# -----------------------------------
# dim_products
# -----------------------------------
product_crm_df = pd.read_sql("SELECT * FROM transformation.crm_prd_info_transformed", con=engine)
category_erp_df = pd.read_sql("SELECT * FROM ingestion.erp_px_cat_g1v2", con=engine)

df = pd.merge(
    left=product_crm_df,
    right=category_erp_df,
    how="left",
    left_on="cat_id",
    right_on="id"
)

dim_products = pd.DataFrame({
    "product_number": df["prd_key"],
    "product_name": df["prd_nm"],
    "category_id": df["cat_id"],
    "category": df["cat"],
    "subcategory": df["subcat"],
    "maintenance": df["maintenance"],
    "cost": df["prd_cost"],
    "product_line": df["prd_line"],
    "start_date": df["prd_start_dt"],
    "end_date": df["prd_end_dt"]
})

dim_products = dim_products.sort_values("product_number").reset_index(drop=True)
dim_products.insert(0, "product_key", dim_products.index + 1)

print(dim_products)

# -----------------------------------
# Load into curated schema
# -----------------------------------
dim_products.to_sql(
    name="dim_products",
    con=engine,
    schema="curated",
    if_exists="replace",
    index=False
)

print("dim_products loaded into curated.dim_products")


# -----------------------------------
# fact_sales
# -----------------------------------
sales_details_df = pd.read_sql("SELECT * FROM transformation.crm_sales_details", con=engine)
dim_products_df = pd.read_sql("SELECT * FROM curated.dim_products", con=engine)
dim_customers_df = pd.read_sql("SELECT * FROM curated.dim_customers", con=engine)

# Join sales to products
df = pd.merge(
    left=sales_details_df,
    right=dim_products_df[["product_key", "product_number"]],
    how="left",
    left_on="sls_prd_key",
    right_on="product_number"
)

# Join result to customers
df = pd.merge(
    left=df,
    right=dim_customers_df[["customer_key", "customer_id"]],
    how="left",
    left_on="sls_cust_id",
    right_on="customer_id"
)

fact_sales = pd.DataFrame({
    "product_key": df["product_key"],
    "customer_key": df["customer_key"],
    "order_number": df["sls_ord_num"],
    "order_date": df["sls_order_dt"],
    "shipping_date": df["sls_ship_dt"],
    "due_date": df["sls_due_dt"],
    "sales": df["sls_sales"],
    "quantity": df["sls_quantity"],
    "price": df["sls_price"]
})

print(fact_sales.head(10))

fact_sales = fact_sales.reset_index(drop=True)
fact_sales.insert(0, "sales_key", fact_sales.index + 1)

# -----------------------------------
# Load into curated schema
# -----------------------------------
fact_sales.to_sql(
    name="fact_sales",
    con=engine,
    schema="curated",
    if_exists="replace",
    index=False
)

print("fact_sales loaded into curated.fact_sales")

conn.close()
