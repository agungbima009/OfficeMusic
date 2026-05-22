# =========================================
# LOCAL PLAYLIST PLAYER
# =========================================

import tkinter as tk
from tkinter import messagebox
import pygame
import os

# =========================================
# CONFIG
# =========================================
MUSIC_FOLDER = "music_cache"

# =========================================
# INIT PYGAME
# =========================================
pygame.mixer.init()

# =========================================
# GUI CLASS
# =========================================
class PlaylistPlayerGUI:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Offline Playlist Player"
        )

        self.root.geometry(
            "1000x750"
        )

        self.root.configure(
            bg="#0f0f0f"
        )

        self.current_song = None

        self.play_all_mode = False

        # =====================================
        # TITLE
        # =====================================
        title = tk.Label(

            root,

            text="Offline Playlist Player",

            font=("Arial", 30, "bold"),

            bg="#0f0f0f",

            fg="#ff0000"
        )

        title.pack(
            pady=20
        )

        # =====================================
        # STATUS
        # =====================================
        self.status_label = tk.Label(

            root,

            text="Ready",

            font=("Arial", 12),

            bg="#0f0f0f",

            fg="#aaaaaa"
        )

        self.status_label.pack(
            pady=10
        )

        # =====================================
        # PLAY MODE FRAME
        # =====================================
        mode_frame = tk.Frame(
            root,
            bg="#0f0f0f"
        )

        mode_frame.pack(
            pady=10
        )

        self.play_mode = tk.StringVar(
            value="selected"
        )

        selected_radio = tk.Radiobutton(

            mode_frame,

            text="Play Selected Only",

            variable=self.play_mode,

            value="selected",

            font=("Arial", 12, "bold"),

            bg="#0f0f0f",

            fg="white",

            selectcolor="#1e1e1e",

            activebackground="#0f0f0f",

            activeforeground="white"
        )

        selected_radio.grid(
            row=0,
            column=0,
            padx=15
        )

        all_radio = tk.Radiobutton(

            mode_frame,

            text="Play All Playlist",

            variable=self.play_mode,

            value="all",

            font=("Arial", 12, "bold"),

            bg="#0f0f0f",

            fg="white",

            selectcolor="#1e1e1e",

            activebackground="#0f0f0f",

            activeforeground="white"
        )

        all_radio.grid(
            row=0,
            column=1,
            padx=15
        )

        # =====================================
        # PLAYLIST FRAME
        # =====================================
        playlist_frame = tk.Frame(
            root,
            bg="#0f0f0f"
        )

        playlist_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        # =====================================
        # SCROLLBAR
        # =====================================
        scrollbar = tk.Scrollbar(
            playlist_frame
        )

        scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        # =====================================
        # LISTBOX
        # =====================================
        self.playlist_box = tk.Listbox(

            playlist_frame,

            font=("Arial", 14),

            bg="#1e1e1e",

            fg="white",

            selectbackground="#ff0000",

            selectforeground="white",

            relief="flat",

            yscrollcommand=scrollbar.set
        )

        self.playlist_box.pack(

            side=tk.LEFT,

            fill="both",

            expand=True
        )

        scrollbar.config(
            command=self.playlist_box.yview
        )

        # =====================================
        # BUTTON FRAME
        # =====================================
        button_frame = tk.Frame(
            root,
            bg="#0f0f0f"
        )

        button_frame.pack(
            pady=20
        )

        # =====================================
        # PLAY BUTTON
        # =====================================
        play_btn = tk.Button(

            button_frame,

            text="▶ Play",

            font=("Arial", 13, "bold"),

            bg="#ff0000",

            fg="white",

            relief="flat",

            padx=20,

            pady=10,

            command=self.play_selected
        )

        play_btn.grid(
            row=0,
            column=0,
            padx=10
        )

        # =====================================
        # STOP BUTTON
        # =====================================
        stop_btn = tk.Button(

            button_frame,

            text="■ Stop",

            font=("Arial", 13, "bold"),

            bg="#444444",

            fg="white",

            relief="flat",

            padx=20,

            pady=10,

            command=self.stop_music
        )

        stop_btn.grid(
            row=0,
            column=1,
            padx=10
        )

        # =====================================
        # NEXT BUTTON
        # =====================================
        next_btn = tk.Button(

            button_frame,

            text="⏭ Next",

            font=("Arial", 13, "bold"),

            bg="#1db954",

            fg="white",

            relief="flat",

            padx=20,

            pady=10,

            command=self.next_song
        )

        next_btn.grid(
            row=0,
            column=2,
            padx=10
        )

        # =====================================
        # PREVIOUS BUTTON
        # =====================================
        prev_btn = tk.Button(

            button_frame,

            text="⏮ Previous",

            font=("Arial", 13, "bold"),

            bg="#1e90ff",

            fg="white",

            relief="flat",

            padx=20,

            pady=10,

            command=self.previous_song
        )

        prev_btn.grid(
            row=0,
            column=3,
            padx=10
        )

        # =====================================
        # REFRESH BUTTON
        # =====================================
        refresh_btn = tk.Button(

            button_frame,

            text="🔄 Refresh",

            font=("Arial", 13, "bold"),

            bg="#ff9800",

            fg="white",

            relief="flat",

            padx=20,

            pady=10,

            command=self.load_playlist
        )

        refresh_btn.grid(
            row=0,
            column=4,
            padx=10
        )

        # =====================================
        # DOUBLE CLICK PLAY
        # =====================================
        self.playlist_box.bind(
            "<Double-Button-1>",
            lambda e: self.play_selected()
        )

        # =====================================
        # AUTO NEXT CHECK
        # =====================================
        self.check_music_end()

        # =====================================
        # LOAD PLAYLIST
        # =====================================
        self.load_playlist()

    # =========================================
    # LOAD PLAYLIST
    # =========================================
    def load_playlist(self):

        self.playlist_box.delete(
            0,
            tk.END
        )

        if not os.path.exists(MUSIC_FOLDER):

            os.makedirs(MUSIC_FOLDER)

        songs = [

            file for file in os.listdir(MUSIC_FOLDER)

            if file.endswith(".mp3")
        ]

        songs.sort()

        self.songs = songs

        for song in songs:

            self.playlist_box.insert(
                tk.END,
                song
            )

        self.status_label.config(
            text=f"{len(songs)} songs loaded"
        )

    # =========================================
    # PLAY SONG
    # =========================================
    def play_song(self, index):

        try:

            song_name = self.songs[index]

            song_path = os.path.join(
                MUSIC_FOLDER,
                song_name
            )

            pygame.mixer.music.stop()

            pygame.mixer.music.load(
                song_path
            )

            pygame.mixer.music.play()

            self.current_song = index

            self.playlist_box.selection_clear(
                0,
                tk.END
            )

            self.playlist_box.selection_set(
                index
            )

            self.playlist_box.activate(
                index
            )

            mode_text = (
                "Playlist Mode"
                if self.play_mode.get() == "all"
                else "Selected Mode"
            )

            self.status_label.config(
                text=f"{mode_text} | Playing: {song_name}"
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )

    # =========================================
    # PLAY SELECTED
    # =========================================
    def play_selected(self):

        selected = self.playlist_box.curselection()

        if not selected:

            messagebox.showwarning(
                "Warning",
                "Select a song first."
            )

            return

        index = selected[0]

        self.play_song(index)

    # =========================================
    # STOP MUSIC
    # =========================================
    def stop_music(self):

        pygame.mixer.music.stop()

        self.status_label.config(
            text="Stopped"
        )

    # =========================================
    # NEXT SONG
    # =========================================
    def next_song(self):

        if self.current_song is None:

            return

        next_index = self.current_song + 1

        if next_index >= len(self.songs):

            next_index = 0

        self.play_song(next_index)

    # =========================================
    # PREVIOUS SONG
    # =========================================
    def previous_song(self):

        if self.current_song is None:

            return

        prev_index = self.current_song - 1

        if prev_index < 0:

            prev_index = len(self.songs) - 1

        self.play_song(prev_index)

    # =========================================
    # AUTO PLAY NEXT
    # =========================================
    def check_music_end(self):

        if not pygame.mixer.music.get_busy():

            if (

                self.play_mode.get() == "all"

                and self.current_song is not None

            ):

                self.next_song()

        self.root.after(
            1000,
            self.check_music_end
        )

# =========================================
# MAIN
# =========================================
def main():

    root = tk.Tk()

    app = PlaylistPlayerGUI(root)

    root.mainloop()

# =========================================
# RUN
# =========================================
if __name__ == "__main__":

    main()