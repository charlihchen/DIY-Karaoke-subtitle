"""12kmac -- one-file karaoke maker (macOS GUI).

Pick a video and the app does the rest:
1. extracts the audio with ffmpeg,
2. separates the instrumental with Demucs (no_vocals),
3. mixes video + instrumental + original audio into a stereo
   karaoke file -- "左伴右唱".

Demucs is NOT bundled into the app (bundling it makes a ~330 MB
app that takes 2-3 minutes to start -- see README). You still
need Python with ``pip install demucs``. The app checks for
demucs and tells you exactly how to install it when it is
missing. ffmpeg ships inside the app.

Built with PyInstaller into 12kmac.app (see .github/workflows/
build-apps.yml).
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import karaoke_common as kc


class FFmpegMixerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Load Video & extract NoVocal.mp3 by Demucs, mix it and Video to Karaoke Song by FFmpeg")

        self.video_label = tk.Label(root, text="Load Video File (MP4/MKV/MPG/AVI):")
        self.video_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.video_entry = tk.Entry(root, width=50)
        self.video_entry.grid(row=0, column=1, padx=5, pady=5)

        self.video_button = tk.Button(root, text="Browse", command=self.load_video)
        self.video_button.grid(row=0, column=2, padx=5, pady=5)

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

    def mix_media(self):
        video_file = self.video_entry.get().strip()

        if not video_file:
            messagebox.showerror("Error", "Please provide a video file.")
            return
        if not os.path.isfile(video_file):
            messagebox.showerror("Error", f"Video file not found:\n{video_file}")
            return

        ffmpeg = kc.find_ffmpeg()
        if not ffmpeg:
            messagebox.showerror("FFmpeg not found", kc.ffmpeg_missing_message())
            return

        demucs = kc.find_demucs()
        if not demucs:
            messagebox.showerror("Demucs not found", kc.demucs_missing_message())
            return

        output_file = kc.karaoke_output_path(video_file, spaced=False)

        def work():
            return kc.separate_vocals_and_mix(ffmpeg, demucs, video_file, output_file)

        def done(ok, message):
            self.progress.stop()
            if ok:
                messagebox.showinfo("Success", f"Media mixed successfully!\nOutput: {output_file}")
            else:
                messagebox.showerror("Error", f"Mixing failed.\n{message}")

        self.progress.start(20)
        self.job.start(
            "Working... extracting audio, separating vocals with Demucs, then mixing. "
            "This takes a few minutes -- please wait.",
            work, done,
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = FFmpegMixerApp(root)
    root.mainloop()

# Make sure Demucs is installed. You can install it using pip:
# pip install demucs
# Created by Charlih Chen on 28AUG2024
# https://github.com/charlihchen
