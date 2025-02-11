import moviepy.editor as mp

# Specify the path to ffprobe
ffprobe_path = '/path/to/ffprobe'

# Set the ffprobe path for moviepy
mp.config.change_settings({'FFPROBE_BINARY': ffprobe_path})

# Now use moviepy functions that require ffprobe

# import os
# folder_path = '/Users/krishnapahuja/Documents/Class Programming/Sem 4/Project_on_venv/HummingBird/main/static/hummings'
# print(os.listdir(folder_path))