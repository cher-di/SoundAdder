import subprocess
import os
import argparse
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
        result = func()
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Program for adding sound to video")

    parser.add_argument("dir_videos",
                        help="Path to directory with videos")

    parser.add_argument("dir_sounds",
                        help="Path to directory with sounds")

    parser.add_argument("dir_results",
                        help="Path to directory to store results")

    parser.add_argument("-y",
                        help="Confirm to run script",
                        dest="confirm",
                        action="store_true")

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    sound_adder = SoundAdder(dir_path_videos=args.dir_videos,
                             dir_path_sounds=args.dir_sounds,
                             dir_path_result=args.dir_results)

    correspondence_table = sound_adder.correspondence_table
    max_file_name_video = max(len(pair.video) for pair in correspondence_table)
    max_file_name_sound = max(len(pair.sound) for pair in correspondence_table)
    header = "{:<3}{:<100}{:<100}".format("#", "Video", "Sound")
    print(header)
    print("-" * len(header))
    for number, (video, sound) in enumerate(correspondence_table):
        print("{:<3}{:<100}{:<100}".format(number + 1, video, sound))
    print(f"Result directory: {args.dir_path_result}")

    if not args.confirm:
        choice = None
        while choice not in ("y", "n"):
            choice = input("Continue? (y)es/(n)o: ")
        if choice == "n":
            print("Cancellation of program")
        else:
            sound_adder.run()
    else:
        sound_adder.run()
