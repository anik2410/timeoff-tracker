import sqlite3
from datetime import datetime

class TimeOffBase:
    def __init__(self, db_file, table_records, table_allowance):
        self.db_file = db_file
        self.table_records = table_records
        self.table_allowance = table_allowance
        
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self.initialize_tables()

    def initialize_tables(self):
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_allowance} (
                key TEXT PRIMARY KEY,
                value FLOAT
            )
        """)
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_records} (
                id INTEGER PRIMARY KEY,
                start_date TEXT,
                end_date TEXT,
                is_full_day BOOLEAN,
                hours FLOAT,
                purpose TEXT
            )
        """)
        self.conn.commit()

    # ---------------------------- ALLOWANCE LOGIC ----------------------------

    def get_allowance(self):
        self.cursor.execute(f"SELECT value FROM {self.table_allowance} WHERE key='total'")
        row = self.cursor.fetchone()
        return row[0] if row else None

    def set_allowance(self, value):
        if self.get_allowance() is None:
            self.cursor.execute(
                f"INSERT INTO {self.table_allowance} VALUES ('total', ?)",
                (value,)
            )
        else:
            self.cursor.execute(
                f"UPDATE {self.table_allowance} SET value=? WHERE key='total'",
                (value,)
            )
        self.conn.commit()

    # ---------------------------- RECORD LOGIC ----------------------------

    def add_record(self, start, end, full_day, purpose):
        days = (end - start).days + 1
        hours = (days if full_day else 0.5) * 8

        self.cursor.execute(
            f"""
            INSERT INTO {self.table_records} (start_date, end_date, is_full_day, hours, purpose)
            VALUES (?, ?, ?, ?, ?)
            """,
            (start.isoformat(), end.isoformat(), full_day, hours, purpose)
        )
        self.conn.commit()

    def get_records(self):
        self.cursor.execute(f"SELECT * FROM {self.table_records}")
        return self.cursor.fetchall()

    def delete_record(self, record_id):
        self.cursor.execute(
            f"DELETE FROM {self.table_records} WHERE id=?",
            (record_id,)
        )
        self.conn.commit()

    def update_record(self, record_id, start, end, full_day, purpose):
        days = (end - start).days + 1
        hours = (days if full_day else 0.5) * 8

        self.cursor.execute(
            f"""
            UPDATE {self.table_records}
            SET start_date=?, end_date=?, is_full_day=?, hours=?, purpose=?
            WHERE id=?
            """,
            (start.isoformat(), end.isoformat(), full_day, hours, purpose, record_id)
        )
        self.conn.commit()

    # --------------------------- CALCULATIONS ---------------------------

    def remaining_days(self):
        total = self.get_allowance()
        if total is None:
            return None

        used = 0
        for rec in self.get_records():
            start = datetime.strptime(rec[1], "%Y-%m-%d").date()
            end   = datetime.strptime(rec[2], "%Y-%m-%d").date()
            full  = rec[3]

            days = (end - start).days + 1
            used += days if full else 0.5

        return total - used

    # --------------------------- RESET LOGIC ---------------------------

    def reset_all(self):
        self.cursor.execute(f"DROP TABLE IF EXISTS {self.table_records}")
        self.cursor.execute(f"DROP TABLE IF EXISTS {self.table_allowance}")
        self.initialize_tables()
