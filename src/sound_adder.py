__all__ = ["SoundAdder"]

import subprocess
import os

from collections import OrderedDict, namedtuple
from time import time
from datetime import timedelta
from functools import wraps
from typing import Callable


def add_sound_to_video_time_decorator(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        _, video, sound = args

        print(f"Adding {sound} to {video}...")

        before = time()
        result = func(*args)

        print(f"Adding {sound} to {video} completed! Time: {timedelta(seconds=time() - before)}")

        return result

    return wrapper


def measure_time(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        before = time()
        result = func(*args, **kwargs)
        run_time = timedelta(seconds=time() - before)

        print(f"Run time: {run_time}")

        return result

    return wrapper


class SoundAdder:
    def __init__(self, dir_path_videos: str, dir_path_sounds: str, dir_path_result: str):
        self._dir_path_videos = self.__class__._check_dir_path(dir_path_videos)
        self._dir_path_sounds = self.__class__._check_dir_path(dir_path_sounds)
        self._dir_path_result = self.__class__._check_dir_path(dir_path_result)

        videos = self.__class__._find_videos(dir_path_videos)
        sounds = self.__class__._find_sounds(dir_path_sounds)
        if len(videos) != len(sounds):
            raise ValueError(f"Not equal number of videos and sounds: {len(videos)} videos and {len(sounds)} sounds")

        _videos, _sounds = sorted(videos), sorted(sounds)
        self._correspondence_table = OrderedDict(zip(_videos, _sounds))

    def __repr__(self):
        return f"{self.__class__.__name__}({self._dir_path_videos!r}, {self._dir_path_sounds!r}, " \
               f"{self._dir_path_result!r})"

    @add_sound_to_video_time_decorator
    def _add_sound_to_video(self, video: str, sound: str):
        video_path = os.path.join(self._dir_path_videos, video)
        sound_path = os.path.join(self._dir_path_sounds, sound)
        result_video_path = os.path.join(self._dir_path_result, video)
        return subprocess.call(("ffmpeg", "-i", video_path, "-i", sound_path, "-c:v", "copy", "-c:a", "copy",
                                "-map", "0:0", "-map", "1:0", "-map", "0:1", result_video_path),
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    @measure_time
    def run(self):
        for video, sound in self._correspondence_table.items():
            self._add_sound_to_video(video, sound)

    @staticmethod
    def _find_videos(dir_path: str) -> tuple:
        def is_video(file_name: str):
            return file_name.endswith((".mkv", ".mp4", ".avi"))

        files = os.listdir(dir_path)
        return tuple(file for file in files if is_video(file))

    @staticmethod
    def _find_sounds(dir_path: str) -> tuple:
        def is_sound(file_name: str):
            return file_name.endswith((".mka", ".aac", ".mp3", ".m4a"))

        files = os.listdir(dir_path)
        return tuple(file for file in files if is_sound(file))

    @staticmethod
    def _check_dir_path(dir_path: str) -> str:
        if not os.path.exists(dir_path):
            raise FileNotFoundError(dir_path)
        if not os.path.isdir(dir_path):
            raise ValueError(f"{dir_path} is not directory")

        return dir_path

    @property
    def correspondence_table(self) -> tuple:
        return tuple(namedtuple("correspondence_table", ("video", "sound"))._make(pair)
                     for pair in self._correspondence_table.items())


if __name__ == '__main__':
    print("This is python script with SoundAdder class")
