import yt_dlp

from app.core.constants import (
    DOWNLOAD_FOLDER,
    VIDEO_FOLDER
)

from app.utils.helper import safe_filename

DOWNLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

VIDEO_FOLDER.mkdir(parents=True, exist_ok=True)

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

    title = safe_filename(
        video['title']
    )

    filename = f"{title}.mp3"

    output_mp3 = DOWNLOAD_FOLDER / filename

    if output_mp3.exists():

        register_song(video, filename)

        return str(output_mp3), True

    ydl_opts = {

        'format':
            'bestaudio/best',

        'outtmpl':
            str(DOWNLOAD_FOLDER / f"{title}.%(ext)s"),

        'quiet':
            True,

        'noplaylist':
            True,

        'extractor_args': {
            'youtube': {
                'player_client': ['android']
            }
        },

        'postprocessors': [{

            'key':
                'FFmpegExtractAudio',

            'preferredcodec':
                'mp3',

            'preferredquality':
                '192',

        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        ydl.download(
            [video['url']]
        )

    register_song(video, filename)

    return str(output_mp3), False


def download_video(video):

    title = safe_filename(
        video['title']
    )

    output_mp4 = VIDEO_FOLDER / f"{title}.mp4"

    if output_mp4.exists():

        return str(output_mp4), True

    ydl_opts = {

        'format':
            'bestvideo+bestaudio/best',

        'outtmpl':
            str(VIDEO_FOLDER / f"{title}.%(ext)s"),

        'quiet':
            True,

        'noplaylist':
            True,

        'merge_output_format':
            'mp4',

        'extractor_args': {
            'youtube': {
                'player_client': ['android']
            }
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        ydl.download(
            [video['url']]
        )

    return str(output_mp4), False