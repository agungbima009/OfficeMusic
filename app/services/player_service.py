
import os
import time
import sys
import threading

if sys.platform == "win32":
    import ctypes
else:
    ctypes = None  # type: ignore[assignment]

from app.core.constants import DOWNLOAD_FOLDER

IS_WINDOWS = sys.platform == "win32"

# =========================================================
# PLAYER STATE
# =========================================================
CURRENT_SONG = None

PLAYLIST_QUEUE = []

QUEUE_INDEX = 0

PLAYER_LOCK = threading.Lock()

# =========================================================
# WINDOWS AUDIO API
# =========================================================
def send_mci_command(command: str) -> bool:
    if not IS_WINDOWS or ctypes is None:
        return True
    try:
        ctypes.windll.winmm.mciSendStringW(command, None, 0, 0)  # type: ignore[union-attr]
        return True
    except Exception:
        return False


# =========================================================
# INTERNAL PLAY
# =========================================================
def _play(song_name):

    global CURRENT_SONG

    song_path = os.path.join(DOWNLOAD_FOLDER, song_name)

    if not os.path.exists(song_path):

        raise FileNotFoundError(
            f"Music not found: {song_path}"
        )

    # =====================================================
    # WINDOWS LOCAL PLAYBACK
    # =====================================================
    if IS_WINDOWS:

        send_mci_command("stop myg")

        send_mci_command("close myg")

        success = send_mci_command(
            f'open "{song_path}" type mpegvideo alias myg'
        )

        if success:

            send_mci_command("play myg")

            CURRENT_SONG = song_name

        else:

            CURRENT_SONG = None

    # =====================================================
    # LINUX / VPS MODE
    # =====================================================
    else:

        # VPS tidak memutar audio
        # hanya update state player

        CURRENT_SONG = song_name

        print(
            f"[LINUX MODE] Current song: {song_name}"
        )

    return CURRENT_SONG


# =========================================================
# PLAY MUSIC
# =========================================================
def play_music(song_name):

    with PLAYER_LOCK:

        return _play(song_name)


# =========================================================
# PLAYLIST QUEUE
# =========================================================
def set_playlist_queue(songs):

    global PLAYLIST_QUEUE
    global QUEUE_INDEX

    with PLAYER_LOCK:

        PLAYLIST_QUEUE = songs

        QUEUE_INDEX = 0

        if not PLAYLIST_QUEUE:
            return None

        return _play(
            PLAYLIST_QUEUE[0]
        )


# =========================================================
# NEXT SONG
# =========================================================
def next_song():

    global QUEUE_INDEX

    with PLAYER_LOCK:

        if not PLAYLIST_QUEUE:
            return None

        QUEUE_INDEX += 1

        if QUEUE_INDEX >= len(PLAYLIST_QUEUE):
            QUEUE_INDEX = 0

        return _play(
            PLAYLIST_QUEUE[QUEUE_INDEX]
        )


# =========================================================
# PREVIOUS SONG
# =========================================================
def previous_song():

    global QUEUE_INDEX

    with PLAYER_LOCK:

        if not PLAYLIST_QUEUE:
            return None

        QUEUE_INDEX -= 1

        if QUEUE_INDEX < 0:
            QUEUE_INDEX = (
                len(PLAYLIST_QUEUE) - 1
            )

        return _play(
            PLAYLIST_QUEUE[QUEUE_INDEX]
        )


# =========================================================
# STOP MUSIC
# =========================================================
def stop_music():

    global CURRENT_SONG

    with PLAYER_LOCK:

        if IS_WINDOWS:

            send_mci_command("stop myg")

            send_mci_command("close myg")

        CURRENT_SONG = None

    return CURRENT_SONG


# =========================================================
# PAUSE MUSIC
# =========================================================
def pause_music():

    if IS_WINDOWS:

        send_mci_command("pause myg")

    # Linux mode: state-only, tidak ada subprocess yang perlu di-pause


# =========================================================
# RESUME MUSIC
# =========================================================
def resume_music():

    if IS_WINDOWS:

        send_mci_command("resume myg")

    # Linux mode: state-only, tidak ada subprocess yang perlu di-resume


# =========================================================
# CURRENT SONG
# =========================================================
def current_song():

    return CURRENT_SONG


# =========================================================
# CURRENT PLAYLIST
# =========================================================
def current_playlist():

    return PLAYLIST_QUEUE


# =========================================================
# CURRENT INDEX
# =========================================================
def current_index():

    return QUEUE_INDEX


# =========================================================
# BACKGROUND PLAYBACK MONITOR (FOR WINDOWS MCI)
# =========================================================
def monitor_playback():
    global QUEUE_INDEX, PLAYLIST_QUEUE, CURRENT_SONG
    while True:
        try:
            time.sleep(1)
            if not IS_WINDOWS:
                continue
                
            if not CURRENT_SONG:
                continue
                
            buffer = ctypes.create_unicode_buffer(64)
            res = ctypes.windll.winmm.mciSendStringW("status myg mode", buffer, 64, 0)
            if res != 0:
                mode = "stopped"
            else:
                mode = buffer.value.strip().lower()
                
            if mode in ["stopped", ""]:
                with PLAYER_LOCK:
                    if PLAYLIST_QUEUE and CURRENT_SONG:
                        QUEUE_INDEX += 1
                        if QUEUE_INDEX < len(PLAYLIST_QUEUE):
                            _play(PLAYLIST_QUEUE[QUEUE_INDEX])
                        else:
                            # Selesai memutar semua lagu di queue
                            CURRENT_SONG = None
                            PLAYLIST_QUEUE = []
                            QUEUE_INDEX = 0
        except Exception:
            pass

if IS_WINDOWS:
    monitor_thread = threading.Thread(target=monitor_playback, daemon=True)
    monitor_thread.start()