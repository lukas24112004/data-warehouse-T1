import pyodbc

# Connect to your SQL Server database
conn = pyodbc.connect(
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=.\SQLEXPRESS;"
    r"DATABASE=MyProjectDB;"
    r"Trusted_Connection=yes;"
)
conn.autocommit = True
cursor = conn.cursor()

# Create schema if it doesn't exist (SQL Server syntax)
cursor.execute("""
    IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'ingestion')
    BEGIN
        EXEC('CREATE SCHEMA ingestion');
    END
""")
print("Schema created or already exists!")

# Drop and create table: crm_cust_info
cursor.execute("DROP TABLE IF EXISTS ingestion.crm_cust_info")
cursor.execute("""
    CREATE TABLE ingestion.crm_cust_info (
        cst_id INTEGER,
        cst_key VARCHAR(50),
        cst_firstname VARCHAR(50),
        cst_lastname VARCHAR(50),
        cst_marital_status VARCHAR(50),
        cst_gndr VARCHAR(50),
        cst_create_date DATE
    )
""")
print("Table ingestion.crm_cust_info created!")

# Drop and create table: crm_prd_info
cursor.execute("DROP TABLE IF EXISTS ingestion.crm_prd_info")
cursor.execute("""
    CREATE TABLE ingestion.crm_prd_info (
        prd_id INTEGER,
        prd_key VARCHAR(50),
        prd_nm VARCHAR(50),
        prd_cost INTEGER,
        prd_line VARCHAR(50),
        prd_start_dt DATE,
        prd_end_dt DATE
    )
""")
print("Table ingestion.crm_prd_info created!")

# Drop and create table: crm_sales_details
cursor.execute("DROP TABLE IF EXISTS ingestion.crm_sales_details")
cursor.execute("""
    CREATE TABLE ingestion.crm_sales_details (
        sls_ord_num VARCHAR(50),
        sls_prd_key VARCHAR(50),
        sls_cust_id INTEGER,
        sls_order_dt INTEGER,
        sls_ship_dt INTEGER,
        sls_due_dt INTEGER,
        sls_sales DECIMAL(10,2),
        sls_quantity INTEGER,
        sls_price DECIMAL(10,2)
    )
""")
print("Table ingestion.crm_sales_details created!")

# Drop and create table: erp_cust_az12
cursor.execute("DROP TABLE IF EXISTS ingestion.erp_cust_az12")
cursor.execute("""
    CREATE TABLE ingestion.erp_cust_az12 (
        cid VARCHAR(50),
        bdate DATE,
        gen VARCHAR(50)
    )
""")
print("Table ingestion.erp_cust_az12 created!")

# Drop and create table: erp_loc_a101
cursor.execute("DROP TABLE IF EXISTS ingestion.erp_loc_a101")
cursor.execute("""
    CREATE TABLE ingestion.erp_loc_a101 (
        cid VARCHAR(50),
        cntry VARCHAR(50)
    )
""")
print("Table ingestion.erp_loc_a101 created!")

# Drop and create table: erp_px_cat_g1v2
cursor.execute("DROP TABLE IF EXISTS ingestion.erp_px_cat_g1v2")
cursor.execute("""
    CREATE TABLE ingestion.erp_px_cat_g1v2 (
        id VARCHAR(50),
        cat VARCHAR(50),
        subcat VARCHAR(50),
        maintenance VARCHAR(50)
    )
""")
print("Table ingestion.erp_px_cat_g1v2 created!")

cursor.close()
conn.close()