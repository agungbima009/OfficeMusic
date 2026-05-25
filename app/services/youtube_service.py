import html
import time
import yt_dlp
from googleapiclient.discovery import build

from app.core.config import API_KEY
from app.core.constants import MAX_RESULTS

# ===========================================================
# SEARCH RESULT CACHE
# Kompleksitas lookup: O(1) rata-rata (dict hash lookup)
# TTL: 5 menit — query yang sama tidak memanggil API/yt-dlp lagi
# ===========================================================
_SEARCH_CACHE: dict = {}       # { query: (timestamp, results) }
_CACHE_TTL_SECONDS = 300       # 5 menit


def _get_cached(query: str):
    """Kembalikan hasil cache jika masih valid, else None — O(1)."""
    entry = _SEARCH_CACHE.get(query)
    if entry and (time.monotonic() - entry[0]) < _CACHE_TTL_SECONDS:
        return entry[1]
    return None


def _set_cache(query: str, results: list):
    """Simpan hasil ke cache — O(1)."""
    _SEARCH_CACHE[query] = (time.monotonic(), results)


def yt_dlp_search_music(query):
    # Kompleksitas: O(N) di mana N = MAX_RESULTS
    # Tidak ada nested loop; setiap entry diproses sekali saja.
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': True,
        'force_generic_extractor': False,
        'socket_timeout': 15,
        'retries': 3,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(
                f"ytsearch{MAX_RESULTS}:{query}",
                download=False
            )
            entries = result.get('entries', []) or []

            # Single-pass list comprehension: O(N)
            videos = []
            for entry in entries:
                if not entry:
                    continue
                video_id = entry.get('id')
                if not video_id:
                    continue

                thumbnails = entry.get('thumbnails') or []
                thumbnail_url = (
                    thumbnails[-1].get('url', '')
                    if thumbnails
                    else f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
                )
                if not thumbnail_url:
                    thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

                videos.append({
                    "title":   html.unescape(entry.get('title') or entry.get('name') or "Unknown Title"),
                    "channel": html.unescape(entry.get('uploader') or entry.get('channel') or "Unknown Channel"),
                    "thumbnail": thumbnail_url,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                })
            return videos
    except Exception as e:
        print(f"Error searching with yt-dlp: {e}")
        return []


def youtube_search_music(query):
    """
    Big-O ringkasan:
      Cache hit  → O(1)   (dict lookup)
      Google API → O(N)   N = item di response (maks MAX_RESULTS)
      yt-dlp     → O(N)   N = MAX_RESULTS
    Untuk query yang sama dalam 5 menit, selalu O(1).
    """
    # 1. Cache hit — O(1)
    cached = _get_cached(query)
    if cached is not None:
        return cached

    videos = []

    # 2. Coba Google YouTube Data API v3 — O(N)
    if API_KEY:
        try:
            youtube = build("youtube", "v3", developerKey=API_KEY)
            response = youtube.search().list(
                q=query,
                part="id,snippet",
                type="video",
                maxResults=MAX_RESULTS,
                topicId="/m/04rlf",
            ).execute()

            # Single-pass loop O(N)
            for item in response.get("items", []):
                video_id = item["id"]["videoId"]
                videos.append({
                    "title":     html.unescape(item["snippet"]["title"]),
                    "channel":   html.unescape(item["snippet"]["channelTitle"]),
                    "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                    "url":       f"https://www.youtube.com/watch?v={video_id}",
                })

            if videos:
                _set_cache(query, videos)   # simpan ke cache — O(1)
                return videos

        except Exception as e:
            print(f"Google YouTube API search failed: {e}. Falling back to yt-dlp...")

    # 3. Fallback yt-dlp — O(N)
    videos = yt_dlp_search_music(query)
    if videos:
        _set_cache(query, videos)
    return videos
