import sqlite3
import requests
import base64
import os


class DatabaseManager:
    def __init__(self, path=os.path.join('sensitive_data_for_fahlberg_interview_db', 'db.sql')):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.cur = self.conn.cursor()
        self._token = os.environ.get('GITHUB_TOKEN')
        self._repo = os.environ.get('GITHUB_REPO')   # "owner/repo-name"
        self._branch = os.environ.get('GITHUB_BRANCH', 'main')
        self._file_path = os.environ.get('GITHUB_FILE_PATH', 'db.sql')

    def _push_to_remote(self):
        if not self._token or not self._repo:
            raise Exception(
                "GITHUB_TOKEN and GITHUB_REPO environment variables must be set."
            )

        headers = {
            'Authorization': f'token {self._token}',
            'Accept': 'application/vnd.github.v3+json',
        }
        url = f'https://api.github.com/repos/{self._repo}/contents/{self._file_path}'

        # Fetch the current file SHA (required by the API to confirm we're updating the right version)
        get_resp = requests.get(url, headers=headers, params={'ref': self._branch})
        if get_resp.status_code != 200:
            msg = get_resp.json().get('message', get_resp.text)
            raise Exception(f"GitHub API error fetching file metadata ({get_resp.status_code}): {msg}")

        current_sha = get_resp.json()['sha']

        with open(self.path, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')

        payload = {
            'message': 'Update database',
            'content': encoded,
            'sha': current_sha,
            'branch': self._branch,
        }
        put_resp = requests.put(url, headers=headers, json=payload)
        if put_resp.status_code not in (200, 201):
            msg = put_resp.json().get('message', put_resp.text)
            raise Exception(f"GitHub API error pushing file ({put_resp.status_code}): {msg}")

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
