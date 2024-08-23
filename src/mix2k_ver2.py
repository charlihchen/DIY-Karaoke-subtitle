import os  
import subprocess  
import tkinter as tk  
from tkinter import filedialog, messagebox  
from tkinterdnd2 import DND_FILES, TkinterDnD  

class FFmpegMixerApp:  
    def __init__(self, root):  
        self.root = root  
        self.root.title("FFmpeg.exe Video and Audio Mixer to become Karaoke Song")  

        # Video file input  
        self.video_label = tk.Label(root, text="Load Video(歌影) File (MP4/MKV/MPG/AVI):")  
        self.video_label.grid(row=0, column=0)  

        self.video_entry = tk.Entry(root, width=50)  
        self.video_entry.grid(row=0, column=1)  
        self.video_entry.drop_target_register(DND_FILES)  
        self.video_entry.dnd_bind('<<Drop>>', self.on_drop_video)  

        self.video_button = tk.Button(root, text="Browse(載入)", command=self.load_video)  
        self.video_button.grid(row=0, column=2)  

        # Audio file input  
        self.audio_label = tk.Label(root, text="Load Instrumental Audio(伴奏) File (MP3/m4a):")  
        self.audio_label.grid(row=1, column=0)  

        self.audio_entry = tk.Entry(root, width=50)  
        self.audio_entry.grid(row=1, column=1)  
        self.audio_entry.drop_target_register(DND_FILES)  
        self.audio_entry.dnd_bind('<<Drop>>', self.on_drop_audio)  

        self.audio_button = tk.Button(root, text="Browse(載入)", command=self.load_audio)  
        self.audio_button.grid(row=1, column=2)  

        # Mix button  
        self.mix_button = tk.Button(root, text="Click here to Mix", command=self.mix_media)  
        self.mix_button.grid(row=3, column=0)  

    def load_video(self):  
        video_filename = filedialog.askopenfilename(filetypes=[("Video Files(歌影檔案)", "*.mp4;*.mkv;*.avi")])  
        if video_filename:  
            self.video_entry.delete(0, tk.END)  
            self.video_entry.insert(0, video_filename)  

    def load_audio(self):  
        audio_filename = filedialog.askopenfilename(filetypes=[("Audio Files(伴奏檔案)", "*.mp3;*.m4a")])  
        if audio_filename:  
            self.audio_entry.delete(0, tk.END)  
            self.audio_entry.insert(0, audio_filename)  

    def on_drop_video(self, event):  
        video_filename = event.data  
        if os.path.isfile(video_filename):  
            self.video_entry.delete(0, tk.END)  
            self.video_entry.insert(0, video_filename)  

    def on_drop_audio(self, event):  
        audio_filename = event.data  
        if os.path.isfile(audio_filename):  
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
        output_file = f"{base_name} (DIY KTV).mkv"  

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
    root = TkinterDnD.Tk()  # Changed from tk.Tk() to TkinterDnD.Tk()  
    app = FFmpegMixerApp(root)  
    root.mainloop()

#Note:
#Copy ffmpeg.exe and all its .dll in the same folder of the mix2k.exe
#Of couse, the Video file and audio file that will mix into as Karaoke song file may need to be the same folder
