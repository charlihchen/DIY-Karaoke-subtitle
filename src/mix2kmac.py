# Usage: $python mnix2kmac.py
#
# $dist/Mix2kmac.app/Contents/MacOS/Mix2kmac
#
import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

class FFmpegMixerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Load Video and Audio to Mix into Karaoke Song (macOS/FFmpeg)")

        # Video file input
        self.video_label = tk.Label(root, text="Load Video(歌影) File (MP4/MKV/MPG/AVI):")
        self.video_label.grid(row=0, column=0, padx=5, pady=5)

        self.video_entry = tk.Entry(root, width=50)
        self.video_entry.grid(row=0, column=1, padx=5, pady=5)

        self.video_button = tk.Button(root, text="Browse(載入)", command=self.load_video)
        self.video_button.grid(row=0, column=2, padx=5, pady=5)

        # Audio file input
        self.audio_label = tk.Label(root, text="Load Instrumental Audio(伴奏) File (MP3/M4A):")
        self.audio_label.grid(row=1, column=0, padx=5, pady=5)

        self.audio_entry = tk.Entry(root, width=50)
        self.audio_entry.grid(row=1, column=1, padx=5, pady=5)

        self.audio_button = tk.Button(root, text="Browse(載入)", command=self.load_audio)
        self.audio_button.grid(row=1, column=2, padx=5, pady=5)

        # Mix button
        self.mix_button = tk.Button(root, text="Click here to Mix", command=self.mix_media)
        self.mix_button.grid(row=2, column=1, padx=5, pady=15)

    def load_video(self):
        video_filename = filedialog.askopenfilename(
            title="Select a Video File",
            filetypes=[
                ("MP4 Files", "*.mp4"),
                ("MKV Files", "*.mkv"),
                ("AVI Files", "*.avi"),
                ("All Video Files", "*.mp4 *.mkv *.avi")
            ]
        )
        if video_filename:
            self.video_entry.delete(0, tk.END)
            self.video_entry.insert(0, video_filename)

    def load_audio(self):
        audio_filename = filedialog.askopenfilename(
            title="Select an Audio File",
            filetypes=[
                ("MP3 Files", "*.mp3"),
                ("M4A Files", "*.m4a"),
                ("All Audio Files", "*.mp3 *.m4a")
            ]
        )
        if audio_filename:
            self.audio_entry.delete(0, tk.END)
            self.audio_entry.insert(0, audio_filename)

    def mix_media(self):
        video_file = self.video_entry.get()
        audio_file = self.audio_entry.get()

        if not video_file or not audio_file:
            messagebox.showerror("Error", "Please provide both a video file and an audio file.")
            return

        base_name = os.path.splitext(os.path.basename(video_file))[0]
        output_file = f"{base_name} (DIY KTV).mkv"

        command = [
            'ffmpeg',
            '-i', video_file,
            '-i', audio_file,
            '-map', '0:v',
            '-filter_complex', '[1:a][0:a]amerge=inputs=2,pan=stereo|c0<c0+c1|c1<c2+c3[a]',
            '-map', '[a]',
            '-ac', '2',  # ensure stereo output
            output_file
        ]

        try:
            subprocess.run(command, check=True)
            messagebox.showinfo("Success", f"Media mixed successfully!\nOutput: {output_file}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"An error occurred during mixing:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FFmpegMixerApp(root)
    root.mainloop()
