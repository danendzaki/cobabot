import sqlite3

conn = sqlite3.connect('inventaris.db', check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS paket (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_paket TEXT,
        isi TEXT,
        harga INTEGER,
        stok INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transaksi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        user TEXT,
        nama_paket TEXT,
        harga INTEGER,
        status TEXT
    )
    ''')

    cursor.execute("SELECT COUNT(*) FROM paket")
    if cursor.fetchone()[0] == 0:
        data_paket = [
            ("Paket 1", "Beras + Minyak + Gula", 50000, 10),
            ("Paket 2", "Minyak + Indomie + Sabun", 45000, 8),
            ("Paket 3", "Kecap + Beras + Kopi", 55000, 5)
        ]

        cursor.executemany(
            "INSERT INTO paket (nama_paket, isi, harga, stok) VALUES (?, ?, ?, ?)",
            data_paket
        )

    conn.commit()