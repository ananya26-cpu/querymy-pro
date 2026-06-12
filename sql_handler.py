import sqlite3
import pandas as pd
import os

def load_csv_to_db(df, db_name="querymy.db", table_name="data"):
    conn = sqlite3.connect(db_name)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()
    return db_name

def run_sql(query, db_name="querymy.db"):
    try:
        conn = sqlite3.connect(db_name)
        result = pd.read_sql_query(query, conn)
        conn.close()
        return result, None
    except Exception as e:
        return None, str(e)

def get_schema(db_name="querymy.db", table_name="data"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    cols = cursor.fetchall()
    conn.close()
    schema = ", ".join([f"{col[1]} ({col[2]})" for col in cols])
    return f"Table: {table_name}\nColumns: {schema}"
