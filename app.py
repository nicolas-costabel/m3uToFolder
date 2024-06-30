import os
import shutil
import webview
import subprocess
import platform

def get_example(m3u_file):
    with open(m3u_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            return line
    return ""

def create_playlist_folder(m3u, music_dir, dest_dir, prefix):
    log = []
    playlist_name = os.path.splitext(os.path.basename(m3u))[0]
    output_directory = os.path.join(dest_dir, playlist_name)

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(m3u, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            try:
                if line.startswith(prefix):
                    line = line[len(prefix):]
                song_path = os.path.abspath(os.path.join(music_dir, line))
                if os.path.exists(song_path):
                    shutil.copy(song_path, output_directory)
                    song_name = os.path.basename(song_path)
                    log.append(f"[ OK ] - {song_name}")
                else:
                    log.append(f'<span style="color:red;">[ NOT FOUND ] - {line}</span>')
            except Exception as e:
                log.append(f'<span style="color:red;">[ ERROR COPYING SONG ] {line}: {e}</span>')

    if platform.system() == "Windows":
        os.startfile(output_directory)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", output_directory])
    else:
        subprocess.Popen(["xdg-open", output_directory])

    return log

class API:
    def select_m3u_file(self):
        file_path = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG, file_types=['M3U files (*.m3u)'])
        if file_path:
            file_path = file_path[0]
            example = get_example(file_path)
            prefix = "Music/"
            return {"m3u": file_path, "example": example, "prefix": prefix}
        return {}

    def select_music_directory(self):
        directory_path = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)
        if directory_path:
            return {"music_dir": directory_path[0]}
        return {}

    def select_destination_directory(self):
        directory_path = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)
        if directory_path:
            return {"dest_dir": directory_path[0]}
        return {}

    def create_playlist_folder(self):
        m3u = self.get_current_field("m3u")
        music_dir = self.get_current_field("music-dir")
        dest_dir = self.get_current_field("dest-dir")
        prefix = self.get_current_field("prefix")
        return create_playlist_folder(m3u, music_dir, dest_dir, prefix)

    def get_current_field(self, field_id):
        return webview.windows[0].evaluate_js(f'document.getElementById("{field_id}").value')

api = API()
window = webview.create_window("M3U Playlist to Folder", "http://localhost:8000/index.html", js_api=api)
webview.start()
