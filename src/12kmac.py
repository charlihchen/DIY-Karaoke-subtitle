"""12kmac -- one-file karaoke maker (macOS GUI).

Pick a video and the app does the rest:
1. extracts the audio with ffmpeg,
2. separates the instrumental with UVR (MDX-Net models, the
   same engine as the UVR5 GUI) -- then
3. mixes video + instrumental + original audio into a stereo
   karaoke file -- "左伴右唱".

UVR is not bundled into the app (torch + friends are far too
big -- see README). It needs ``pip install
"audio-separator[cpu]" audioread`` (in a venv on macOS). The
app checks for it and tells you exactly how to install it
when it is missing. ffmpeg ships inside the app.

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
        self.root.title("Load Video & extract instrumental with UVR, mix it and Video to Karaoke Song by FFmpeg")

        self.video_label = tk.Label(root, text="Load Video File (MP4/MKV/MPG/AVI):")
        self.video_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.video_entry = tk.Entry(root, width=50)
        self.video_entry.grid(row=0, column=1, padx=5, pady=5)

        self.video_button = tk.Button(root, text="Browse", command=self.load_video)
        self.video_button.grid(row=0, column=2, padx=5, pady=5)

        self.model_label = tk.Label(root, text="UVR model:")
        self.model_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.model_combo = ttk.Combobox(
            root, values=[label for _, label in kc.UVR_MODELS],
            state="readonly", width=47,
        )
        self.model_combo.set(kc.UVR_MODELS[0][1])
        self.model_combo.grid(row=1, column=1, padx=5, pady=5)

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

        model = kc.UVR_MODELS[self.model_combo.current()][0]
        tool = kc.find_audio_separator()
        if not tool:
            messagebox.showerror("UVR not found", kc.audio_separator_missing_message())
            return
        backend_name = f"UVR ({model})"

        output_file = kc.karaoke_output_path(video_file, spaced=False)

        def work():
            return kc.separate_and_mix(
                ffmpeg, video_file, output_file,
                model=model, audio_separator=tool,
            )

        def done(ok, message):
            self.progress.stop()
            if ok:
                messagebox.showinfo("Success", f"Media mixed successfully!\nOutput: {output_file}")
            else:
                messagebox.showerror("Error", f"Mixing failed.\n{message}")

        self.progress.start(20)
        self.job.start(
            f"Working... extracting audio, separating instrumental with {backend_name}, "
            "then mixing. This takes a few minutes -- please wait.",
            work, done,
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = FFmpegMixerApp(root)
    root.mainloop()

# Created by Charlih Chen on 28AUG2024
# https://github.com/charlihchen
