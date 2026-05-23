import sqlite3
from app.core.constants import DB_PATH

# =========================================
# CONNECTION
# =========================================

def get_connection():

    conn = sqlite3.connect(
        str(DB_PATH),
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

    # =====================================
    # MIGRATION
    # =====================================
    try:
        migrate_html_entities(conn)
        conn.commit()
    except Exception as e:
        print(f"Error running HTML entities migration: {e}")

    conn.close()


def migrate_html_entities(conn):
    import os
    import html
    from app.core.constants import DOWNLOAD_FOLDER, VIDEO_FOLDER

    cursor = conn.cursor()

    # 1. Fetch all songs to check for HTML entities in title or filename
    cursor.execute("SELECT id, title, filename FROM songs")
    songs = cursor.fetchall()

    for song in songs:
        song_id = song["id"]
        old_title = song["title"]
        old_filename = song["filename"]

        # Check if there is any change when unescaping
        new_title = html.unescape(old_title)
        new_filename = html.unescape(old_filename)

        if old_title != new_title or old_filename != new_filename:
            print(f"[MIGRATION] Migrating song {song_id}: '{old_title}' -> '{new_title}'")

            # A. Rename actual files on disk if they exist under the old name
            if old_filename != new_filename:
                # check in music_cache
                old_music_path = os.path.join(DOWNLOAD_FOLDER, old_filename)
                new_music_path = os.path.join(DOWNLOAD_FOLDER, new_filename)
                if os.path.exists(old_music_path) and not os.path.exists(new_music_path):
                    try:
                        os.rename(old_music_path, new_music_path)
                        print(f"[MIGRATION] Renamed music file to: {new_filename}")
                    except Exception as e:
                        print(f"[MIGRATION] Failed to rename music file: {e}")

                # check in video_cache (mp4)
                old_video_base = old_filename[:-4] if old_filename.endswith(".mp3") else old_filename
                new_video_base = new_filename[:-4] if new_filename.endswith(".mp3") else new_filename
                old_video_filename = f"{old_video_base}.mp4"
                new_video_filename = f"{new_video_base}.mp4"

                old_video_path = os.path.join(VIDEO_FOLDER, old_video_filename)
                new_video_path = os.path.join(VIDEO_FOLDER, new_video_filename)
                if os.path.exists(old_video_path) and not os.path.exists(new_video_path):
                    try:
                        os.rename(old_video_path, new_video_path)
                        print(f"[MIGRATION] Renamed video file to: {new_video_filename}")
                    except Exception as e:
                        print(f"[MIGRATION] Failed to rename video file: {e}")

            # B. Update the database record in the `songs` table
            cursor.execute(
                "UPDATE songs SET title = ?, filename = ? WHERE id = ?",
                (new_title, new_filename, song_id)
            )

            # C. Update the playlist entries referencing the old filename in the `playlists` table
            cursor.execute(
                "UPDATE playlists SET song_filename = ? WHERE song_filename = ?",
                (new_filename, old_filename)
            )

    # 2. Scan physical directories to rename any other cache files containing HTML entities
    for folder in [DOWNLOAD_FOLDER, VIDEO_FOLDER]:
        if os.path.exists(folder):
            for file_name in os.listdir(folder):
                new_file_name = html.unescape(file_name)
                if file_name != new_file_name:
                    old_path = os.path.join(folder, file_name)
                    new_path = os.path.join(folder, new_file_name)
                    if not os.path.exists(new_path):
                        try:
                            os.rename(old_path, new_path)
                            print(f"[MIGRATION] Disk scan renamed: {file_name} -> {new_file_name}")
                        except Exception as e:
                            print(f"[MIGRATION] Disk scan failed to rename: {e}")