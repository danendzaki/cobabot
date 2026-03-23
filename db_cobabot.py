import sqlite3

conn = sqlite3.connect('todo.db', check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tugas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        nama_tugas TEXT,
        deadline TEXT,
        prioritas TEXT,
        status TEXT
    )
    ''')
    conn.commit()