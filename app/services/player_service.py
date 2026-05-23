import os
import sys
import threading

DOWNLOAD_FOLDER = "music_cache"

IS_WINDOWS = sys.platform.startswith("win")
IS_LINUX = sys.platform.startswith("linux")

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
if IS_WINDOWS:

    import ctypes

    def send_mci_command(command):

        try:

            ctypes.windll.winmm.mciSendStringW(
                command,
                None,
                0,
                0
            )

            return True

        except Exception:
            return False

else:

    def send_mci_command(command):
        return True


# =========================================================
# INTERNAL PLAY
# =========================================================
def _play(song_name):

    global CURRENT_SONG

    song_path = os.path.normpath(
        os.path.abspath(
            os.path.join(
                DOWNLOAD_FOLDER,
                song_name
            )
        )
    )

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

    return CURRENT_SONG


# =========================================================
# RESUME MUSIC
# =========================================================
def resume_music():

    if IS_WINDOWS:

        send_mci_command("resume myg")

    return CURRENT_SONG


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