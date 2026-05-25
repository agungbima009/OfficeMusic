import os
import html
import yt_dlp

from app.core.constants import (
    DOWNLOAD_FOLDER,
    VIDEO_FOLDER
)

from app.utils.helper import safe_filename

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

os.makedirs(VIDEO_FOLDER, exist_ok=True)

DOWNLOAD_STATUS = {}

def check_cached_audio(video):
    video['title'] = html.unescape(video.get('title', 'Unknown Song'))
    title = safe_filename(video['title'])
    filename = f"{title}.mp3"
    output_mp3 = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(output_mp3):
        return output_mp3, True
    return output_mp3, False


def check_cached_video(video):
    video['title'] = html.unescape(video.get('title', 'Unknown Video'))
    title = safe_filename(video['title'])
    output_mp4 = os.path.join(VIDEO_FOLDER, f"{title}.mp4")
    if os.path.exists(output_mp4):
        return output_mp4, True
    return output_mp4, False


def make_progress_hook(url):
    def hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)
            percentage = (downloaded / total * 100) if total else 0
            speed = d.get('speed', 0) or 0
            eta = d.get('eta', 0) or 0
            
            DOWNLOAD_STATUS[url] = {
                "status": "downloading",
                "percentage": round(percentage, 2),
                "downloaded_bytes": downloaded,
                "total_bytes": total,
                "speed": speed,
                "eta": eta
            }
        elif d['status'] == 'finished':
            DOWNLOAD_STATUS[url] = {
                "status": "finished",
                "percentage": 100.0,
                "speed": 0,
                "eta": 0
            }
    return hook


def register_song(video, filename):
    from app.core.database import get_connection
    title = video.get('title', 'Unknown Title')
    channel = video.get('channel', 'Unknown Channel')
    thumbnail = video.get('thumbnail', '')
    url = video.get('url', '')

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM songs WHERE filename = ?", (filename,))
        row = cursor.fetchone()
        if not row:
            cursor.execute(
                "INSERT INTO songs (title, filename, channel, thumbnail, youtube_url, downloaded) VALUES (?, ?, ?, ?, ?, 1)",
                (title, filename, channel, thumbnail, url)
            )
            conn.commit()
    except Exception as e:
        print(f"Error registering song in DB: {e}")
    finally:
        conn.close()

def download_audio(video):
    try:
        url = video.get('url')
        if not url:
            raise ValueError("URL video tidak ditemukan")

        video['title'] = html.unescape(video.get('title', 'Unknown Song'))
        video['channel'] = html.unescape(video.get('channel', 'Unknown Channel'))

        title = safe_filename(
            video['title']
        )

        filename = f"{title}.mp3"
        output_mp3 = os.path.join(DOWNLOAD_FOLDER, filename)

        if os.path.exists(output_mp3):
            register_song(video, filename)
            DOWNLOAD_STATUS[url] = {
                "status": "finished",
                "percentage": 100.0,
                "speed": 0,
                "eta": 0
            }
            return output_mp3, True

        # Initialize status
        DOWNLOAD_STATUS[url] = {
            "status": "downloading",
            "percentage": 0.0,
            "speed": 0,
            "eta": 0
        }

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, f"{title}.%(ext)s"),
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'socket_timeout': 30,          # Mengurangi kemungkinan gantung saat koneksi lambat
            'retries': 10,                 # Mengulang jika terjadi error network
            'fragment_retries': 10,        # Mengulang download fragmen video
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios', 'web'] # Mencoba berbagai client jika salah satu diblokir
                }
            },
            'progress_hooks': [make_progress_hook(url)],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        register_song(video, filename)
        DOWNLOAD_STATUS[url] = {
            "status": "finished",
            "percentage": 100.0,
            "speed": 0,
            "eta": 0
        }
        return output_mp3, False

    except Exception as e:
        print(f"Error dalam download_audio: {e}")
        DOWNLOAD_STATUS[url] = {
            "status": "failed",
            "percentage": 0.0,
            "error": str(e)
        }
        raise e


def download_video(video):
    try:
        url = video.get('url')
        if not url:
            raise ValueError("URL video tidak ditemukan")

        video['title'] = html.unescape(video.get('title', 'Unknown Video'))
        video['channel'] = html.unescape(video.get('channel', 'Unknown Channel'))

        title = safe_filename(
            video['title']
        )

        output_mp4 = os.path.join(VIDEO_FOLDER, f"{title}.mp4")

        if os.path.exists(output_mp4):
            DOWNLOAD_STATUS[url] = {
                "status": "finished",
                "percentage": 100.0,
                "speed": 0,
                "eta": 0
            }
            return output_mp4, True

        # Initialize status
        DOWNLOAD_STATUS[url] = {
            "status": "downloading",
            "percentage": 0.0,
            "speed": 0,
            "eta": 0
        }

        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(VIDEO_FOLDER, f"{title}.%(ext)s"),
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'socket_timeout': 30,
            'retries': 10,
            'fragment_retries': 10,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios', 'web']
                }
            },
            'progress_hooks': [make_progress_hook(url)],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        DOWNLOAD_STATUS[url] = {
            "status": "finished",
            "percentage": 100.0,
            "speed": 0,
            "eta": 0
        }
        return output_mp4, False

    except Exception as e:
        print(f"Error dalam download_video: {e}")
        DOWNLOAD_STATUS[url] = {
            "status": "failed",
            "percentage": 0.0,
            "error": str(e)
        }
        raise e