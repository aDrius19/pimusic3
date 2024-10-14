import os
import sqlite3
import pygame
from tkinter import Tk, Button, Label, Listbox, filedialog, messagebox, Scale, HORIZONTAL

# Initialize pygame mixer for playing audio
pygame.mixer.init()

# Database setup function
def init_db():
    conn = sqlite3.connect('music_library.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS songs 
                      (id INTEGER PRIMARY KEY, title TEXT, file_path TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS songs 
                          (song_id INTEGER, FOREIGN KEY (song_id) REFERENCES songs(id))''')
    conn.commit()
    conn.close()

# Add music to the database
def add_song_to_db(file_path):
    conn = sqlite3.connect('music_library.db')
    cursor = conn.cursor()
    title = os.path.basename(file_path)
    cursor.execute("INSERT INTO songs (title, file_path) VALUES (?, ?)", (title, file_path))
    conn.commit()
    conn.close()

# Fetch all songs from the database
def fetch_songs():
    conn = sqlite3.connect('music_library.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM songs")
    songs = cursor.fetchall()
    conn.close()
    return songs

def delete_song():
    curr_song=song_listbox.curselection()
    if curr_song:
        song_title = song_listbox.get(curr_song)
        conn = sqlite3.connect('music_library.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM songs WHERE title=?", (song_title,))
        song_listbox.delete(curr_song[0])
        song_id = cursor.fetchone()[0]
        cursor.execute("DELETE FROM songs  WHERE id = ?", (song_id,))
        stop_song()
        conn.commit()
        conn.close()
    else:
        messagebox.showwarning("Select song", "Please select a song to delete")
# Play the selected song
def play_song():
    selected_song = song_listbox.curselection()
    if selected_song:
        song_title = song_listbox.get(selected_song[0])  # Get the selected song's title
        conn = sqlite3.connect('music_library.db')
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM songs WHERE title=?", (song_title,))
        song_path = cursor.fetchone()[0]
        conn.close()
        if song_path:
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            status_label.config(text=f"Playing: {song_title}")
    else:
        messagebox.showwarning("Select song", "Please select a song to play")

# Pause song
def pause_song():
    pygame.mixer.music.pause()
    status_label.config(text="Paused")

# Resume song
def resume_song():
    pygame.mixer.music.unpause()
    status_label.config(text="Resumed")

def previous_song():
    curr_selec = song_listbox.curselection()
    if curr_selec:
        prev_one = curr_selec[0] -1
        if prev_one >=0:
            song_listbox.selection_clear(0, 'end')
            song_listbox.select_set(prev_one)
            play_song()
        else:
            messagebox.showwarning("No song", "No previous song exists!")

def set_volume(val):
    volume = float(val) / 100
    pygame.mixer.music.set_volume(volume)


def next_song():
    curr_selec = song_listbox.curselection()
    if curr_selec:
        next_one = curr_selec[0] + 1
        if next_one < song_listbox.size():
            song_listbox.selection_clear(0, 'end')
            song_listbox.select_set(next_one)
            play_song()
        else:
            messagebox.showwarning("No song", "No next song exists!")

#  top song
def stop_song():
    pygame.mixer.music.stop()
    status_label.config(text="Stopped")

# Add songs through file dialog
def add_song():
    file_path = filedialog.askopenfilename(title="Select a song", filetypes=(("MP3 Files", "*.mp3"),))
    if file_path:
        add_song_to_db(file_path)
        load_song_list()

# Load songs from the database into the Listbox
def load_song_list():
    song_listbox.delete(0, 'end')  # Clear the Listbox
    songs = fetch_songs()
    for song in songs:
        song_listbox.insert('end', song[1])  # Insert song title into the Listbox

# Initialize the GUI
def init_gui():
    global song_listbox, status_label

    root = Tk()
    root.title("PiMusic3")
    root.configure(bg='lightblue')

    # Song listbox
    song_listbox = Listbox(root, width=50, height=15, bg='lightgrey')
    song_listbox.grid(row=0, column=0, columnspan=4, pady=10)

    # Play, Pause, Resume, Stop buttons
    play_button = Button(root, text="Play", width=10, command=play_song, bg='lightgreen')
    play_button.grid(row=1, column=0, padx=5, pady=5)

    pause_button = Button(root, text="Pause", width=10, command=pause_song, bg='lightgreen')
    pause_button.grid(row=1, column=1, padx=5, pady=5)

    resume_button = Button(root, text="Resume", width=10, command=resume_song, bg='lightgreen')
    resume_button.grid(row=1, column=2, padx=5, pady=5)

    stop_button = Button(root, text="Stop", width=10, command=stop_song, bg='lightgreen')
    stop_button.grid(row=1, column=3, padx=5, pady=5)

    # Add Song button
    add_button = Button(root, text="Add Song", width=10, command=add_song, bg='lightyellow')
    add_button.grid(row=2, column=0, padx=5, pady=5)

    previous_button = Button(root, text="Previous", width=10, command=previous_song, bg='lightyellow')
    previous_button.grid(row=2, column=1, padx=5, pady=5)

    next_button = Button(root, text="Next", width=10, command=next_song, bg='lightyellow')
    next_button.grid(row=2, column=2, padx=5, pady=5)

    delete_button = Button(root, text="Delete", width=10, command=delete_song, bg='lightyellow')
    delete_button.grid(row=2, column=3, padx=5, pady=5)
    
    volume_label = Label(root, text="Volume", bg='lightpink')
    volume_label.grid(row=3,column=0, padx=5, pady=5)
    volume_slider = Scale(root, from_=0, to=100, orient=HORIZONTAL, command=set_volume, bg='lightpink')
    volume_slider.set(50)  # Set default volume to 50%
    volume_slider.grid(row=3,column=1, padx=5, pady=5)

    # Status label
    status_label = Label(root, text="Welcome to PiMusic3 Player App", wraplength=300, bg='lightblue')
    status_label.grid(row=6, column=0, columnspan=4, pady=10)

    # Load songs from the database
    load_song_list()

    root.mainloop()

# Main execution
if __name__ == "__main__":
    init_db()  # Initialize database
    init_gui()  # Initialize and run the GUI
