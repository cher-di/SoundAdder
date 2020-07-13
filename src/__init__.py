import os as _os

script_root = _os.path.realpath(_os.path.dirname(_os.path.dirname(__file__)))
tools_path = _os.path.join(script_root, 'tools')
ffmpeg = _os.path.join(tools_path, 'ffmpeg')
ffprobe = _os.path.join(tools_path, 'ffprobe')
