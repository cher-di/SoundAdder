import os
import platform
import logging
import sys

logger = logging.getLogger('SoundAdder')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)


def add_extension_if_necessary(binary: str) -> str:
    if platform.system() == 'Windows':
        binary += '.exe'
    return binary


SCRIPT_ROOT = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
TOOLS_ROOT = os.path.join(SCRIPT_ROOT, 'tools')

FFMPEG = os.path.join(TOOLS_ROOT, add_extension_if_necessary('ffmpeg'))
FFPROBE = os.path.join(TOOLS_ROOT, add_extension_if_necessary('ffprobe'))

APP_NAME = 'SoundAdder'
