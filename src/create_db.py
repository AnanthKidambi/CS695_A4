import sqlite3

def create_control_server_db(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    