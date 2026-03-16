import pyodbc
import pandas as pd
#cleaning for product
# Connect to your SQL Server database
conn = pyodbc.connect(
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=.\SQLEXPRESS;"
    r"DATABASE=MyProjectDB;"
    r"Trusted_Connection=yes;"
)
conn.autocommit = True
cursor = conn.cursor()

df = pd.read_sql_query("SELECT * FROM ingestion.crm_prd_info", con =conn)

df['cat_id'] = df['prd_key'].str[:5]
df["cat_id"] = df["cat_id"].str.replace("-", "_")
df["prd_cost"] = df["prd_cost"].fillna(0)
df["prd_line"] = df["prd_line"].str.replace("R", "Road") 
df["prd_line"] = df["prd_line"].str.replace("S", "Sport")
df["prd_line"] = df["prd_line"].str.replace("M", "Mountain")
df["prd_line"] = df["prd_line"].str.replace("T", "Touring")
df["prd_line"] = df["prd_line"].fillna("N/A")
df["prd_start_dt"] = pd.to_datetime(df["prd_start_dt"])
df = df.sort_values(["prd_key", "prd_start_dt"])
df["prd_end_dt"] = df.groupby("prd_key")["prd_start_dt"].shift(-1) - pd.Timedelta(days=1)

df= df.sort_values("prd_id").copy()
print(df)






df.to_csv("C:\\Users\\Gebruiker\\Downloads\\new_database\\crm_prd_info_transformed.csv", index=False)

# Create schema if it doesn't exist (SQL Server syntax)
cursor.execute("""
    IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'transformation')
    BEGIN
        EXEC('CREATE SCHEMA transformation');
    END
""")
print("Schema created or already exists!")

# Drop and create table: crm_prd_info
cursor.execute("DROP TABLE IF EXISTS transformation.crm_prd_info_transformed")
cursor.execute("""
    CREATE TABLE transformation.crm_prd_info_transformed (
        prd_id INTEGER,
        prd_key VARCHAR(50),
        prd_nm VARCHAR(50),
        prd_cost INTEGER,
        prd_line VARCHAR(50),
        prd_start_dt DATE,
        prd_end_dt DATE,
        cat_id VARCHAR(50)
    )
""")
print("Table transformation.crm_prd_info_transformed created!")



tables = [
    {
        "table": "transformation.crm_prd_info_transformed",
        "file": "crm_prd_info_transformed.csv",
        "columns": 8
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
            # Cast prd_id (col 0) and prd_cost (col 3) to int
            if row[0] is not None:
                row[0] = int(float(row[0]))
            if row[3] is not None:
                row[3] = int(float(row[3]))
            cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", row)
            rows += 1

    print(f"Loaded {rows} rows into {table_name}")

cursor.close()
conn.close()
print("All transformation tables loaded!")
