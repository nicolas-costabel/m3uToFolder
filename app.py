import os
import shutil
import webview
import subprocess
import platform

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>M3U Playlist to Folder</title>
    <link rel="icon" href="data:image/x-icon;base64,{base64_favicon}" type="image/x-icon">
    <style>
        html, body {{
            background-color: black;
            background-image: url('data:image/png;base64,{base64_background}');
            background-size: cover;
            color: #65ff9f;
            font-family: monospace, sans-serif;
            margin: 0;
            padding: 0;
            height: 100%;
            overflow: hidden;
        }}
        body {{
            padding: 20px;
            box-sizing: border-box;
            overflow: auto;
        }}
        body::-webkit-scrollbar {{
            display: none;
        }}
        body {{
            -ms-overflow-style: none;
            scrollbar-width: none;
        }}
        h2 {{
            text-align: center;
            margin: 0px 0px 20px 0px;
        }}
        .container {{
            max-width: 800px;
            margin: auto;
            padding: 30px;
            background-color: #222;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
        }}
        label {{
            display: block;
            margin-bottom: 8px;
        }}
        input[type="text"] {{
            width: calc(100% - 22px);
            padding: 10px;
            margin-right: 10px;
            border: 2px solid #65ff9f;
            border-radius: 10px;
            background-color: #333;
            color: #65ff9f;
        }}
        button {{
            background-color: #65ff9f;
            border: 2px solid #333;
            color: black;
            padding: 12px 20px;
            border-radius: 10px;
            cursor: pointer;
            font-family: monospace, sans-serif;
            font-weight: bold;
        }}
        button:hover {{
            background-color: #4dd484;
        }}
        .log::-webkit-scrollbar {{
            width: 0px;
            background: transparent;
        }}
        .log {{
            background-color: #333;
            border: 2px solid #65ff9f;
            color: #65ff9f;
            font-family: monospace, sans-serif;
            font-weight: bold;
            padding: 10px;
            border-radius: 10px;
            height: 200px;
            overflow-y: scroll;
        }}
        .example {{
            background-color: #333;
            padding: 10px;
            border-radius: 5px;
            color: #65ff9f;
            user-select: text;
        }}
        .linea {{
            display: flex;
            align-items: center;
            margin-bottom: 30px;
        }}
        .linea-example {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }}
        .linea-buttons {{
            display: flex;
            margin-bottom: 30px;
            justify-content: space-evenly;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>M3U Playlist to Folder</h2>
        <label for="m3u">Playlist M3U:</label>
        <div class="linea">
            <input type="text" id="m3u" readonly>
            <button onclick="selectM3UFile()">Browse</button>
        </div>

        <label for="music-dir">Root Music folder:</label>
        <div class="linea">
            <input type="text" id="music-dir" readonly>
            <button onclick="selectMusicDirectory()">Browse</button>
        </div>

        <label for="dest-dir">Playlist destination Folder:</label>
        <div class="linea">
            <input type="text" id="dest-dir" readonly>
            <button onclick="selectDestinationDirectory()">Browse</button>
        </div>

        <label for="prefix">M3U parent path to remove:</label>
        <div class="linea">
            <input type="text" id="prefix">
        </div>
        <div class="linea-example">
            <div class="example" id="example">M3U path example: </div>
        </div>

        <div class="linea-buttons">
            <button onclick="createPlaylistFolder()">Create Playlist</button>
            <button onclick="resetFields()">Reset</button>
        </div>

        <div class="log" id="log"></div>
    </div>
    <script>
        function selectM3UFile() {{
            pywebview.api.select_m3u_file().then(updateFields);
        }}

        function selectMusicDirectory() {{
            pywebview.api.select_music_directory().then(updateFields);
        }}

        function selectDestinationDirectory() {{
            pywebview.api.select_destination_directory().then(updateFields);
        }}

        function createPlaylistFolder() {{
            pywebview.api.create_playlist_folder().then(updateLog);
        }}

        function resetFields() {{
            document.getElementById('m3u').value = '';
            document.getElementById('music-dir').value = '';
            document.getElementById('dest-dir').value = '';
            document.getElementById('prefix').value = '';
            document.getElementById('example').innerText = 'M3U path example: ';
            document.getElementById('log').innerHTML = '';
        }}

        function updateFields(data) {{
            if (data.m3u) {{
                document.getElementById('m3u').value = data.m3u;
                document.getElementById('example').innerText = 'M3U path example: ' + data.example;
                document.getElementById('prefix').value = data.prefix;
            }}
            if (data.music_dir) {{
                document.getElementById('music-dir').value = data.music_dir;
            }}
            if (data.dest_dir) {{
                document.getElementById('dest-dir').value = data.dest_dir;
            }}
        }}

        function updateLog(log) {{
            document.getElementById('log').innerHTML = log.join('<br>');
        }}
    </script>
</body>
</html>
"""

def get_base64_image(image_path):
    import base64
    if not os.path.exists(image_path):
        return ""
    with open(image_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

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
base64_favicon = get_base64_image('./img/favicon.ico')
base64_background = get_base64_image('./img/background.png')
html_content = html_content.format(base64_favicon=base64_favicon, base64_background=base64_background)

window = webview.create_window("M3U Playlist to Folder", html=html_content, js_api=api)
webview.start()
