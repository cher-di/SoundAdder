import os as _os
import platform as _platform

SCRIPT_ROOT = _os.path.realpath(_os.path.dirname(_os.path.dirname(__file__)))
TOOLS_PATH = _os.path.join(SCRIPT_ROOT, 'tools')

_ffmpeg_binary = 'ffmpeg.exe' if _platform.system().lower() == 'windows' else 'ffmpeg'
_ffprobe_binary = 'ffprobe.exe' if _platform.system().lower() == 'windows' else 'ffprobe'

FFMPEG = _os.path.join(TOOLS_PATH, _ffmpeg_binary)
FFPROBE = _os.path.join(TOOLS_PATH, _ffprobe_binary)

APP_NAME = 'SoundAdder'
