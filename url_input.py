import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import json
import os

class URLInputGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video URL Input")
        self.root.geometry("600x400")
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # List to store video entries
        self.video_entries = []
        
        # Create scrollable frame
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Add initial video entry
        self.add_video_entry()
        
        # Buttons frame
        self.button_frame = ttk.Frame(self.root, padding="10")
        self.button_frame.pack(fill=tk.X)
        
        # Add buttons
        ttk.Button(self.button_frame, text="Add Another Video", command=self.add_video_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Start Video Player", command=self.start_video_player).pack(side=tk.RIGHT, padx=5)
    
    def add_video_entry(self):
        """Add a new video entry form"""
        # Create frame for this entry
        entry_frame = ttk.LabelFrame(self.scrollable_frame, text=f"Video {len(self.video_entries) + 1}", padding="10")
        entry_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Video URL
        ttk.Label(entry_frame, text="Google Drive Video URL:").pack(fill=tk.X)
        video_url = ttk.Entry(entry_frame, width=50)
        video_url.pack(fill=tk.X, pady=2)
        
        # Website URL
        ttk.Label(entry_frame, text="Website URL (when clicked):").pack(fill=tk.X)
        website_url = ttk.Entry(entry_frame, width=50)
        website_url.pack(fill=tk.X, pady=2)
        
        # Remove button
        def remove_entry():
            entry_frame.destroy()
            self.video_entries.remove((video_url, website_url))
            # Update the numbering of remaining entries
            for i, entry in enumerate(self.scrollable_frame.winfo_children()):
                entry.configure(text=f"Video {i + 1}")
        
        if len(self.video_entries) > 0:  # Only show remove button if there's more than one entry
            ttk.Button(entry_frame, text="Remove", command=remove_entry).pack(pady=5)
        
        # Add to list of entries
        self.video_entries.append((video_url, website_url))
        
        # Update canvas scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def validate_urls(self):
        """Validate that all URLs are filled in"""
        for video_url, website_url in self.video_entries:
            if not video_url.get() or not website_url.get():
                messagebox.showerror("Error", "Please fill in all URL fields")
                return False
            if not video_url.get().startswith("https://drive.google.com/"):
                messagebox.showerror("Error", "Please enter valid Google Drive URLs")
                return False
            if not website_url.get().startswith("http"):
                messagebox.showerror("Error", "Please enter valid website URLs (starting with http:// or https://)")
                return False
        return True
    
    def start_video_player(self):
        """Start the video player with the entered URLs"""
        if not self.validate_urls():
            return
        
        # Create the video links list
        videos_with_links = [
            {
                "video": video_url.get(),
                "click_url": website_url.get()
            }
            for video_url, website_url in self.video_entries
        ]
        
        # Save the URLs to a temporary file
        with open("video_urls.json", "w") as f:
            json.dump(videos_with_links, f)
        
        # Update the video_player.py file with the new URLs
        self.update_video_player()
        
        # Start the video player
        subprocess.Popen(["python", "video_player.py"])
        
        # Close the URL input window
        self.root.destroy()
    
    def update_video_player(self):
        """Update the video_player.py file with the new URLs"""
        with open("video_urls.json", "r") as f:
            videos_with_links = json.load(f)
        
        with open("video_player.py", "r") as f:
            lines = f.readlines()
        
        # Find the videos_with_links list in the code and replace it
        start_index = -1
        end_index = -1
        for i, line in enumerate(lines):
            if "videos_with_links = [" in line:
                start_index = i
            elif start_index != -1 and "]" in line and end_index == -1:
                end_index = i + 1
                break
        
        if start_index != -1 and end_index != -1:
            # Create the new videos_with_links code
            new_lines = ["    videos_with_links = [\n"]
            for video in videos_with_links:
                new_lines.extend([
                    "        {\n",
                    f'            "video": "{video["video"]}",\n',
                    f'            "click_url": "{video["click_url"]}"\n',
                    "        },\n"
                ])
            new_lines.append("    ]\n")
            
            # Replace the old lines with the new ones
            lines[start_index:end_index] = new_lines
            
            # Write the updated code back to the file
            with open("video_player.py", "w") as f:
                f.writelines(lines)

def main():
    root = tk.Tk()
    app = URLInputGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 