__all__ = ["AudioAdder"]

import os

from collections import OrderedDict, namedtuple
from typing import Generator, Tuple

_VIDEO_EXTENSIONS = (".mkv", ".mp4", ".avi")
_AUDIO_EXTENSIONS = (".mka", ".aac", ".mp3", ".m4a")


class Runner:
    def __init__(self, video_path: str, audio_path: str, result_path: str):
        self._video_path = video_path
        self._audio_path = audio_path
        self._result_path = result_path

    @property
    def _args(self) -> Tuple:
        return "ffmpeg", "-i", self._video_path, "-i", self._audio_path,\
               "-c:v", "copy", "-c:a", "copy", "-map", "0:0", "-map", "1:0", "-map", "0:1", self._result_path

    def run_verbose(self) -> Generator[str, None, None]:
        from src.utils import execute_verbose

        for output in execute_verbose(self._args):
            yield output

    def run_silent(self) -> int:
        from src.utils import execute

        return execute(self._args)

    @property
    def video_path(self):
        return self._video_path

    @property
    def audio_path(self):
        return self._audio_path

    @property
    def result_path(self):
        return self._result_path


class AudioAdder:

    def __init__(self, dir_path_videos: str, dir_path_audios: str, dir_path_result: str):
        self._dir_path_videos = self.__class__._check_dir_path(dir_path_videos)
        self._dir_path_audios = self.__class__._check_dir_path(dir_path_audios)
        self._dir_path_result = self.__class__._check_dir_path(dir_path_result)

        videos = self.__class__._find_videos(dir_path_videos)
        audios = self.__class__._find_audios(dir_path_audios)
        if len(videos) != len(audios):
            raise ValueError(f"Not equal number of videos and audios: {len(videos)} videos and {len(audios)} audios")

        _videos, _audios = sorted(videos), sorted(audios)
        self._correspondence_table = OrderedDict(zip(_videos, _audios))

    def __repr__(self):
        return f"{self.__class__.__name__}({self._dir_path_videos!r}, {self._dir_path_audios!r}, " \
               f"{self._dir_path_result!r})"
    
    def _make_cmd_to_add_audio_to_video(self, video: str, audio: str):
        video_path = os.path.join(self._dir_path_videos, video)
        audio_path = os.path.join(self._dir_path_audios, audio)
        result_video_path = os.path.join(self._dir_path_result, video)

        return f"ffmpeg -i '{video_path}' -i '{audio_path}' -c:v copy -c:a copy -map 0:0 -map 1:0 -map 0:1 {result_video_path}"

    def _make_runner(self, video: str, audio: str):
        video_path = os.path.join(self._dir_path_videos, video)
        audio_path = os.path.join(self._dir_path_audios, audio)
        result_path = os.path.join(self._dir_path_result, video)

        return Runner(video_path, audio_path, result_path)

    def get_runners(self) -> Generator[Runner, None, None]:
        for video, audio in self._correspondence_table.items():
            yield self._make_runner(video, audio)

    @staticmethod
    def _find_videos(dir_path: str) -> tuple:
        def is_video(file_name: str):
            return file_name.endswith(_VIDEO_EXTENSIONS)

        files = os.listdir(dir_path)
        return tuple(file for file in files if is_video(file))

    @staticmethod
    def _find_audios(dir_path: str) -> tuple:
        def is_audio(file_name: str):
            return file_name.endswith(_AUDIO_EXTENSIONS)

        files = os.listdir(dir_path)
        return tuple(file for file in files if is_audio(file))

    @staticmethod
    def _check_dir_path(dir_path: str) -> str:
        if not os.path.exists(dir_path):
            raise FileNotFoundError(dir_path)
        if not os.path.isdir(dir_path):
            raise ValueError(f"{dir_path} is not directory")

        return dir_path

    @property
    def correspondence_table(self) -> tuple:
        return tuple(namedtuple("correspondence_table", ("video", "audio"))._make(pair)
                     for pair in self._correspondence_table.items())


if __name__ == '__main__':
    print("This is python script with AudioAdder class")
