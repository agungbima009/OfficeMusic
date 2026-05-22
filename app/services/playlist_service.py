import os

from app.core.constants import (
    DOWNLOAD_FOLDER
)

# =========================================
# GET PLAYLIST (Synced with Database & Disk)
# =========================================
def get_playlist():

    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    # 1. Scan .mp3 files on disk
    disk_files = {f for f in os.listdir(DOWNLOAD_FOLDER) if f.endswith(".mp3")}

    from app.core.database import get_connection
    conn = get_connection()
    cursor = conn.cursor()

    # 2. Get registered files in DB
    cursor.execute("SELECT filename FROM songs")
    db_files = {row['filename'] for row in cursor.fetchall()}

    # 3. Synchronize DB with Disk:
    # Remove database entries if the physical file was deleted
    missing_on_disk = db_files - disk_files
    for filename in missing_on_disk:
        cursor.execute("DELETE FROM songs WHERE filename = ?", (filename,))
        cursor.execute("DELETE FROM playlists WHERE song_filename = ?", (filename,))

    # Register physical files into the database if missing
    missing_in_db = disk_files - db_files
    for filename in missing_in_db:
        # Generate readable title from filename
        readable_title = filename[:-4].replace("_", " ")
        cursor.execute(
            "INSERT INTO songs (title, filename, channel, thumbnail, youtube_url, downloaded) VALUES (?, ?, ?, ?, ?, 1)",
            (readable_title, filename, "Local Import", "", "")
        )

    if missing_on_disk or missing_in_db:
        conn.commit()

    # 4. Fetch all songs from database
    cursor.execute("SELECT id, title, filename, channel, thumbnail, youtube_url, created_at FROM songs ORDER BY title ASC")
    songs = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return songs

# =========================================
# DELETE SONG (From disk and database)
# =========================================
def delete_song(filename):

    file_path = os.path.join(
        DOWNLOAD_FOLDER,
        filename
    )

    # Delete physical file from disk
    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete from SQLite database
    from app.core.database import get_connection
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM songs WHERE filename = ?", (filename,))
        cursor.execute("DELETE FROM playlists WHERE song_filename = ?", (filename,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting song from DB: {e}")
    finally:
        conn.close()

    return {
        "status": True,
        "message": f"{filename} deleted from library and database"
    }

# =========================================
# SONG DETAIL (Richer details from database)
# =========================================
def get_song_detail(filename):

    file_path = os.path.join(
        DOWNLOAD_FOLDER,
        filename
    )

    file_size = 0.0
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)

    from app.core.database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM songs WHERE filename = ?", (filename,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {
            "status": False,
            "message": "File not found in database"
        }

    song_details = dict(row)
    song_details["status"] = True
    song_details["size_mb"] = round(file_size / (1024 * 1024), 2)

    return song_details


# =========================================
# PLAYLIST GROUP OPERATIONS (SQLite DB)
# =========================================

def get_all_playlists():
    from app.core.database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT playlist_name FROM playlists ORDER BY playlist_name ASC")
    playlists = [row["playlist_name"] for row in cursor.fetchall()]
    conn.close()
    return playlists


def create_playlist(playlist_name: str):
    """Create an empty playlist entry.
    Since playlists are stored in the `playlists` table as mappings, an empty playlist
    can be represented by inserting a placeholder row with a null filename. This row
    is later ignored when retrieving songs.
    """
    from app.core.database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    # Ensure we don't duplicate placeholder rows
    cursor.execute(
        "SELECT COUNT(*) as cnt FROM playlists WHERE playlist_name = ? AND (song_filename IS NULL OR song_filename = '')",
        (playlist_name,)
    )
    if cursor.fetchone()["cnt"] == 0:
        cursor.execute(
            "INSERT INTO playlists (playlist_name, song_filename) VALUES (?, '')",
            (playlist_name,)
        )
        conn.commit()
    conn.close()
    return {"status": True, "message": f"Playlist {playlist_name} created (or already exists)"}


def get_playlist_stream_urls(playlist_name: str):
    """Return streaming URLs for all songs in a playlist.
    The URLs correspond to the `/stream/{filename}` endpoint defined in the
    `playlist_routes` module.
    """
    songs = get_songs_in_playlist(playlist_name)
    return [f"/stream/{song['filename']}" for song in songs]

def get_songs_in_playlist(playlist_name):
    from app.core.database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, s.title, s.filename, s.channel, s.thumbnail, s.youtube_url, s.created_at
        FROM playlists p
        JOIN songs s ON p.song_filename = s.filename
        WHERE p.playlist_name = ?
        ORDER BY p.id ASC
    """, (playlist_name,))
    songs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return songs

def add_song_to_playlist(playlist_name, song_filename):
    """Add a song to a playlist, creating the playlist if it does not exist.
    Returns a dict indicating success or failure.
    """
    from app.core.database import get_connection
    conn = get_connection()
    cursor = conn.cursor()

    # Ensure the playlist exists (create placeholder row if needed)
    cursor.execute(
        "SELECT COUNT(*) as cnt FROM playlists WHERE playlist_name = ?",
        (playlist_name,)
    )
    if cursor.fetchone()["cnt"] == 0:
        # Insert a placeholder entry to represent an empty playlist
        cursor.execute(
            "INSERT INTO playlists (playlist_name, song_filename) VALUES (?, '')",
            (playlist_name,)
        )
        conn.commit()

    # Check if song exists in songs table
    cursor.execute("SELECT id FROM songs WHERE filename = ?", (song_filename,))
    if not cursor.fetchone():
        conn.close()
        return {"status": False, "message": f"Song {song_filename} not found in library"}

    # Check if mapping already exists
    cursor.execute("SELECT id FROM playlists WHERE playlist_name = ? AND song_filename = ?", (playlist_name, song_filename))
    if cursor.fetchone():
        conn.close()
        return {"status": True, "message": f"Song already in playlist {playlist_name}"}

    cursor.execute(
        "INSERT INTO playlists (playlist_name, song_filename) VALUES (?, ?)",
        (playlist_name, song_filename)
    )
    conn.commit()
    conn.close()
    return {"status": True, "message": f"Song {song_filename} added to playlist {playlist_name}"}

def remove_song_from_playlist(playlist_name, song_filename):
    from app.core.database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM playlists WHERE playlist_name = ? AND song_filename = ?", (playlist_name, song_filename))
    conn.commit()
    conn.close()
    return {"status": True, "message": f"Song {song_filename} removed from playlist {playlist_name}"}

def delete_playlist(playlist_name):
    from app.core.database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM playlists WHERE playlist_name = ?", (playlist_name,))
    conn.commit()
    conn.close()
    return {"status": True, "message": f"Playlist {playlist_name} deleted successfully"}