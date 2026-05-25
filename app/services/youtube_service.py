import html
import yt_dlp
from googleapiclient.discovery import build

from app.core.config import API_KEY
from app.core.constants import MAX_RESULTS

def yt_dlp_search_music(query):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': True,
        'force_generic_extractor': False,
        'playlist_items': f'1-{MAX_RESULTS}',
        'socket_timeout': 15,
        'retries': 3
    }
    videos = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Menggunakan prefix ytsearch untuk pencarian YouTube
            result = ydl.extract_info(f"ytsearch{MAX_RESULTS}:{query}", download=False)
            if 'entries' in result:
                for entry in result['entries']:
                    if not entry:
                        continue
                    video_id = entry.get('id')
                    if not video_id:
                        continue
                        
                    # Dapatkan thumbnail resolusi tinggi atau default
                    thumbnails = entry.get('thumbnails', [])
                    thumbnail_url = ""
                    if thumbnails:
                        thumbnail_url = thumbnails[-1].get('url', '')
                    if not thumbnail_url:
                        thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
                        
                    videos.append({
                        "title": html.unescape(entry.get('title') or entry.get('name') or "Unknown Title"),
                        "channel": html.unescape(entry.get('uploader') or entry.get('channel') or "Unknown Channel"),
                        "thumbnail": thumbnail_url,
                        "url": f"https://www.youtube.com/watch?v={video_id}"
                    })
    except Exception as e:
        print(f"Error searching with yt-dlp: {e}")
    return videos

def youtube_search_music(query):
    # Coba gunakan Google YouTube API jika API_KEY tersedia
    if API_KEY:
        try:
            youtube = build(
                "youtube",
                "v3",
                developerKey=API_KEY
            )

            response = youtube.search().list(
                q=query,
                part="id,snippet",
                type="video",
                maxResults=MAX_RESULTS,
                topicId="/m/04rlf"
            ).execute()

            videos = []
            for item in response.get("items", []):
                video_id = item["id"]["videoId"]
                videos.append({
                    "title": html.unescape(item["snippet"]["title"]),
                    "channel": html.unescape(item["snippet"]["channelTitle"]),
                    "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                    "url": f"https://www.youtube.com/watch?v={video_id}"
                })
            
            if videos:
                return videos
        except Exception as e:
            print(f"Google YouTube API search failed: {e}. Falling back to yt-dlp...")

    # Fallback pencarian menggunakan yt-dlp
    return yt_dlp_search_music(query)