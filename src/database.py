"""
Need to change sqlite3 to psycopg2
- sqlite3 doesn't support row level locking so almost no concurrency possible :(
"""

import sqlite3
import os
from threading import Lock, Condition
from readerwriterlock import rwlock
import time

sqlite3.threadsafety = 3

class ControlDB:
    def __init__(self, file = 'database.db', restart=True):
        self.DB_FILE = file
        if restart:
            self._clear_db()
        self._create_metadata_table()
        
    def _clear_db(self):
        if os.path.exists(self.DB_FILE):
            os.remove(self.DB_FILE)

    def _create_metadata_table(self):
        connection = sqlite3.connect(self.DB_FILE)
        cursor = connection.cursor()
        cursor.execute(f'CREATE TABLE IF NOT EXISTS organizations (org TEXT PRIMARY KEY)')
        cursor.execute(f'CREATE TABLE IF NOT EXISTS endpoints (org TEXT, endpoint TEXT, PRIMARY KEY (org, endpoint), FOREIGN KEY (org) REFERENCES organizations)')
        connection.commit()
        cursor.close()
        connection.close()
    
    def add_organization(self, org: str): # this should be the last step while adding the organization
        connection = sqlite3.connect(self.DB_FILE)
        cursor = connection.cursor()
        cursor.execute(f'INSERT INTO organizations (org) VALUES ("{org}")')
        cursor.execute(f'CREATE TABLE IF NOT EXISTS {org} (id INTEGER PRIMARY KEY, data TEXT)')
        cursor.execute(f'INSERT INTO {org} (id, data) VALUES (0, "init")')
        connection.commit()
        cursor.close()
        connection.close()
        
    def add_endpoint(self, org: str, endpoint: str):
        connection = sqlite3.connect(self.DB_FILE)
        cursor = connection.cursor()
        cursor.execute(f'INSERT INTO endpoints (org, endpoint) VALUES ("{org}", "{endpoint}")')
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
        
    def reserve_next_available_id(self, org: str):
        retries = 0
        connection = sqlite3.connect(self.DB_FILE)
        cursor = connection.cursor()
        while True:
            try:
                cursor.execute(f'BEGIN')
                cursor.execute(f'SELECT min(D1.id) FROM {org} as D1 WHERE NOT EXISTS (SELECT * FROM {org} as D2 WHERE D2.id = D1.id + 1)')
                result = cursor.fetchone()[0] + 1
                cursor.execute(f'INSERT INTO {org} (id, data) VALUES ({result}, null)')
                cursor.execute(f'COMMIT')
                cursor.close()
                connection.close()
                return result
            except:
                cursor.execute(f'ROLLBACK')
                time.sleep(0.1)
                retries += 1
                if (retries > 20):
                    raise Exception(f"Transaction failed after {retries} retries.")
    
    def insert_val(self, org: str, id: int, val: str):
        retries = 0
        connection = sqlite3.connect(self.DB_FILE)
        cursor = connection.cursor()
        while True:
            try:
                cursor.execute(f'BEGIN')
                cursor.execute(f'DELETE FROM {org} WHERE id = {id}')
                cursor.execute(f'INSERT INTO {org} (id, data) VALUES ({id}, "{val}")')
                cursor.execute(f'COMMIT')
                cursor.close()
                connection.close()
                return
            except:
                cursor.execute(f'ROLLBACK')
                time.sleep(0.1)
                retries += 1
                if (retries > 20):
                    raise Exception(f"Transaction failed after {retries} retries.")
                
    def get_val_and_delete(self, org: str, id: int):
        retries = 0
        connection = sqlite3.connect(self.DB_FILE)
        cursor = connection.cursor()
        while True:
            try:
                cursor.execute(f'BEGIN')
                cursor.execute(f'SELECT data FROM {org} WHERE id = {id}')
                result = cursor.fetchone()[0]
                cursor.execute(f'DELETE FROM {org} WHERE id = {id}')
                cursor.execute(f'COMMIT')
                cursor.close()
                connection.close()
                return result
            except:
                cursor.execute(f'ROLLBACK')
                time.sleep(0.1)
                retries += 1
                if (retries > 20):
                    raise Exception(f"Transaction failed after {retries} retries.")

class ConditionVarStore:
    
    def __init__(self):
        self.storage = {}
        self.storage_lock = rwlock.RWLockFairD()
    
    def add_organization(self, org: str):
        with self.storage_lock.gen_wlock():
            self.storage[org] = (Lock(), {})
        
    def wait_for_condition_var(self, org: str, id: int):
        lock: Lock = None
        org_dict: dict = None
        with self.storage_lock.gen_rlock():
            lock, org_dict = self.storage[org]
        lock.acquire()
        org_dict[id] = Condition(lock)
        org_dict[id].wait()
        lock.release()
        
    def wakeup_condition_var(self, org: str, id: int):
        lock: Lock = None
        org_dict: dict = None
        with self.storage_lock.gen_rlock():
            lock, org_dict = self.storage[org]
        lock.acquire()
        org_dict[id].notify()
        lock.release()

if __name__ == "__main__":
    db = ControlDB(restart = False)
    # db.create_table('test')
    print(db.reserve_next_available_id('test'))