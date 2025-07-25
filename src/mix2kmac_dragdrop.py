import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import shlex  # For parsing dropped file paths

from tkinterdnd2 import TkinterDnD, DND_FILES  # <-- Key import

class FFmpegMixerApp:
    """
    A Tkinter application to mix video and audio files using FFmpeg.
    Supports drag-and-drop for input files and paste functionality.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("FFmpeg.exe Video and Audio Mixer to become Karaoke Song")
        self.root.grid_columnconfigure(1, weight=1)

        # --- Video file input section ---
        self.video_label = tk.Label(root, text="Load Video(歌影) File (MP4/MKV/MPG/AVI):")
        self.video_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.video_entry = tk.Entry(root, width=50)
        self.video_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        # Drag-and-drop support:
        self.video_entry.drop_target_register(DND_FILES)
        self.video_entry.dnd_bind('<<Drop>>', self.handle_video_drop)
        # Paste support
        self.video_entry.bind("<Control-v>", self.paste_video_path)
        self.video_entry.bind("<Command-v>", self.paste_video_path) # For macOS

        self.video_button = tk.Button(root, text="Browse(載入)", command=self.load_video)
        self.video_button.grid(row=0, column=2, padx=5, pady=5)

        # --- Audio file input section ---
        self.audio_label = tk.Label(root, text="Load Instrumental Audio(伴奏) File (MP3/m4a):")
        self.audio_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.audio_entry = tk.Entry(root, width=50)
        self.audio_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        # Drag-and-drop support:
        self.audio_entry.drop_target_register(DND_FILES)
        self.audio_entry.dnd_bind('<<Drop>>', self.handle_audio_drop)
        # Paste support
        self.audio_entry.bind("<Control-v>", self.paste_audio_path)
        self.audio_entry.bind("<Command-v>", self.paste_audio_path) # For macOS

        self.audio_button = tk.Button(root, text="Browse(載入)", command=self.load_audio)
        self.audio_button.grid(row=1, column=2, padx=5, pady=5)

        # --- Mix button ---
        self.mix_button = tk.Button(root, text="Click here to Mix", command=self.mix_media)
        self.mix_button.grid(row=2, column=0, columnspan=3, pady=10)

    def load_video(self):
        """Opens a file dialog to select a video file and populates the video entry."""
        video_filename = filedialog.askopenfilename(
            filetypes=[("Video Files(歌影檔案)", "*.mp4;*.mkv;*.avi;*.mpg")]
        )
        if video_filename:
            self.video_entry.delete(0, tk.END)
            self.video_entry.insert(0, video_filename)

    def load_audio(self):
        """Opens a file dialog to select an audio file and populates the audio entry."""
        audio_filename = filedialog.askopenfilename(
            filetypes=[("Audio Files(伴奏檔案)", "*.mp3;*.m4a")]
        )
        if audio_filename:
            self.audio_entry.delete(0, tk.END)
            self.audio_entry.insert(0, audio_filename)

    def handle_drop(self, event, entry_widget):
        """
        Handles file drop events for entry widgets.
        Parses the dropped data to extract the file path and inserts it into the entry.
        """
        try:
            paths = shlex.split(event.data)
            if not paths:
                return
            file_path = paths[0]
            if file_path.startswith('{') and file_path.endswith('}'):
                file_path = file_path[1:-1]
            if os.path.isfile(file_path):
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, file_path)
            else:
                messagebox.showwarning("Invalid Drop", "Please drop a valid file.")
        except Exception as e:
            messagebox.showerror("Drop Error", f"Could not process dropped item: {e}")

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
        video_file = self.video_entry.get()
        audio_file = self.audio_entry.get()
        if not video_file or not audio_file:
            messagebox.showerror("Error", "Please provide both a video file and an audio file.")
            return

        base_name = os.path.splitext(os.path.basename(video_file))[0]
        output_file = f"{base_name}(DIY KTV).mkv"

        ffmpeg_executable = 'ffmpeg'
        script_dir = os.path.dirname(os.path.abspath(__file__))
        local_ffmpeg_path = os.path.join(script_dir, ffmpeg_executable)
        if os.path.exists(local_ffmpeg_path):
            ffmpeg_executable = local_ffmpeg_path
        elif os.name == 'nt' and os.path.exists(local_ffmpeg_path + '.exe'):
            ffmpeg_executable = local_ffmpeg_path + '.exe'

        command = [
            ffmpeg_executable,
            '-i', video_file,
            '-i', audio_file,
            '-map', '0:v',
            '-filter_complex', '[1:a][0:a]amerge=inputs=2,pan=stereo|c0<c0+c1|c1<c2+c3[a]',
            '-map', '[a]',
            output_file
        ]

        try:
            creationflags = 0
            if os.name == 'nt':
                creationflags = subprocess.CREATE_NO_WINDOW
            subprocess.run(command, check=True, creationflags=creationflags)
            messagebox.showinfo("Success", f"Media mixed successfully!\nOutput file: {output_file}")
        except FileNotFoundError:
            messagebox.showerror("Error", "FFmpeg not found. Please ensure 'ffmpeg' (or 'ffmpeg.exe' on Windows) is in the same directory as the script or in your system's PATH.")
        except subprocess.CalledProcessError as e:
            error_output = e.stderr.decode(errors='ignore') if e.stderr else "No specific error output from FFmpeg."
            messagebox.showerror("Error", f"An error occurred during FFmpeg execution:\n{error_output}\nCommand: {' '.join(command)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    root = TkinterDnD.Tk()  # Use TkinterDnD for drag-and-drop support
    app = FFmpegMixerApp(root)
    root.mainloop()
