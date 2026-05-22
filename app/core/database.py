import sqlite3

DB_NAME = "office_music.db"

# =========================================
# CONNECTION
# =========================================

def get_connection():

    conn = sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn

# =========================================
# INIT DB
# =========================================

def init_db():

    conn = get_connection()

    cursor = conn.cursor()

    # =====================================
    # SONGS
    # =====================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS songs (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        title TEXT,

        filename TEXT UNIQUE,

        channel TEXT,

        thumbnail TEXT,

        youtube_url TEXT,

        downloaded INTEGER DEFAULT 1,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # =====================================
    # PLAYLIST
    # =====================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS playlists (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        playlist_name TEXT,

        song_filename TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()

    conn.close()