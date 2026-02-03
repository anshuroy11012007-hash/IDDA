import pyodbc
import json
import os

# 1. Connection Configuration
SERVER = 'localhost\\SQLEXPRESS'  # Update as needed
DATABASE = 'DataWarehouse'
USERNAME = 'YOUR_USER'
PASSWORD = 'YOUR_PASSWORD'
DRIVER = '{ODBC Driver 17 for SQL Server}'

conn_str = f'DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'

def get_schema_metadata():
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # 2. Query to get all Tables and Columns
        # We join Tables and Columns to get a complete view
        query = """
        SELECT 
            t.TABLE_NAME,
            c.COLUMN_NAME,
            c.DATA_TYPE,
            c.CHARACTER_MAXIMUM_LENGTH,
            c.IS_NULLABLE
        FROM INFORMATION_SCHEMA.TABLES t
        INNER JOIN INFORMATION_SCHEMA.COLUMNS c 
            ON t.TABLE_NAME = c.TABLE_NAME
        WHERE t.TABLE_TYPE = 'BASE TABLE'
        ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # 3. Structure the data into a Dictionary
        schema = {}
        
        for row in rows:
            table = row.TABLE_NAME
            if table not in schema:
                schema[table] = []
            
            col_info = {
                "name": row.COLUMN_NAME,
                "type": row.DATA_TYPE,
                "length": row.CHARACTER_MAXIMUM_LENGTH,
                "nullable": row.IS_NULLABLE
            }
            if col_info not in schema[table]:
                schema[table].append(col_info)
            
        conn.close()
        return schema

    except Exception as e:
        print(f"Error: {e}")
        return None

# 4. Save to JSON
metadata = get_schema_metadata()
if metadata:
    with open('documentation\\db_schema.json', 'w') as f:
        json.dump(metadata, f, indent=4)
    print("✅ Schema extracted to db_schema.json")