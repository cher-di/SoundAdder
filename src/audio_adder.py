import os as _os
import json as _json
import datetime as _datetime

import src.utils as _utils
import src.runner as _runner

from typing import Generator as _Generator, Tuple as _Tuple, Callable as _Callable

from src import FFMPEG


class AudioAdderRunner(_runner.Runner):
    def __init__(self, video_path: str, audio_path: str, result_path: str):
        super().__init__((FFMPEG, "-i", video_path, "-i", audio_path, "-c:v", "copy",
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
    def __init__(self, dir_path_videos: str, dir_path_audios: str, dir_path_result: str, max_duration_delta=0):
        self._dir_path_videos = dir_path_videos
        self._dir_path_audios = dir_path_audios
        self._dir_path_result = dir_path_result
        self._max_duration_delta = _datetime.timedelta(seconds=max_duration_delta)

        videos = self.__class__._find_files(dir_path_videos, _utils.is_video)
        audios = self.__class__._find_files(dir_path_audios, _utils.is_audio)

        self.__class__._check_media_num(len(videos), len(audios))

        _videos, _audios = sorted(videos), sorted(audios)
        correspondence_table = tuple(tuple(pair) for pair in zip(_videos, _audios))

        self.__class__._check_media_duration(correspondence_table, self._max_duration_delta)

        self._correspondence_table = correspondence_table

    def __repr__(self):
        return f"{self.__class__.__name__}({self._dir_path_videos!r}, {self._dir_path_audios!r}, " \
               f"{self._dir_path_result!r}, {self._max_duration_delta!r})"

    def get_runners(self) -> _Generator[AudioAdderRunner, None, None]:
        for video, audio in self._correspondence_table:
            video_name = _os.path.basename(video)
            result_path = _os.path.join(self._dir_path_result, video_name)
            yield AudioAdderRunner(video, audio, result_path)

    @staticmethod
    def _find_files(dir_path: str, is_correct_file_type: _Callable) -> _Tuple[str, ...]:
        files = (_os.path.join(dir_path, file) for file in _os.listdir(dir_path))
        return tuple(file for file in files if is_correct_file_type(file))

    @staticmethod
    def _check_media_num(videos_num: int, audios_num: int):
        if videos_num != audios_num:
            raise ValueError(f"Not equal number of videos and audios: {videos_num} videos and {audios_num} audios")

    @staticmethod
    def _check_media_duration(correspondence_table: _Tuple[_Tuple[str, str], ...],
                              max_duration_delta: _datetime.timedelta):
        different_length = []
        for video, audio in correspondence_table:
            video_duration = _utils.get_media_duration(video)
            audio_duration = _utils.get_media_duration(audio)
            if abs(video_duration - audio_duration) > max_duration_delta:
                different_length.append({
                    video: str(video_duration),
                    audio: str(audio_duration),
                })
        if different_length:
            raise ValueError(f'There are some videos and audios with difference between durations '
                             f'more than {max_duration_delta}: 'f'{_json.dumps(different_length, indent=4)}')

    @property
    def correspondence_table(self) -> _Tuple[_Tuple[str, str], ...]:
        return self._correspondence_table


if __name__ == '__main__':
    print("This is python script with AudioAdder class")
