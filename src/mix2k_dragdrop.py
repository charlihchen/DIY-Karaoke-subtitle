"""mix2k_dragdrop -- drag-and-drop version of mix2k (Windows GUI).

Drop a video (歌影) onto the first box and an instrumental track
(伴奏) onto the second, then click Mix. Builds a stereo file with
the instrumental on the left channel and the original (vocal)
audio on the right -- "左伴右唱".

Needs tkinterdnd2 (pip install tkinterdnd2). Built with
PyInstaller into mix2k_dragdrop.exe (see .github/workflows/
build-apps.yml). ffmpeg ships inside the app.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from tkinterdnd2 import DND_FILES, TkinterDnD

import karaoke_common as kc


class FFmpegMixerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FFmpeg.exe Video and Audio Mixer to become Karaoke Song")

        self.video_label = tk.Label(root, text="Load Video(歌影) File (MP4/MKV/MPG/AVI):")
        self.video_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.video_entry = tk.Entry(root, width=50)
        self.video_entry.grid(row=0, column=1, padx=5, pady=5)
        self.video_entry.drop_target_register(DND_FILES)
        self.video_entry.dnd_bind("<<Drop>>", self.handle_video_drop)

        self.video_button = tk.Button(root, text="Browse(載入)", command=self.load_video)
        self.video_button.grid(row=0, column=2, padx=5, pady=5)

        self.audio_label = tk.Label(root, text="Load Instrumental Audio(伴奏) File (MP3/m4a):")
        self.audio_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.audio_entry = tk.Entry(root, width=50)
        self.audio_entry.grid(row=1, column=1, padx=5, pady=5)
        self.audio_entry.drop_target_register(DND_FILES)
        self.audio_entry.dnd_bind("<<Drop>>", self.handle_audio_drop)

        self.audio_button = tk.Button(root, text="Browse(載入)", command=self.load_audio)
        self.audio_button.grid(row=1, column=2, padx=5, pady=5)

        self.mix_button = tk.Button(root, text="Click here to Mix", command=self.mix_media)
        self.mix_button.grid(row=3, column=0, columnspan=3, pady=10)

        self.status_label = tk.Label(root, text="", fg="blue")
        self.status_label.grid(row=4, column=0, columnspan=3, padx=5, pady=2, sticky="w")

        self.progress = ttk.Progressbar(root, mode="indeterminate")
        self.progress.grid(row=5, column=0, columnspan=3, padx=5, pady=2, sticky="ew")

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

    def _dropped_path(self, event):
        # tkinterdnd2 gives one path, or "{path with spaces}" for a
        # single file, or several "{...} {...}" for several files.
        data = event.data.strip()
        if data.startswith("{"):
            end = data.find("}")
            if end != -1:
                return data[1:end]
        return data.split("} {")[0].strip("{}")

    def handle_video_drop(self, event):
        file_path = self._dropped_path(event)
        if file_path.lower().endswith(kc.VIDEO_EXTS) and os.path.isfile(file_path):
            self.video_entry.delete(0, tk.END)
            self.video_entry.insert(0, file_path)
        else:
            messagebox.showwarning("Invalid File", "Please drop a valid video file (MP4/MKV/MPG/AVI)")

    def handle_audio_drop(self, event):
        file_path = self._dropped_path(event)
        if file_path.lower().endswith(kc.AUDIO_EXTS) and os.path.isfile(file_path):
            self.audio_entry.delete(0, tk.END)
            self.audio_entry.insert(0, file_path)
        else:
            messagebox.showwarning("Invalid File", "Please drop a valid audio file (MP3/M4A)")

    def mix_media(self):
        video_file = self.video_entry.get().strip()
        audio_file = self.audio_entry.get().strip()

        if not video_file or not audio_file:
            messagebox.showerror("Error", "Please provide a video file and audio file.")
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
            output_file,
        ]

        def work():
            return kc.run_ffmpeg(command)

        def done(ok, message):
            self.progress.stop()
            if ok:
                messagebox.showinfo("Success", f"Media mixed successfully!\nOutput: {output_file}")
            else:
                messagebox.showerror("Error", f"Mixing failed.\n{message}")

        self.progress.start(20)
        self.job.start("Mixing... please wait, this can take a few minutes.", work, done)


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = FFmpegMixerApp(root)
    root.mainloop()
