import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import platform

def select_m3u_file():
    file_path = filedialog.askopenfilename(filetypes=[("M3U files", "*.m3u")])
    if file_path:
        m3u_entry.delete(0, tk.END)
        m3u_entry.insert(0, file_path)
        update_example_and_prefix(file_path)

def update_example_and_prefix(m3u_file):
    with open(m3u_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):  # Ignore comments and empty lines
            example_text.config(state=tk.NORMAL)
            example_text.delete(1.0, tk.END)
            example_text.insert(tk.END, f"Ejemplo: {line}")
            example_text.config(state=tk.DISABLED)
            first_parent_folder = line.split('/')[0] + '/'
            prefix_entry.delete(0, tk.END)
            prefix_entry.insert(0, first_parent_folder)
            return

def select_music_directory():
    directory_path = filedialog.askdirectory()
    if directory_path:
        music_dir_entry.delete(0, tk.END)
        music_dir_entry.insert(0, directory_path)

def select_destination_directory():
    directory_path = filedialog.askdirectory()
    if directory_path:
        dest_dir_entry.delete(0, tk.END)
        dest_dir_entry.insert(0, directory_path)

def create_playlist_folder():
    m3u_file = m3u_entry.get()
    music_directory = music_dir_entry.get()
    dest_directory = dest_dir_entry.get()
    prefix_to_remove = prefix_entry.get()
    log_text.delete(1.0, tk.END)
    
    if not m3u_file or not os.path.exists(m3u_file):
        messagebox.showerror("Error", "Seleccione un archivo .m3u")
        return
    
    if not music_directory or not os.path.exists(music_directory):
        messagebox.showerror("Error", "Seleccione una ruta valida")
        return

    if not dest_directory or not os.path.exists(dest_directory):
        messagebox.showerror("Error", "Seleccione una ruta valida")
        return

    playlist_name = os.path.splitext(os.path.basename(m3u_file))[0]
    output_directory = os.path.join(dest_directory, playlist_name)

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(m3u_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):  # Ignore comments and empty lines
            try:
                if line.startswith(prefix_to_remove):
                    line = line[len(prefix_to_remove):]  # Remove the specified prefix
                song_path = os.path.abspath(os.path.join(music_directory, line))
                if os.path.exists(song_path):
                    shutil.copy(song_path, output_directory)
                    song_name = os.path.basename(song_path)
                    log_text.insert(tk.END, f"OK: {song_name}\n", "ok")
                else:
                    log_text.insert(tk.END, f"File not found: {line}\n", "error")
            except Exception as e:
                log_text.insert(tk.END, f"Error copying file {line}: {e}\n", "error")

    messagebox.showinfo("Success", f"Playlist folder created at: {output_directory}")
    open_folder(output_directory)

def open_folder(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":  # macOS
        subprocess.Popen(["open", path])
    else:  # Linux
        subprocess.Popen(["xdg-open", path])

def reset_fields():
    m3u_entry.delete(0, tk.END)
    music_dir_entry.delete(0, tk.END)
    dest_dir_entry.delete(0, tk.END)
    prefix_entry.delete(0, tk.END)
    log_text.delete(1.0, tk.END)
    example_text.config(state=tk.NORMAL)
    example_text.delete(1.0, tk.END)
    example_text.config(state=tk.DISABLED)

# Create the main window
root = tk.Tk()
root.title("M3U Playlist to Folder")
root.geometry("800x600")

# Create and place the widgets
m3u_label = tk.Label(root, text="Playlist M3U:")
m3u_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

m3u_entry = tk.Entry(root, width=50)
m3u_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

m3u_button = tk.Button(root, text="Browse", command=select_m3u_file)
m3u_button.grid(row=0, column=2, padx=10, pady=10)

music_dir_label = tk.Label(root, text="Carpeta raíz de Música:")
music_dir_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

music_dir_entry = tk.Entry(root, width=50)
music_dir_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

music_dir_button = tk.Button(root, text="Browse", command=select_music_directory)
music_dir_button.grid(row=1, column=2, padx=10, pady=10)

dest_dir_label = tk.Label(root, text="Carpeta destino de playlist:")
dest_dir_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

dest_dir_entry = tk.Entry(root, width=50)
dest_dir_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

dest_dir_button = tk.Button(root, text="Browse", command=select_destination_directory)
dest_dir_button.grid(row=2, column=2, padx=10, pady=10)

prefix_label = tk.Label(root, text="Prefijo a remover:")
prefix_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

prefix_entry = tk.Entry(root, width=50)
prefix_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

# Example path text widget
example_text = tk.Text(root, height=2, font=("Helvetica", 10, "italic"))
example_text.grid(row=4, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
example_text.config(state=tk.DISABLED)

create_button = tk.Button(root, text="Create Playlist Folder", command=create_playlist_folder)
create_button.grid(row=5, column=0, columnspan=1, pady=10)

reset_button = tk.Button(root, text="Reset", command=reset_fields)
reset_button.grid(row=5, column=2, columnspan=1, pady=10)

log_text = scrolledtext.ScrolledText(root, width=80, height=20)
log_text.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

# Define tags for styling
log_text.tag_config("ok", foreground="black", font=("Helvetica", 10, "bold"))
log_text.tag_config("error", foreground="red", font=("Helvetica", 10, "bold"))

# Make the GUI responsive
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(6, weight=1)

# Run the main event loop
root.mainloop()
