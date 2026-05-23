
from fastapi import APIRouter
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

    current = play_music(song_name)

    return {
        "status": True,
        "current_song": current
    }


# =========================================================
# PLAY PLAYLIST
# =========================================================
@router.post("/playlist/play")
def play_playlist(data: PlaylistRequest):

    current = set_playlist_queue(
        data.songs
    )

    return {
        "status": True,
        "current_song": current
    }


# =========================================================
# NEXT SONG
# =========================================================
@router.post("/next")
def next_music():

    current = next_song()

    return {
        "status": True,
        "current_song": current
    }


# =========================================================
# PREVIOUS SONG
# =========================================================
@router.post("/previous")
def previous_music():

    current = previous_song()

    return {
        "status": True,
        "current_song": current
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

    return {
        "status": True,
        "current_song": current_song()
    }

