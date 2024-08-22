import os  
import subprocess  
import tkinter as tk  
from tkinter import messagebox  

class FFmpegDL4m3u8App:  
    def __init__(self, root):  
        self.root = root  
        self.root.title("FFmpeg.exe to download video from https://URL/m3u8")  

        # Input the URL by copy and paste   
        self.URL_label = tk.Label(root, text="Input (the https://URL/m3u8)): ")  
        self.URL_label.grid(row=0, column=0)        
        
        self.URL_entry = tk.Entry(root, width=50)  
        self.URL_entry.grid(row=0, column=1)        

        # Button to trigger the download  
        self.download_button = tk.Button(root, text="Download", command=self.download_URL)  
        self.download_button.grid(row=1, columnspan=2)  # Corrected columnspan to 2 to center the button under the input  

    def download_URL(self):  
        URL = self.URL_entry.get()      
        
        if not URL:  
            messagebox.showerror("Error", "Please provide a URL.")  
            return  

        # Derive output file name from the URL or use a default name  
        base_name = "downloaded_video"  
        output_file = f"{base_name}(Downloaded_下載).mp4"  

        # Prepare the command for ffmpeg  
        command = [  
            'ffmpeg',  
            '-i', URL,   
            '-c', 'copy',  
            '-bsf:a', 'aac_adtstoasc',  
            output_file  
        ]  

        try:  
            subprocess.run(command, check=True)  
            messagebox.showinfo("Success", "Download successfully!")  
        except subprocess.CalledProcessError as e:  
            messagebox.showerror("Error", f"An error occurred: {str(e)}")  

if __name__ == "__main__":  
    root = tk.Tk()  
    app = FFmpegDL4m3u8App(root)  
    root.mainloop()
#Note:
#Copy ffmpeg.exe and all its .dll in the same folder of the DL4m3u8.exe
