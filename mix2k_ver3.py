import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD

class FFmpegMixerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FFmpeg.exe commands to mix Video and Audio into a Karaoke Song")

        # Video file input
        self.video_label = tk.Label(root, text="Drag and drop video file(拖放歌影檔)(MP4/MKV/MPG/AVI):")
        self.video_label.grid(row=0, column=0)

        self.video_entry = tk.Entry(root, width=50, state="readonly")
        self.video_entry.grid(row=0, column=1)

        self.video_entry.drop_target_register(DND_FILES)
        self.video_entry.dnd_bind('<<Drop>>', self.load_video)

        # Audio file input
        self.audio_label = tk.Label(root, text="Drag and drop audio file(拖放伴奏檔)(MP3/m4a):")
        self.audio_label.grid(row=1, column=0)

        self.audio_entry = tk.Entry(root, width=50, state="readonly")
        self.audio_entry.grid(row=1, column=1)

        self.audio_entry.drop_target_register(DND_FILES)
        self.audio_entry.dnd_bind('<<Drop>>', self.load_audio)

        # Mix button
        self.mix_button = tk.Button(root, text="Click here to Mix(點這裡就開始混合成K檔)", command=self.mix_media)
        self.mix_button.grid(row=3, column=0)

    def load_video(self, event):
        video_filename = event.data
        self.video_entry.delete(0, tk.END)
        self.video_entry.insert(0, video_filename)

    def load_audio(self, event):
        audio_filename = event.data
        self.audio_entry.delete(0, tk.END)
        self.audio_entry.insert(0, audio_filename)

    def mix_media(self):
        video_file = self.video_entry.get()
        audio_file = self.audio_entry.get()

        if not video_file or not audio_file:
            messagebox.showerror("Error", "Please provide a video(歌影) file and audio(伴奏) file.")
            return

        # Derive output file name from video file name
        base_name = os.path.splitext(os.path.basename(video_file))[0]
        output_file = f"{base_name}(DIY KTV).mkv"

        command = [
            'ffmpeg',
            '-i', video_file,
            '-i', audio_file,
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
    root = TkinterDnD.Tk()
    app = FFmpegMixerApp(root)
    root.mainloop()


#Note:
#Copy ffmpeg.exe and all its .dll in the same folder of the mix2k.exe
#Of couse, the Video file and audio file that will mix into as Karaoke song file may need to be the same folder