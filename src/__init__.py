import os as _os
import platform as _platform

script_root = _os.path.realpath(_os.path.dirname(_os.path.dirname(__file__)))
tools_path = _os.path.join(script_root, 'tools')

_ffmpeg_binary = 'ffmpeg.exe' if _platform.system().lower() == 'windows' else 'ffmpeg'
_ffprobe_binary = 'ffprobe.exe' if _platform.system().lower() == 'windows' else 'ffprobe'

ffmpeg = _os.path.join(tools_path, _ffmpeg_binary)
ffprobe = _os.path.join(tools_path, _ffprobe_binary)
