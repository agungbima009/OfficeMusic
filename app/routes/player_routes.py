
import os
import html as html_lib
from urllib.parse import unquote

from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.player_service import (
    play_music,
    stop_music,
    pause_music,
    resume_music,
    current_song,
    set_playlist_queue,
    next_song,
    previous_song,
)

from app.core.constants import DOWNLOAD_FOLDER

router = APIRouter()


# =========================================================
# REQUEST MODEL
# =========================================================
class PlaylistRequest(BaseModel):
    songs: list[str]


# =========================================================
# PLAY SINGLE MUSIC
# =========================================================
@router.post("/play/{song_name}")
def play(song_name: str):

    song_name = html_lib.unescape(unquote(song_name))
    current = play_music(song_name)

    return {
        "status": True,
        "current_song": current,
        "stream_url": f"/player/stream/{song_name}"
    }


# =========================================================
# PLAY PLAYLIST
# =========================================================
@router.post("/playlist/play")
def play_playlist(data: PlaylistRequest):

    songs = [html_lib.unescape(s) for s in data.songs]
    current = set_playlist_queue(
        songs
    )

    return {
        "status": True,
        "current_song": current,
        "stream_url": (
            f"/player/stream/{current}"
            if current else None
        )
    }


# =========================================================
# NEXT SONG
# =========================================================
@router.post("/next")
def next_music():

    current = next_song()

    return {
        "status": True,
        "current_song": current,
        "stream_url": (
            f"/player/stream/{current}"
            if current else None
        )
    }


# =========================================================
# PREVIOUS SONG
# =========================================================
@router.post("/previous")
def previous_music():

    current = previous_song()

    return {
        "status": True,
        "current_song": current,
        "stream_url": (
            f"/player/stream/{current}"
            if current else None
        )
    }


# =========================================================
# STOP
# =========================================================
@router.post("/stop")
def stop():

    stop_music()

    return {
        "status": True
    }


# =========================================================
# PAUSE
# =========================================================
@router.post("/pause")
def pause():

    pause_music()

    return {
        "status": True
    }


# =========================================================
# RESUME
# =========================================================
@router.post("/resume")
def resume():

    resume_music()

    return {
        "status": True
    }


# =========================================================
# CURRENT SONG
# =========================================================
@router.get("/current")
def current():

    song = current_song()

    return {
        "status": True,
        "current_song": song,
        "stream_url": (
            f"/player/stream/{song}"
            if song else None
        )
    }


# =========================================================
# STREAM AUDIO
# =========================================================
@router.get("/stream/{song_name}")
def stream(song_name: str):

    # Decode URL encoding lalu HTML entity (&amp; -> &)
    song_name = html_lib.unescape(unquote(song_name))

    song_path = os.path.join(
        DOWNLOAD_FOLDER,
        song_name
    )

    if not os.path.exists(song_path):

        return {
            "status": False,
            "message": "Music not found"
        }

    return FileResponse(
        path=song_path,
        media_type="audio/mpeg",
        filename=song_name
    )