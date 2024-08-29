import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

class FFmpegMixerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Load Video and use Demucs to extract NoVocal.mp3 and use FFmpeg.exe to mix the Video and the MP3 into Karaoke Song")

        # Video file input
        self.video_label = tk.Label(root, text="Load Video (歌影) File (MP4/MKV/MPG/AVI):")
        self.video_label.grid(row=0, column=0)

        self.video_entry = tk.Entry(root, width=50)
        self.video_entry.grid(row=0, column=1)

        self.video_button = tk.Button(root, text="Browse (載入)", command=self.load_video)
        self.video_button.grid(row=0, column=2)

        # Mix button
        self.mix_button = tk.Button(root, text="Click here to Mix", command=self.mix_media)
        self.mix_button.grid(row=3, column=0)

    def load_video(self):
        video_filename = filedialog.askopenfilename(filetypes=[("Video Files (歌影檔案)", "*.mp4;*.mkv;*.avi")])
        if video_filename:
            self.video_entry.delete(0, tk.END)
            self.video_entry.insert(0, video_filename)

    def mix_media(self):
        video_file = self.video_entry.get()

        if not video_file:
            messagebox.showerror("Error", "Please provide a video file.")
            return

        # Derive output file name from video file name
        base_name = os.path.splitext(os.path.basename(video_file))[0]
        output_file = f"{base_name}(DIY KTV).mkv"

        # Convert video_file into .wav for Demucs
        command = [
            'ffmpeg',
			'-y', #overwrite output file if exists
            '-i', video_file,
            f"{base_name}.wav"
        ]

        try:
            subprocess.run(command, check=True)
            #messagebox.showinfo("Success", "Media mixed successfully!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            return

        # Ensure the path to Demucs is in the PATH environment variable
        demucs_path = r"C:\Users\charl\anaconda3\Scripts"
        os.environ["PATH"] += os.pathsep + demucs_path

        # Use Demucs to extract instrumental audio
        demucs_output_dir = os.path.join(os.path.dirname(f"{base_name}.wav"), "demucs_output")
        os.makedirs(demucs_output_dir, exist_ok=True)

        try:
            subprocess.run(["demucs", "--two-stems=vocals", "-o", demucs_output_dir, "--mp3", f"{base_name}.wav"], check=True)
			#subprocess.run(["demucs", "-o", demucs_output_dir, "--device=cuda", "--mp3", f"{base_name}.wav"], check=True)
        except FileNotFoundError:
            messagebox.showerror("Error", "Demucs executable not found. Please ensure it is installed and in your PATH.")
            return
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Demucs failed: {str(e)}")
            return

        # Find the extracted instrumental audio file
        # 12k\demucs_output\htdemucs\VideoFileName\no_vocals.mp3
        instrumental_audio_file = os.path.join(demucs_output_dir, "htdemucs", base_name, "no_vocals.mp3")
		
        if not os.path.exists(instrumental_audio_file):
            messagebox.showerror("Error", "Instrumental audio file not found.")
            return

        command = [
            'ffmpeg',
            '-i', video_file,
            '-i', instrumental_audio_file,
            '-map', '0:v',
            '-filter_complex', '[1:a][0:a]amerge=inputs=2,pan=stereo|c0<c0+c1|c1<c2+c3[a]',
            '-map', '[a]',
            output_file
        ]

        try:
            subprocess.run(command, check=True)
            messagebox.showinfo("Success", "Media mixed successfully!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FFmpegMixerApp(root)
    root.mainloop()

#Created by Charlih Chen on 28AUG2024
#Here are some potential solutions:
#Check Demucs Installation:
#Ensure that Demucs is correctly installed on your system. If you haven’t installed it yet, follow the instructions from the Demucs GitHub repository.
#Specify the Full Path to Demucs:
#Instead of just using "demucs" as the command, provide the full path to the Demucs executable.
#demucs_path = r"C:\path\to\demucs.exe"
#subprocess.run([demucs_path, "-o", demucs_output_dir, "--device=cuda", video_file], check=True)