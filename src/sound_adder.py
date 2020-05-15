__all__ = ["SoundAdder"]

import os

from collections import OrderedDict, namedtuple
from typing import Generator

from src.utils import check_ffmpeg_executable
from src.wrapper import FFMPEGWrapper


_VIDEO_EXTENSIONS = (".mkv", ".mp4", ".avi")
_AUDIO_EXTENSIONS = (".mka", ".aac", ".mp3", ".m4a")


class SoundAdderWrapper(FFMPEGWrapper):
    def __init__(self, ffmpeg_executable: str, video_path: str, sound_path: str, result_video_path: str):
        args = ("-i", video_path, "-i", sound_path, "-c:v", "copy", "-c:a", "copy", "-map", "0:0", "-map", "1:0",
                "-map", "0:1", result_video_path)

        super().__init__(ffmpeg_executable, args)

        self._video_path = video_path
        self._sound_path = sound_path
        self._result_video_path = result_video_path

    @property
    def video_path(self):
        return self._video_path

    @property
    def sound_path(self):
        return self._sound_path

    @property
    def result_video_path(self):
        return self._result_video_path


class SoundAdder:

    def __init__(self, dir_path_videos: str, dir_path_sounds: str, dir_path_result: str, ffmpeg_executable: str):
        self._dir_path_videos = self.__class__._check_dir_path(dir_path_videos)
        self._dir_path_sounds = self.__class__._check_dir_path(dir_path_sounds)
        self._dir_path_result = self.__class__._check_dir_path(dir_path_result)

        self._ffmpeg_executable = check_ffmpeg_executable(ffmpeg_executable)

        videos = self.__class__._find_videos(dir_path_videos)
        sounds = self.__class__._find_sounds(dir_path_sounds)
        if len(videos) != len(sounds):
            raise ValueError(f"Not equal number of videos and sounds: {len(videos)} videos and {len(sounds)} sounds")

        _videos, _sounds = sorted(videos), sorted(sounds)
        self._correspondence_table = OrderedDict(zip(_videos, _sounds))

    def __repr__(self):
        return f"{self.__class__.__name__}({self._dir_path_videos!r}, {self._dir_path_sounds!r}, " \
               f"{self._dir_path_result!r}, f{self._ffmpeg_executable!r})"

    def _add_sound_to_video(self, video: str, sound: str) -> SoundAdderWrapper:
        video_path = os.path.join(self._dir_path_videos, video)
        sound_path = os.path.join(self._dir_path_sounds, sound)
        result_video_path = os.path.join(self._dir_path_result, video)

        return SoundAdderWrapper(self._ffmpeg_executable, video_path, sound_path, result_video_path)

    def get_ffmpeg_wrappers(self) -> Generator[SoundAdderWrapper, None, None]:
        for video, sound in self._correspondence_table.items():
            yield self._add_sound_to_video(video, sound)

    def run(self):
        for video, sound in self._correspondence_table.items():
            self._add_sound_to_video(video, sound).execute()

    @staticmethod
    def _find_videos(dir_path: str) -> tuple:
        def is_video(file_name: str):
            return file_name.endswith(_VIDEO_EXTENSIONS)

        files = os.listdir(dir_path)
        return tuple(file for file in files if is_video(file))

    @staticmethod
    def _find_sounds(dir_path: str) -> tuple:
        def is_sound(file_name: str):
            return file_name.endswith(_AUDIO_EXTENSIONS)

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
