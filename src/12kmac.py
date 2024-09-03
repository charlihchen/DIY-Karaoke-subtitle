import os  
import subprocess  
import shutil  
import tkinter as tk  
from tkinter import filedialog, messagebox  

class FFmpegMixerApp:  
    def __init__(self, root):  
        self.root = root  
        self.root.title("Load Video & extract NoVocal.mp3 by Demucs, mix it and Video to Karaoke Song by FFmpeg")  

        # Video file input  
        self.video_label = tk.Label(root, text="Load Video File (MP4/MKV/MPG/AVI):")  
        self.video_label.grid(row=0, column=0)  

        self.video_entry = tk.Entry(root, width=50)  
        self.video_entry.grid(row=0, column=1)  

        self.video_button = tk.Button(root, text="Browse", command=self.load_video)  
        self.video_button.grid(row=0, column=2)  

        # Mix button  
        self.mix_button = tk.Button(root, text="Click here to Mix", command=self.mix_media)  
        self.mix_button.grid(row=3, column=0)  

    def load_video(self):  
        video_filename = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.mkv;*.avi")])  
        if video_filename:  
            self.video_entry.delete(0, tk.END)  
            self.video_entry.insert(0, video_filename)  

    def mix_media(self):  
        video_file = self.video_entry.get()  

        if not video_file:  
            messagebox.showerror("Error", "Please provide a video file.")  
            return  

        def safe_remove(path):  
            try:  
                if os.path.isfile(path):  
                    os.remove(path)  
                elif os.path.isdir(path):  
                    shutil.rmtree(path)  
            except Exception as e:  
                print(f"Warning: Unable to delete {path}: {str(e)}")  
        
        # Derive output file name from video file name  
        base_name = os.path.splitext(os.path.basename(video_file))[0]  
        output_file = f"{base_name}(DIY KTV).mkv"  

        # Convert video_file into .wav for Demucs  
        command = [  
            'ffmpeg',  
            '-y', # overwrite output file if exists  
            '-i', video_file,  
            f"{base_name}.wav"  
        ]  

        try:  
            subprocess.run(command, check=True)  
        except subprocess.CalledProcessError as e:  
            messagebox.showerror("Error", f"An error occurred during FFmpeg conversion: {str(e)}")  
            return  

        # Ensure the path to Demucs is in the PATH environment variable  
        # Update path accordingly if Demucs is not in PATH  
        demucs_path = "/usr/local/bin"  # Adjust if needed based on your setup  
        os.environ["PATH"] += os.pathsep + demucs_path  

        # Use Demucs to extract instrumental audio  
        demucs_output_dir = os.path.join(os.path.dirname(f"{base_name}.wav"), "demucs_output")  
        os.makedirs(demucs_output_dir, exist_ok=True)  

        try:  
            # Call the Demucs command with full path if necessary  
            subprocess.run(["demucs", "--two-stems=vocals", "-o", demucs_output_dir, "--mp3", f"{base_name}.wav"], check=True)  
        except FileNotFoundError:  
            messagebox.showerror("Error", "Demucs executable not found. Please ensure it is installed and in your PATH.")  
            return  
        except subprocess.CalledProcessError as e:  
            messagebox.showerror("Error", f"Demucs failed: {str(e)}")  
            return  

        # Find the extracted instrumental audio file  
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
            messagebox.showerror("Error", f"An error occurred during mixing: {str(e)}")  

        # Clean up temporary files  
        safe_remove(demucs_output_dir)  
        wav_file = f"{base_name}.wav"  
        if os.path.exists(wav_file):  
            os.remove(wav_file)  
            print(f"Temporary File '{wav_file}' and Folder '{demucs_output_dir}' deleted successfully.")  
        else:  
            print("The file does not exist")  
            
if __name__ == "__main__":  
    root = tk.Tk()  
    app = FFmpegMixerApp(root)  
    root.mainloop()  

# Make sure Demucs is installed. You can install it using pip as follows:  
# pip install demucs
# Created by Charlih Chen on 28AUG2024
# https://github.com/charlihchen