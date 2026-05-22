from fastapi import APIRouter

from app.services.player_service import (

    play_music,

    stop_music,

    pause_music,

    resume_music,

    current_song
)

router = APIRouter()

# =========================================
# PLAY
# =========================================
@router.post("/play/{song_name}")
def play(song_name: str):

    play_music(song_name)

    return {

        "status": True,

        "message": f"Playing {song_name}"
    }

# =========================================
# STOP
# =========================================
@router.post("/stop")
def stop():

    stop_music()

    return {

        "status": True,

        "message": "Music stopped"
    }

# =========================================
# PAUSE
# =========================================
@router.post("/pause")
def pause():

    pause_music()

    return {

        "status": True,

        "message": "Music paused"
    }

# =========================================
# RESUME
# =========================================
@router.post("/resume")
def resume():

    resume_music()

    return {

        "status": True,

        "message": "Music resumed"
    }

# =========================================
# CURRENT PLAYING
# =========================================
@router.get("/current")
def current():

    return {

        "status": True,

        "current_song": current_song()
    }