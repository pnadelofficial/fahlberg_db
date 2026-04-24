import sqlite3
import subprocess
import os


class DatabaseManager:
    def __init__(self, path=os.path.join('sensitive_data_for_fahlberg_interview_db', 'db.sql')):
        self.path = path
        self.repo_dir = os.path.dirname(os.path.abspath(path))
        self.conn = sqlite3.connect(path)
        self.cur = self.conn.cursor()

    def _push_to_remote(self):
        try:
            subprocess.run(
                ['git', '-C', self.repo_dir, 'config', 'user.email', 'app@fahlberg'],
                check=True, capture_output=True
            )
            subprocess.run(
                ['git', '-C', self.repo_dir, 'config', 'user.name', 'Fahlberg App'],
                check=True, capture_output=True
            )
            subprocess.run(
                ['git', '-C', self.repo_dir, 'add', 'db.sql'],
                check=True, capture_output=True
            )
            subprocess.run(
                ['git', '-C', self.repo_dir, 'commit', '-m', 'Update database'],
                check=True, capture_output=True
            )
            subprocess.run(
                ['git', '-C', self.repo_dir, 'push'],
                check=True, capture_output=True
            )
        except subprocess.CalledProcessError as e:
            raise Exception(
                f"Database saved locally but failed to push to GitHub.\n"
                f"Command: {e.cmd}\n"
                f"Error: {e.stderr.decode().strip()}"
            )
        
    def insert(self, table, **kwargs):
        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join(['?'] * len(kwargs))
        values = tuple([v[0] if isinstance(v, tuple) else v for v in kwargs.values()])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self.cur.execute(query, values)
        self.conn.commit()
        self._push_to_remote()

    def update(self, table, case_no, **kwargs):
        set_values = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        values = tuple(kwargs.values())
        query = f"UPDATE {table} SET {set_values} WHERE case_no = ?"
        self.cur.execute(query, values + (case_no,))
        self.conn.commit()
        self._push_to_remote()

    def delete(self, table, case_no):
        query = f"DELETE FROM {table} WHERE case_no = ?"
        self.cur.execute(query, (case_no,))
        self.conn.commit()
        self._push_to_remote()