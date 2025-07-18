import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

def resource_path(relative_path):
    """
    Get absolute path to resource, works for development and for Py2app bundled app.
    In a Py2app bundle, resources are typically found in the Contents/Resources directory,
    which sys._MEIPASS (or sys.frozen if using pyinstaller) points to.
    """
    try:
        # Py2app: resources are in sys._MEIPASS or sys.frozen.
        # sys._MEIPASS is more common for pyinstaller, but py2app uses a similar concept.
        # For py2app, resources are usually directly accessible relative to the executable
        # or within the Contents/Resources directory.
        # A common pattern for py2app is to put data files relative to the script.
        # Let's assume 'ffmpeg' will be placed directly next to the app executable
        # or in Contents/Resources.
        if hasattr(sys, 'frozen') and sys.frozen: # Check if running as a frozen app (py2app)
            # In a py2app bundle, the executable is in Contents/MacOS/
            # Resources are in Contents/Resources/
            # We need to go up two directories from the executable to the .app root,
            # then down into Contents/Resources.
            # A simpler approach is to rely on py2app's data_files mechanism,
            # which places files relative to the app's Contents/Resources directory.
            # The resource_path should then be relative to that.
            # For simplicity, we'll assume 'ffmpeg' is placed directly in Contents/Resources
            # and access it relative to the app's main script location.
            # The actual path will be handled by how py2app bundles it.
            # For py2app, a common pattern is:
            # base_path = os.path.join(os.path.dirname(sys.executable), '..', 'Resources')
            # However, the simpler `os.path.abspath(".")` often works if data_files
            # are configured correctly to put resources at the app's root or Resources.
            # Let's stick to the original logic which is generally robust for both.
            base_path = os.path.abspath(os.path.dirname(sys.executable))
            # If ffmpeg is placed directly in Contents/Resources, and the executable is in Contents/MacOS,
            # we need to go up one level (to MacOS), then up again (to Contents), then into Resources.
            # So, '../../Resources/ffmpeg' relative to the executable.
            # Or, if `sys.frozen` is true, py2app might set the working directory to Resources.
            # The original `sys._MEIPASS` is more for PyInstaller.
            # For py2app, it's often more direct:
            # os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
            # when running from the bundle, __file__ points to the bundled script.
            # Let's use a more direct approach for py2app that places it in Contents/Resources.
            # The `setup.py` will define where `ffmpeg` goes.
            # If `ffmpeg` is placed in `Contents/Resources`, and our script is in `Contents/MacOS`,
            # we need to go up two levels to the .app root, then into `Contents/Resources`.
            # A more reliable way for py2app is to use `pkg_resources` or `importlib.resources`
            # but for simple file access, direct path manipulation based on `sys.executable`
            # or `__file__` (which points to the bundled script) is common.
            # Given the `ffmpeg` binary will be a data file, it's often placed in `Contents/Resources`.
            # The `resource_path` function as written will work if the current working directory
            # is set to `Contents/Resources` by py2app, or if `ffmpeg` is placed directly
            # in the same directory as the main script within `Contents/MacOS` (less common for binaries).
            # The safest is to explicitly point to Contents/Resources.
            return os.path.join(os.path.dirname(sys.executable), '..', 'Resources', relative_path)
        else:
            # Development environment: use current directory
            base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)
    except Exception:
        # Fallback for unexpected scenarios, use current directory
        base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)


class FFmpegMixerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FFmpeg Video and Audio Mixer to become Karaoke Song")

        # Video file input
        self.video_label = tk.Label(root, text="Load Video(歌影) File (MP4/MKV/MPG/AVI):")
        self.video_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.video_entry = tk.Entry(root, width=50)
        self.video_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.video_button = tk.Button(root, text="Browse(載入)", command=self.load_video)
        self.video_button.grid(row=0, column=2, padx=5, pady=5)

        # Audio file input
        self.audio_label = tk.Label(root, text="Load Instrumental Audio(伴奏) File (MP3/m4a):")
        self.audio_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.audio_entry = tk.Entry(root, width=50)
        self.audio_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.audio_button = tk.Button(root, text="Browse(載入)", command=self.load_audio)
        self.audio_button.grid(row=1, column=2, padx=5, pady=5)

        # Configure grid column weights for responsiveness
        root.grid_columnconfigure(1, weight=1)

        # Mix button
        self.mix_button = tk.Button(root, text="Click here to Mix", command=self.mix_media)
        self.mix_button.grid(row=3, column=0, columnspan=3, pady=10)

    def load_video(self):
        video_filename = filedialog.askopenfilename(filetypes=[("Video Files(歌影檔案)", "*.mp4;*.mkv;*.mpg;*.avi")])
        if video_filename:
            self.video_entry.delete(0, tk.END)
            self.video_entry.insert(0, video_filename)

    def load_audio(self):
        audio_filename = filedialog.askopenfilename(filetypes=[("Audio Files(伴奏檔案)", "*.mp3;*.m4a")])
        if audio_filename:
            self.audio_entry.delete(0, tk.END)
            self.audio_entry.insert(0, audio_filename)

    def mix_media(self):
        video_file = self.video_entry.get()
        audio_file = self.audio_entry.get()

        if not video_file or not audio_file:
            messagebox.showerror("Error", "Please provide a video file and audio file.")
            return

        # Derive output file name from video file name
        base_name = os.path.splitext(os.path.basename(video_file))[0]
        # Suggest saving the output in the same directory as the video file
        output_file = os.path.join(os.path.dirname(video_file), f"{base_name} (DIY KTV).mkv")

        # Locate FFmpeg binary
        ffmpeg_path = resource_path("ffmpeg") # This will now look in Contents/Resources/ffmpeg
        
        # Ensure FFmpeg binary exists and is executable
        if not os.path.exists(ffmpeg_path):
            messagebox.showerror("Error", f"FFmpeg binary not found at: {ffmpeg_path}. Please ensure it's bundled correctly.")
            return

        # Make sure FFmpeg is executable
        try:
            os.chmod(ffmpeg_path, 0o755) # Give read, write, execute permissions for owner, read+execute for group/others
        except OSError as e:
            messagebox.showerror("Error", f"Failed to set FFmpeg executable permissions: {e}")
            return

        command = [
            ffmpeg_path,
            '-i', video_file,
            '-i', audio_file,
            '-map', '0:v', # Map video stream from first input
            # Mix audio: [1:a] is audio from second input (instrumental), [0:a] is audio from first input (original video)
            # amerge=inputs=2 merges them.
            # pan=stereo|c0<c0+c1|c1<c2+c3 mixes channels for stereo output.
            # This assumes original audio is stereo (c0,c1) and instrumental is stereo (c2,c3).
            # If instrumental is mono, you might need a different pan filter.
            # For simple mixing, `amerge` is often sufficient.
            '-filter_complex', '[1:a][0:a]amerge=inputs=2[a]', # Simpler merge, handles mono/stereo better
            '-map', '[a]', # Map the merged audio stream
            '-c:v', 'copy',  # Copy video stream to avoid re-encoding
            '-c:a', 'aac',   # Encode audio to AAC for compatibility
            '-b:a', '192k',  # Set audio bitrate for quality
            '-shortest',     # End encoding when the shortest input stream ends
            output_file
        ]

        try:
            # Use subprocess.run for Python 3.5+ for simpler error handling
            # capture_output=True captures stdout and stderr
            process = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
            messagebox.showinfo("Success", f"Media mixed successfully! Output saved as:\n{output_file}\n\nFFmpeg Output:\n{process.stdout}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"An error occurred during FFmpeg processing:\n\nCommand: {' '.join(e.cmd)}\n\nReturn Code: {e.returncode}\n\nSTDOUT:\n{e.stdout}\n\nSTDERR:\n{e.stderr}")
        except FileNotFoundError:
            messagebox.showerror("Error", "FFmpeg binary not found. Please ensure it is included in the application bundle and is executable.")
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {e}")

def main():
    root = tk.Tk()
    app = FFmpegMixerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
