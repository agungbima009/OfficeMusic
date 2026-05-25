
import os
from urllib.parse import quote

from app.core.constants import DOWNLOAD_FOLDER


# =========================================
# GET PLAYLIST
# =========================================
def get_playlist():

    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    disk_files = {
        f for f in os.listdir(DOWNLOAD_FOLDER)
        if f.endswith(".mp3")
    }

    from app.core.database import get_connection

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT filename FROM songs"
    )

    db_files = {
        row['filename']
        for row in cursor.fetchall()
    }

    # Remove missing files
    missing_on_disk = db_files - disk_files

    for filename in missing_on_disk:

        cursor.execute(
            "DELETE FROM songs WHERE filename = ?",
            (filename,)
        )

        cursor.execute(
            "DELETE FROM playlists WHERE song_filename = ?",
            (filename,)
        )

    # Add missing files
    missing_in_db = disk_files - db_files

    for filename in missing_in_db:

        readable_title = (
            filename[:-4]
            .replace("_", " ")
        )

        cursor.execute("""
            INSERT INTO songs
            (
                title,
                filename,
                channel,
                thumbnail,
                youtube_url,
                downloaded
            )
            VALUES (?, ?, ?, ?, ?, 1)
        """, (
            readable_title,
            filename,
            "Local Import",
            "",
            ""
        ))

    if missing_on_disk or missing_in_db:
        conn.commit()

    cursor.execute("""
        SELECT
            id,
            title,
            filename,
            channel,
            thumbnail,
            youtube_url,
            created_at
        FROM songs
        ORDER BY title ASC
    """)

    songs = [
        dict(row)
        for row in cursor.fetchall()
    ]

    conn.close()

    return songs


# =========================================
# DELETE SONG
# =========================================
def delete_song(filename):

    file_path = os.path.join(DOWNLOAD_FOLDER, filename)

    if os.path.exists(file_path):
        os.remove(file_path)

    from app.core.database import get_connection

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM songs WHERE filename = ?",
            (filename,)
        )

        cursor.execute(
            "DELETE FROM playlists WHERE song_filename = ?",
            (filename,)
        )

        conn.commit()

    finally:
        conn.close()

    return {
        "status": True,
        "message": f"{filename} deleted"
    }


# =========================================
# SONG DETAIL
# =========================================
def get_song_detail(filename):

    file_path = os.path.join(DOWNLOAD_FOLDER, filename)

    file_size = 0.0

    if os.path.exists(file_path):

        file_size = os.path.getsize(file_path)

    from app.core.database import get_connection

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM songs WHERE filename = ?",
        (filename,)
    )

    row = cursor.fetchone()

    conn.close()

    if not row:

        return {
            "status": False,
            "message": "Music not found"
        }

    song = dict(row)

    song["status"] = True

    song["size_mb"] = round(
        file_size / (1024 * 1024),
        2
    )

    return song


# =========================================
# GET PLAYLISTS
# =========================================
def get_all_playlists():

    from app.core.database import get_connection

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT playlist_name
        FROM playlists
        ORDER BY playlist_name ASC
    """)

    playlists = [
        row["playlist_name"]
        for row in cursor.fetchall()
        if row["playlist_name"]
    ]

    conn.close()

    return playlists


# =========================================
# CREATE PLAYLIST
# =========================================
def create_playlist(playlist_name):

    from app.core.database import get_connection

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) as cnt
        FROM playlists
        WHERE playlist_name = ?
    """, (playlist_name,))

    exists = cursor.fetchone()["cnt"]

    if exists == 0:

        cursor.execute("""
            INSERT INTO playlists
            (
                playlist_name,
                song_filename
            )
            VALUES (?, '')
        """, (playlist_name,))

        conn.commit()

    conn.close()

    return {
        "status": True,
        "message": f"{playlist_name} created"
    }


# =========================================
# PLAYLIST STREAM URLS
# =========================================
def get_playlist_stream_urls(playlist_name):

    songs = get_songs_in_playlist(
        playlist_name
    )

    return [
        f"/stream/{quote(song['filename'])}"
        for song in songs
    ]


# =========================================
# PLAYLIST SONGS
# =========================================
def get_songs_in_playlist(playlist_name):

    from app.core.database import get_connection

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            s.id,
            s.title,
            s.filename,
            s.channel,
            s.thumbnail,
            s.youtube_url,
            s.created_at

        FROM playlists p

        JOIN songs s
        ON p.song_filename = s.filename

        WHERE p.playlist_name = ?

        ORDER BY p.id ASC
    """, (playlist_name,))

    songs = [
        dict(row)
        for row in cursor.fetchall()
    ]

    conn.close()

    return songs


# =========================================
# ADD SONG
# =========================================
def add_song_to_playlist(
    playlist_name,
    song_filename
):

    from app.core.database import get_connection

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM playlists
        WHERE playlist_name = ?
        AND song_filename = ?
    """, (
        playlist_name,
        song_filename
    ))

    exists = cursor.fetchone()

    if exists:

        conn.close()

        return {
            "status": True,
            "message": "Song already exists"
        }

    cursor.execute("""
        INSERT INTO playlists
        (
            playlist_name,
            song_filename
        )
        VALUES (?, ?)
    """, (
        playlist_name,
        song_filename
    ))

    conn.commit()

    conn.close()

    return {
        "status": True,
        "message": "Song added"
    }


# =========================================
# REMOVE SONG
# =========================================
def remove_song_from_playlist(
    playlist_name,
    song_filename
):

    from app.core.database import get_connection

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM playlists
        WHERE playlist_name = ?
        AND song_filename = ?
    """, (
        playlist_name,
        song_filename
    ))

    conn.commit()

    conn.close()

    return {
        "status": True
    }


# =========================================
# DELETE PLAYLIST
# =========================================
def delete_playlist(playlist_name):

    from app.core.database import get_connection

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM playlists
        WHERE playlist_name = ?
    """, (playlist_name,))

    conn.commit()

    conn.close()

    return {
        "status": True
    }
