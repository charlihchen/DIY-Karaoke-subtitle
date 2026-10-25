"""mix2kmac_dragdrop -- drag-and-drop version of mix2kmac (macOS GUI).

Drop a video (歌影) onto the first box and an instrumental track
(伴奏) onto the second (or paste a path with Cmd-V), then click
Mix. Builds a stereo file with the instrumental on the left
channel and the original (vocal) audio on the right -- "左伴右唱".

Needs tkinterdnd2 (pip install tkinterdnd2). Built with
PyInstaller into mix2kmac_dragdrop.app (see .github/workflows/
build-apps.yml). ffmpeg ships inside the app.
"""

import os
import shlex  # For parsing dropped file paths
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from tkinterdnd2 import DND_FILES, TkinterDnD

import karaoke_common as kc


class FFmpegMixerApp:
    """Tkinter app to mix video and audio files using FFmpeg.

    Supports drag-and-drop for input files and paste functionality.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("FFmpeg.exe Video and Audio Mixer to become Karaoke Song")
        self.root.grid_columnconfigure(1, weight=1)

        self.video_label = tk.Label(root, text="Load Video(歌影) File (MP4/MKV/MPG/AVI):")
        self.video_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.video_entry = tk.Entry(root, width=50)
        self.video_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.video_entry.drop_target_register(DND_FILES)
        self.video_entry.dnd_bind("<<Drop>>", self.handle_video_drop)
        self.video_entry.bind("<Control-v>", self.paste_video_path)
        self.video_entry.bind("<Command-v>", self.paste_video_path)  # macOS

        self.video_button = tk.Button(root, text="Browse(載入)", command=self.load_video)
        self.video_button.grid(row=0, column=2, padx=5, pady=5)

        self.audio_label = tk.Label(root, text="Load Instrumental Audio(伴奏) File (MP3/m4a):")
        self.audio_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.audio_entry = tk.Entry(root, width=50)
        self.audio_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.audio_entry.drop_target_register(DND_FILES)
        self.audio_entry.dnd_bind("<<Drop>>", self.handle_audio_drop)
        self.audio_entry.bind("<Control-v>", self.paste_audio_path)
        self.audio_entry.bind("<Command-v>", self.paste_audio_path)  # macOS

        self.audio_button = tk.Button(root, text="Browse(載入)", command=self.load_audio)
        self.audio_button.grid(row=1, column=2, padx=5, pady=5)

        self.mix_button = tk.Button(root, text="Click here to Mix", command=self.mix_media)
        self.mix_button.grid(row=2, column=0, columnspan=3, pady=10)

        self.status_label = tk.Label(root, text="", fg="blue")
        self.status_label.grid(row=3, column=0, columnspan=3, padx=5, pady=2, sticky="w")

        self.progress = ttk.Progressbar(root, mode="indeterminate")
        self.progress.grid(row=4, column=0, columnspan=3, padx=5, pady=2, sticky="ew")

        self.job = kc.BackgroundJob(root, self.status_label, [self.mix_button])

    def load_video(self):
        video_filename = filedialog.askopenfilename(filetypes=kc.VIDEO_TYPES)
        if video_filename:
            self.video_entry.delete(0, tk.END)
            self.video_entry.insert(0, video_filename)

    def load_audio(self):
        audio_filename = filedialog.askopenfilename(filetypes=kc.AUDIO_TYPES)
        if audio_filename:
            self.audio_entry.delete(0, tk.END)
            self.audio_entry.insert(0, audio_filename)

    def handle_drop(self, event, entry_widget):
        try:
            paths = shlex.split(event.data)
            if not paths:
                return
            file_path = paths[0]
            if file_path.startswith("{") and file_path.endswith("}"):
                file_path = file_path[1:-1]
            if os.path.isfile(file_path):
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, file_path)
            else:
                messagebox.showwarning("Invalid Drop", "Please drop a valid file.")
        except Exception as exc:
            messagebox.showerror("Drop Error", f"Could not process dropped item: {exc}")

    def handle_video_drop(self, event):
        self.handle_drop(event, self.video_entry)

    def handle_audio_drop(self, event):
        self.handle_drop(event, self.audio_entry)

    def paste_path(self, entry_widget):
        try:
            clipboard_content = self.root.clipboard_get()
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, clipboard_content)
        except tk.TclError:
            pass

    def paste_video_path(self, event):
        self.paste_path(self.video_entry)

    def paste_audio_path(self, event):
        self.paste_path(self.audio_entry)

    def mix_media(self):
        video_file = self.video_entry.get().strip()
        audio_file = self.audio_entry.get().strip()

        if not video_file or not audio_file:
            messagebox.showerror("Error", "Please provide both a video file and an audio file.")
            return
        if not os.path.isfile(video_file):
            messagebox.showerror("Error", f"Video file not found:\n{video_file}")
            return
        if not os.path.isfile(audio_file):
            messagebox.showerror("Error", f"Audio file not found:\n{audio_file}")
            return

        ffmpeg = kc.find_ffmpeg()
        if not ffmpeg:
            messagebox.showerror("FFmpeg not found", kc.ffmpeg_missing_message())
            return

        output_file = kc.karaoke_output_path(video_file, spaced=True)
        command = [
            ffmpeg,
            "-y",
            "-i", video_file,
            "-i", audio_file,
            "-map", "0:v",
            "-filter_complex", "[1:a][0:a]amerge=inputs=2,pan=stereo|c0<c0+c1|c1<c2+c3[a]",
            "-map", "[a]",
            "-ac", "2",  # ensure stereo output
            output_file,
        ]

        def work():
            return kc.run_ffmpeg(command)

        def done(ok, message):
            self.progress.stop()
            if ok:
                messagebox.showinfo("Success", f"Media mixed successfully!\nOutput: {output_file}")
            else:
                messagebox.showerror("Error", f"An error occurred during mixing:\n{message}")

        self.progress.start(20)
        self.job.start("Mixing... please wait, this can take a few minutes.", work, done)


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = FFmpegMixerApp(root)
    root.mainloop()
