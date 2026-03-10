import pyodbc
import pandas as pd

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

tables = [
    {
        "table": "transformation.crm_cust_info_transformed",
        "file": "crm_cust_info_transformed.csv",
        "columns": 7
    },

]
# df.to_sql('crm_cust_info', con=conn, schema='transformation', if_exists='replace', index=False)
