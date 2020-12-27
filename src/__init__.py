import os
import platform


__all__ = [
    'SCRIPT_ROOT',
    'TOOLS_ROOT',
    'FFMPEG',
    'FFPROBE',
    'APP_NAME',

    'audio_adder',
    'install',
    'runner',
    'status_file',
    'utils',
    'ffbinaries',
]


SCRIPT_ROOT = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
TOOLS_ROOT = os.path.join(SCRIPT_ROOT, 'tools')

ffmpeg_binary = 'ffmpeg.exe' if platform.system().lower() == 'windows' else 'ffmpeg'
ffprobe_binary = 'ffprobe.exe' if platform.system().lower() == 'windows' else 'ffprobe'

FFMPEG = os.path.join(TOOLS_ROOT, ffmpeg_binary)
FFPROBE = os.path.join(TOOLS_ROOT, ffprobe_binary)

APP_NAME = 'SoundAdder'
