import os
import sys

from app.core.constants import (
    DOWNLOAD_FOLDER
)

IS_WINDOWS = sys.platform == "win32"
CURRENT_SONG = None

if IS_WINDOWS:
    import ctypes
    
    def send_mci_command(command):
        try:
            # We use mciSendStringW (Unicode version)
            ctypes.windll.winmm.mciSendStringW(command, None, 0, 0)
            return True
        except Exception:
            return False
else:
    def send_mci_command(command):
        return True

# =========================================
# PLAY
# =========================================
def play_music(song_name):
    global CURRENT_SONG

    song_path = os.path.normpath(os.path.abspath(os.path.join(
        DOWNLOAD_FOLDER,
        song_name
    )))

    if IS_WINDOWS:
        # Stop and close any previous playback to avoid conflict
        send_mci_command("stop myg")
        send_mci_command("close myg")
        
        # Open and play the new song. Double quotes protect spaces in file path.
        success = send_mci_command(f'open "{song_path}" type mpegvideo alias myg')
        if success:
            send_mci_command("play myg")
            CURRENT_SONG = song_name
        else:
            CURRENT_SONG = None
    else:
        # Simulated fallback for cloud/non-Windows environments (like Streamlit Cloud)
        CURRENT_SONG = song_name

# =========================================
# STOP
# =========================================
def stop_music():
    global CURRENT_SONG
    if IS_WINDOWS:
        send_mci_command("stop myg")
        send_mci_command("close myg")
    CURRENT_SONG = None

# =========================================
# PAUSE
# =========================================
def pause_music():
    if IS_WINDOWS:
        send_mci_command("pause myg")

# =========================================
# RESUME
# =========================================
def resume_music():
    if IS_WINDOWS:
        send_mci_command("resume myg")

# =========================================
# CURRENT SONG
# =========================================
def current_song():
    return CURRENT_SONG