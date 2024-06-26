"""
Need to change sqlite3 to psycopg2
- sqlite3 doesn't support row level locking so almost no concurrency possible :(
"""

import sqlite3
import os

sqlite3.threadsafety = 3

class ControlDB:
    def __init__(self, file = 'database.db', restart=True):
        self.DB_FILE = file
        if restart:
            self._clear_db()
        self._create_metadata_tables()
        
    def _clear_db(self):
        if os.path.exists(self.DB_FILE):
            os.remove(self.DB_FILE)

    def _create_metadata_tables(self):
        connection = sqlite3.connect(self.DB_FILE)
        cursor = connection.cursor()
        cursor.execute(f'CREATE TABLE IF NOT EXISTS organizations (org TEXT PRIMARY KEY)')
        cursor.execute(f'CREATE TABLE IF NOT EXISTS endpoints (org TEXT, endpoint TEXT, ip TEXT, image TEXT, replicas INTEGER, PRIMARY KEY (org, endpoint), FOREIGN KEY (org) REFERENCES organizations)') 
        connection.commit()
        cursor.close()
        connection.close()
    
    def add_organization(self, org: str): # this should be the last step while adding the organization
        connection = sqlite3.connect(self.DB_FILE)
        cursor = connection.cursor()
        cursor.execute(f'INSERT INTO organizations (org) VALUES ("{org}")')
        connection.commit()
        cursor.close()
        connection.close()
        
    def add_endpoint(self, org: str, endpoint: str, ip: str, image: str, replicas: int):
        connection = sqlite3.connect(self.DB_FILE)
        cursor = connection.cursor()
        cursor.execute(f'INSERT INTO endpoints (org, endpoint, ip, image, replicas) VALUES ("{org}", "{endpoint}", "{ip}", "{image}", {replicas})')
        connection.commit()
        cursor.close()
        connection.close()
        
    def check_endpoint(self, org: str, endpoint: str):
        connection = sqlite3.connect(self.DB_FILE)
        cursor = connection.cursor()
        cursor.execute(f'SELECT * FROM endpoints WHERE org = "{org}" AND endpoint = "{endpoint}"')
        ret = cursor.fetchone() is not None
        cursor.close()
        connection.close()
        return ret
    
    def check_organization(self, org: str):
        connection = sqlite3.connect(self.DB_FILE)
        cursor = connection.cursor()
        cursor.execute(f'SELECT * FROM organizations WHERE org = "{org}"')
        ret = cursor.fetchone() is not None
        cursor.close()
        connection.close()
        return ret
        
    def get_endpoint(self, org: str, endpoint: str):
        connection = sqlite3.connect(self.DB_FILE)
        cursor = connection.cursor()
        cursor.execute(f'SELECT ip, image, replicas FROM endpoints WHERE org = "{org}" AND endpoint = "{endpoint}"')
        ret = cursor.fetchone()
        cursor.close()
        connection.close()
        return ret if ret is not None else None
    
    def iterate_over_endpoints(self):
        connection = sqlite3.connect(self.DB_FILE)
        cursor = connection.cursor()
        cursor.execute(f'SELECT org, endpoint, ip, image, replicas FROM endpoints')
        for row in cursor:
            yield row
        cursor.close()
        connection.close()

if __name__ == "__main__":
    db = ControlDB(restart = False)
    db.create_table('test')
