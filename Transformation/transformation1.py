import pyodbc
import pandas as pd
#cleaning for costumer
# Connect to your SQL Server database
conn = pyodbc.connect(
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=.\SQLEXPRESS;"
    r"DATABASE=MyProjectDB;"
    r"Trusted_Connection=yes;"
)
conn.autocommit = True
cursor = conn.cursor()

df = pd.read_sql_query("SELECT * FROM ingestion.crm_cust_info", con =conn)

print(df)

df= df.dropna(subset= ["cst_id"])
df = df.drop_duplicates(subset= ["cst_id"], keep= 'last')
df.to_csv("C:\\Users\\Gebruiker\\Downloads\\new_database\\crm_cust_info_transformed.csv", index=False)


# Create schema if it doesn't exist (SQL Server syntax)
cursor.execute("""
    IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'transformation')
    BEGIN
        EXEC('CREATE SCHEMA transformation');
    END
""")
print("Schema created or already exists!")



# Drop and create table: crm_cust_info
cursor.execute("DROP TABLE IF EXISTS transformation.crm_cust_info_transformed")
cursor.execute("""
    CREATE TABLE transformation.crm_cust_info_transformed (
        cst_id INTEGER,
        cst_key VARCHAR(50),
        cst_firstname VARCHAR(50),
        cst_lastname VARCHAR(50),
        cst_marital_status VARCHAR(50),
        cst_gndr VARCHAR(50),
        cst_create_date DATE
    )
""")
print("Table transformation.crm_cust_info_transformed created!")




tables = [
    {
        "table": "transformation.crm_cust_info_transformed",
        "file": "crm_cust_info_transformed.csv",
        "columns": 7
    },
]

import csv
for t in tables:
    table_name = t["table"]
    file_path = t["file"]
    placeholders = ",".join(["?" for _ in range(t["columns"])])

    cursor.execute(f"TRUNCATE TABLE {table_name}")

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = 0
        for row in reader:
            row = [None if val == "" else val for val in row]
            cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", row)
            rows += 1

    print(f"Loaded {rows} rows into {table_name}")

cursor.close()
conn.close()
print("All transformation tables loaded!")

