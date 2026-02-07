import pyodbc
import json
import os

# 1. Connection Configuration
SERVER = 'localhost\\SQLEXPRESS'  # Update as needed
DATABASE = 'DataWarehouse'
DRIVER = '{ODBC Driver 17 for SQL Server}'

conn_str = f'DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'

def get_schema_metadata():
    schema = {}
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        print("1️⃣  Extracting Table & Column Metadata...")
        # Query 1: Get standard column details
        col_query = """
        SELECT 
            t.TABLE_NAME,
            c.COLUMN_NAME,
            c.DATA_TYPE,
            c.IS_NULLABLE
        FROM INFORMATION_SCHEMA.TABLES t
        INNER JOIN INFORMATION_SCHEMA.COLUMNS c 
            ON t.TABLE_NAME = c.TABLE_NAME
        WHERE t.TABLE_TYPE = 'BASE TABLE'
        """
        cursor.execute(col_query)
        
        for row in cursor.fetchall():
            t_name = row.TABLE_NAME
            if t_name not in schema:
                schema[t_name] = {"columns": [], "foreign_keys": []}
            
            schema[t_name]["columns"].append({
                "name": row.COLUMN_NAME,
                "type": row.DATA_TYPE,
                "nullable": row.IS_NULLABLE
            })

        print("2️⃣  Extracting Foreign Key Relationships...")
        # Query 2: Get Foreign Key relationships using system tables
        fk_query = """
        SELECT 
            tp.name AS [TableName],
            cp.name AS [ColumnName],
            tr.name AS [ReferencedTable],
            cr.name AS [ReferencedColumn]
        FROM sys.foreign_keys AS fk
        INNER JOIN sys.tables AS tp ON fk.parent_object_id = tp.object_id
        INNER JOIN sys.tables AS tr ON fk.referenced_object_id = tr.object_id
        INNER JOIN sys.foreign_key_columns AS fkc ON fkc.constraint_object_id = fk.object_id
        INNER JOIN sys.columns AS cp ON fkc.parent_column_id = cp.column_id AND fkc.parent_object_id = cp.object_id
        INNER JOIN sys.columns AS cr ON fkc.referenced_column_id = cr.column_id AND fkc.referenced_object_id = cr.object_id
        """
        cursor.execute(fk_query)
        
        for row in cursor.fetchall():
            t_name = row.TableName
            if t_name in schema:
                schema[t_name]["foreign_keys"].append({
                    "column": row.ColumnName,
                    "references_table": row.ReferencedTable,
                    "references_column": row.ReferencedColumn
                })

        conn.close()
        return schema

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# 4. Save to JSON
metadata = get_schema_metadata()
if metadata:
    with open('documentation\\db_schema.json', 'w') as f:
        json.dump(metadata, f, indent=4)
    print("✅ Schema extracted to db_schema.json")