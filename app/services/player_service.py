
import sys
import signal
import threading
import subprocess

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
# LINUX: subprocess-based player (mpg123 / ffplay)
# =========================================================
_linux_process = None  # holds the subprocess for Linux playback


def _kill_linux_process():
    global _linux_process
    if _linux_process and _linux_process.poll() is None:
        _linux_process.terminate()
        try:
            _linux_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            _linux_process.kill()
    _linux_process = None


def _get_linux_player():
    """Return the first available command-line audio player."""
    for player in ["mpg123", "ffplay", "aplay", "cvlc"]:
        result = subprocess.run(
            ["which", player],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return player
    return None


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
    global _linux_process

    song_file = DOWNLOAD_FOLDER / song_name
    song_path = str(song_file)

    if not song_file.exists():

        raise FileNotFoundError(
            f"Music not found: {song_path}"
        )

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

    else:
        # -------------------------------------------------------
        # Linux / VPS: gunakan mpg123 atau ffplay
        # -------------------------------------------------------
        _kill_linux_process()

        player = _get_linux_player()

        if player is None:
            # Tidak ada audio player tersedia di server
            # Tetap simpan state agar API bisa tracking lagu
            CURRENT_SONG = song_name
            print(
                f"[WARNING] Tidak ada audio player (mpg123/ffplay) di server. "
                f"Install dengan: sudo apt install mpg123"
            )
            return CURRENT_SONG

        if player == "mpg123":
            cmd = ["mpg123", "-q", song_path]

        elif player == "ffplay":
            cmd = [
                "ffplay", "-nodisp", "-autoexit",
                "-loglevel", "quiet", song_path
            ]

        elif player == "cvlc":
            cmd = ["cvlc", "--play-and-exit", song_path]

        else:
            cmd = [player, song_path]

        _linux_process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        CURRENT_SONG = song_name

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

        else:

            _kill_linux_process()

        CURRENT_SONG = None


# =========================================================
# PAUSE MUSIC
# =========================================================
def pause_music():

    if IS_WINDOWS:
        send_mci_command("pause myg")

    else:
        # mpg123 / ffplay tidak mendukung pause via signal standar,
        # kirim SIGSTOP ke process untuk pause
        global _linux_process
        if _linux_process and _linux_process.poll() is None:
            try:
                _linux_process.send_signal(signal.SIGSTOP)  # type: ignore[attr-defined]
            except Exception:
                pass


# =========================================================
# RESUME MUSIC
# =========================================================
def resume_music():

    if IS_WINDOWS:
        send_mci_command("resume myg")

    else:
        global _linux_process
        if _linux_process and _linux_process.poll() is None:
            try:
                _linux_process.send_signal(signal.SIGCONT)  # type: ignore[attr-defined]
            except Exception:
                pass


# =========================================================
# CURRENT SONG
# =========================================================
def current_song():

    return CURRENT_SONG
