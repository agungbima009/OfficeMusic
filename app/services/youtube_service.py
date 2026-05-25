import html
from googleapiclient.discovery import build

from app.core.config import API_KEY
from app.core.constants import MAX_RESULTS

def youtube_search_music(query):

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

            "title":
                html.unescape(item["snippet"]["title"]),

            "channel":
                html.unescape(item["snippet"]["channelTitle"]),

            "thumbnail":
                item["snippet"]["thumbnails"]["high"]["url"],

            "url":
                f"https://www.youtube.com/watch?v={video_id}"

        })

    return videos