import pygame
import os

from app.core.constants import (
    DOWNLOAD_FOLDER
)

pygame.mixer.init()

CURRENT_SONG = None

# =========================================
# PLAY
# =========================================
def play_music(song_name):

    global CURRENT_SONG

    song_path = os.path.join(
        DOWNLOAD_FOLDER,
        song_name
    )

    pygame.mixer.music.stop()

    pygame.mixer.music.load(
        song_path
    )

    pygame.mixer.music.play()

    CURRENT_SONG = song_name

# =========================================
# STOP
# =========================================
def stop_music():

    pygame.mixer.music.stop()

# =========================================
# PAUSE
# =========================================
def pause_music():

    pygame.mixer.music.pause()

# =========================================
# RESUME
# =========================================
def resume_music():

    pygame.mixer.music.unpause()

# =========================================
# CURRENT SONG
# =========================================
def current_song():

    return CURRENT_SONG