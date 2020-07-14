import os as _os
import collections as _collections

import src.utils as _utils
import src.runner as _runner

from typing import Generator as _Generator, Tuple as _Tuple

from src import ffmpeg


class SoundAdderRunner(_runner.Runner):
    def __init__(self, video_path: str, audio_path: str, result_path: str):
        super().__init__((ffmpeg, "-i", video_path, "-i", audio_path, "-c:v", "copy",
                          "-c:a", "copy", "-map", "0:0", "-map", "1:0", result_path))
        self._video_path = video_path
        self._audio_path = audio_path
        self._result_path = result_path

    @property
    def video_path(self) -> str:
        return self._video_path

    @property
    def audio_path(self) -> str:
        return self._audio_path

    @property
    def result_path(self) -> str:
        return self._result_path


class AudioAdder:

    def __init__(self, dir_path_videos: str, dir_path_audios: str, dir_path_result: str):
        self._dir_path_videos = dir_path_videos
        self._dir_path_audios = dir_path_audios
        self._dir_path_result = dir_path_result

        videos = self.__class__._find_videos(dir_path_videos)
        audios = self.__class__._find_audios(dir_path_audios)
        if len(videos) != len(audios):
            raise ValueError(f"Not equal number of videos and audios: {len(videos)} videos and {len(audios)} audios")

        _videos, _audios = sorted(videos), sorted(audios)
        self._correspondence_table = _collections.OrderedDict(zip(_videos, _audios))

    def __repr__(self):
        return f"{self.__class__.__name__}({self._dir_path_videos!r}, {self._dir_path_audios!r}, " \
               f"{self._dir_path_result!r})"

    def get_runners(self) -> _Generator[SoundAdderRunner, None, None]:
        for video, audio in self._correspondence_table.items():
            video_name = _os.path.basename(video)
            result_path = _os.path.join(self._dir_path_result, video_name)
            yield SoundAdderRunner(video, audio, result_path)

    @staticmethod
    def _find_videos(dir_path: str) -> _Tuple[str, ...]:
        files = (_os.path.join(dir_path, file) for file in _os.listdir(dir_path))
        return tuple(file for file in files if _utils.is_video(file))

    @staticmethod
    def _find_audios(dir_path: str) -> _Tuple[str, ...]:
        files = (_os.path.join(dir_path, file) for file in _os.listdir(dir_path))
        return tuple(file for file in files if _utils.is_audio(file))

    @property
    def correspondence_table(self) -> tuple:
        return tuple(_collections.namedtuple("correspondence_table", ("video", "audio"))._make(pair)
                     for pair in self._correspondence_table.items())


if __name__ == '__main__':
    print("This is python script with AudioAdder class")
