import tkinter as tk
from tkinter import ttk, messagebox
import vlc
import re
import yt_dlp
import time
import os
import urllib.parse
import requests
import webbrowser

class VideoPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Advertisement Player")
        
        # Configure the main window
        self.root.geometry("800x600")
        
        # Create main container frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create frame for video
        self.video_frame = ttk.Frame(self.main_frame)
        self.video_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create URL link label
        self.url_label = ttk.Label(
            self.main_frame,
            text="Click here to visit website",
            cursor="hand2",
            foreground="blue"
        )
        self.url_label.pack(pady=5)
        self.url_label.bind('<Button-1>', self.on_url_click)
        
        # Create frame for controls
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create buttons
        self.prev_button = ttk.Button(self.control_frame, text="Previous", command=self.previous_video)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        self.play_pause_button = ttk.Button(self.control_frame, text="Play", command=self.toggle_play_pause)
        self.play_pause_button.pack(side=tk.LEFT, padx=5)
        
        self.next_button = ttk.Button(self.control_frame, text="Next", command=self.next_video)
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(self.control_frame, text="")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        try:
            # Check if VLC is installed
            if not self.check_vlc_installed():
                messagebox.showerror("Error", "VLC media player is not installed. Please install VLC first.")
                root.destroy()
                return
                
            # Initialize VLC instance
            self.instance = vlc.Instance()
            self.player = self.instance.media_player_new()
            print("VLC instance created successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize VLC: {str(e)}")
            print(f"VLC initialization error: {str(e)}")
            root.destroy()
            return
        
        # Initialize yt-dlp
        self.ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True
        }
        
        # List to store video URLs and their associated click URLs
        self.video_urls = []
        self.click_urls = {}  # Dictionary to store click URLs for each video
        self.current_video_index = 0
        self.is_playing = False
        
    def check_vlc_installed(self):
        """Check if VLC is installed"""
        if os.name == 'nt':  # Windows
            return os.path.exists("C:\\Program Files\\VideoLAN\\VLC\\vlc.exe") or \
                   os.path.exists("C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe")
        else:  # Linux/Mac
            return os.path.exists("/usr/bin/vlc") or os.path.exists("/usr/local/bin/vlc")
    
    def on_url_click(self, event=None):
        """Handle click event on URL label"""
        if self.video_urls and self.current_video_index < len(self.video_urls):
            current_video = self.video_urls[self.current_video_index]
            if current_video in self.click_urls:
                url = self.click_urls[current_video]
                print(f"Opening URL in browser: {url}")
                webbrowser.open_new_tab(url)
                self.status_label.config(text=f"Opening {url}")
    
    def check_drive_permissions(self, file_id):
        """Check if the Google Drive file is accessible"""
        url = f"https://drive.google.com/uc?id={file_id}"
        response = requests.head(url, allow_redirects=True)
        return response.status_code == 200
        
    def convert_drive_link(self, drive_link):
        """Convert Google Drive link to direct playable link"""
        try:
            file_id = re.findall(r'\/d\/(.*?)\/|\/d\/(.*?)$', drive_link)
            if file_id:
                file_id = [i for i in file_id[0] if i][0]
                
                # Check if file is accessible
                if not self.check_drive_permissions(file_id):
                    raise Exception(
                        "Video is not accessible. Please make sure:\n"
                        "1. The video file exists\n"
                        "2. The link sharing is set to 'Anyone with the link'\n"
                        "3. You have copied the correct link"
                    )
                
                direct_link = f'https://drive.google.com/uc?id={file_id}'
                print(f"Converted drive link: {direct_link}")
                return direct_link
            return drive_link
        except Exception as e:
            print(f"Error converting drive link: {str(e)}")
            raise
    
    def get_video_url(self, url):
        """Get direct video URL using yt-dlp"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'url' not in info:
                    raise Exception("Could not extract video URL. Please check if the video is accessible.")
                return info['url']
        except Exception as e:
            print(f"Error extracting video URL: {str(e)}")
            raise
    
    def load_video(self, url):
        """Load video from URL"""
        try:
            print(f"\nAttempting to load video from URL: {url}")
            self.status_label.config(text="Loading video...")
            
            converted_url = self.convert_drive_link(url)
            print(f"Using converted URL: {converted_url}")
            
            direct_url = self.get_video_url(converted_url)
            if not direct_url:
                raise Exception("Could not get direct video URL")
            
            print(f"Direct URL obtained successfully")
            
            media = self.instance.media_new(direct_url)
            print("Media object created successfully")
            
            self.player.set_media(media)
            print("Media set to player successfully")
            
            # Get the handle of the video frame
            if self.root.winfo_exists():
                handle = self.video_frame.winfo_id()
                print(f"Video frame handle: {handle}")
                self.player.set_hwnd(handle)
                self.player.play()
                self.is_playing = True
                self.play_pause_button.config(text="Pause")
                self.status_label.config(text="Playing")
                print("Video playback started")
                
                # Update URL label with current URL
                if url in self.click_urls:
                    self.url_label.config(text=f"Click here to visit: {self.click_urls[url]}")
            else:
                print("Root window no longer exists")
                
        except Exception as e:
            error_msg = f"Error loading video: {str(e)}"
            print(error_msg)
            messagebox.showerror("Error", error_msg)
            self.status_label.config(text="Error loading video")
    
    def toggle_play_pause(self):
        """Toggle between play and pause"""
        if self.is_playing:
            self.player.pause()
            self.play_pause_button.config(text="Play")
            self.status_label.config(text="Paused")
        else:
            self.player.play()
            self.play_pause_button.config(text="Pause")
            self.status_label.config(text="Playing")
        self.is_playing = not self.is_playing
    
    def previous_video(self):
        """Play previous video in the playlist"""
        if self.video_urls:
            self.current_video_index = (self.current_video_index - 1) % len(self.video_urls)
            self.load_video(self.video_urls[self.current_video_index])
    
    def next_video(self):
        """Play next video in the playlist"""
        if self.video_urls:
            self.current_video_index = (self.current_video_index + 1) % len(self.video_urls)
            self.load_video(self.video_urls[self.current_video_index])
    
    def add_video(self, url, click_url):
        """Add video to playlist with associated click URL"""
        self.video_urls.append(url)
        self.click_urls[url] = click_url
        if len(self.video_urls) == 1:  # If this is the first video, play it
            self.load_video(url)

def main():
    root = tk.Tk()
    player = VideoPlayer(root)
    
    # Add your Google Drive video links and their associated click URLs
    videos_with_links = [
        {
            "video": "https://drive.google.com/file/d/1EurMx3f3RZGvpFIooFKbVWqQI82UB50d/view?usp=drive_link",
            "click_url": "http://msn.com"
        },
    ]
    
    for video in videos_with_links:
        player.add_video(video["video"], video["click_url"])
    
    root.mainloop()

if __name__ == "__main__":
    main() 