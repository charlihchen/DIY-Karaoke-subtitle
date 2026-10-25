"""mix2kmac -- mix a karaoke video + instrumental audio into one file.

macOS GUI. Picks a video (歌影) and an instrumental track (伴奏)
and builds a stereo file with the instrumental on the left channel
and the original (vocal) audio on the right -- "左伴右唱".

Built with PyInstaller into mix2kmac.app (see .github/workflows/
build-apps.yml). ffmpeg ships inside the app, so no separate
ffmpeg install is needed.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import karaoke_common as kc


class FFmpegMixerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Load Video and Audio to Mix into Karaoke Song (macOS/FFmpeg)")

        self.video_label = tk.Label(root, text="Load Video(歌影) File (MP4/MKV/MPG/AVI):")
        self.video_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.video_entry = tk.Entry(root, width=50)
        self.video_entry.grid(row=0, column=1, padx=5, pady=5)

        self.video_button = tk.Button(root, text="Browse(載入)", command=self.load_video)
        self.video_button.grid(row=0, column=2, padx=5, pady=5)

        self.audio_label = tk.Label(root, text="Load Instrumental Audio(伴奏) File (MP3/M4A):")
        self.audio_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.audio_entry = tk.Entry(root, width=50)
        self.audio_entry.grid(row=1, column=1, padx=5, pady=5)

        self.audio_button = tk.Button(root, text="Browse(載入)", command=self.load_audio)
        self.audio_button.grid(row=1, column=2, padx=5, pady=5)

        self.mix_button = tk.Button(root, text="Click here to Mix", command=self.mix_media)
        self.mix_button.grid(row=2, column=1, padx=5, pady=15)

        self.status_label = tk.Label(root, text="", fg="blue")
        self.status_label.grid(row=3, column=0, columnspan=3, padx=5, pady=2, sticky="w")

        self.progress = ttk.Progressbar(root, mode="indeterminate")
        self.progress.grid(row=4, column=0, columnspan=3, padx=5, pady=2, sticky="ew")

        self.job = kc.BackgroundJob(root, self.status_label, [self.mix_button])

    def load_video(self):
        video_filename = filedialog.askopenfilename(
            title="Select a Video File", filetypes=kc.VIDEO_TYPES
        )
        if video_filename:
            self.video_entry.delete(0, tk.END)
            self.video_entry.insert(0, video_filename)

    def load_audio(self):
        audio_filename = filedialog.askopenfilename(
            title="Select an Audio File", filetypes=kc.AUDIO_TYPES
        )
        if audio_filename:
            self.audio_entry.delete(0, tk.END)
            self.audio_entry.insert(0, audio_filename)

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
    root = tk.Tk()
    app = FFmpegMixerApp(root)
    root.mainloop()
