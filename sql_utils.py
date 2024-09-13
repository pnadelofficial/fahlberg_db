import sqlite3
import os

class DatabaseManager:
    def __init__(self, path=os.path.join('sensitive_data_for_fahlberg_interview_db','db.sql')):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.cur = self.conn.cursor()
    
    def insert(self, table, **kwargs):
        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join(['?'] * len(kwargs))
        values = tuple([v[0] if isinstance(v, tuple) else v for v in kwargs.values()])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self.cur.execute(query, values)
        self.conn.commit()
    
    def update(self, table, case_no, **kwargs):
        set_values = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        values = tuple(kwargs.values())
        query = f"UPDATE {table} SET {set_values} WHERE case_no = ?"
        self.cur.execute(query, values + (case_no,))
        self.conn.commit()
    
    def delete(self, table, case_no):
        query = f"DELETE FROM {table} WHERE case_no = ?"
        self.cur.execute(query, (case_no,))
        self.conn.commit()
