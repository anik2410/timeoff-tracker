import sqlite3

def get_conn(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    return conn, cursor


def init_tables(conn, cursor, table_name, allowance_table):
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {allowance_table} (
            key TEXT PRIMARY KEY,
            value FLOAT
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY,
            start_date TEXT,
            end_date TEXT,
            is_full_day BOOLEAN,
            hours FLOAT,
            purpose TEXT
        )
    """)

    conn.commit()
