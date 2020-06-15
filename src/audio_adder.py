import os as _os
import collections as _collections
import dataclasses as _dataclasses
import src.utils as _utils

from typing import Generator as _Generator, Tuple as _Tuple


@_dataclasses.dataclass(frozen=True)
class Runner:
    video_path: str
    audio_path: str
    result_path: str
    _args: _Tuple[str, ...] = _dataclasses.field(init=False)

    def __post_init__(self):
        object.__setattr__(self, '_args', ("ffmpeg", "-i", self.video_path, "-i", self.audio_path, "-c:v", "copy",
                                           "-c:a", "copy", "-map", "0:0", "-map", "1:0", "-map", "0:1",
                                           self.result_path))

    def run_verbose(self) -> _Generator[str, None, None]:
        for output in _utils.execute_verbose(self._args):
            yield output

    def run_silent(self) -> int:
        return _utils.execute(self._args)


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
    
    def _make_cmd_to_add_audio_to_video(self, video: str, audio: str) -> _Tuple[str, ...]:
        video_path = _os.path.join(self._dir_path_videos, video)
        audio_path = _os.path.join(self._dir_path_audios, audio)
        result_video_path = _os.path.join(self._dir_path_result, video)

        return f"ffmpeg -i '{video_path}' -i '{audio_path}' -c:v copy -c:a copy -map 0:0 -map 1:0 -map 0:1 {result_video_path}"

    def _make_runner(self, video: str, audio: str):
        video_path = _os.path.join(self._dir_path_videos, video)
        audio_path = _os.path.join(self._dir_path_audios, audio)
        result_path = _os.path.join(self._dir_path_result, video)

        return Runner(video_path, audio_path, result_path)

    def get_runners(self) -> _Generator[Runner, None, None]:
        for video, audio in self._correspondence_table.items():
            yield self._make_runner(video, audio)

    @staticmethod
    def _find_videos(dir_path: str) -> tuple:
        files = _os.listdir(dir_path)
        return tuple(file for file in files if _utils.is_video(file))

    @staticmethod
    def _find_audios(dir_path: str) -> tuple:
        files = _os.listdir(dir_path)
        return tuple(file for file in files if _utils.is_audio(file))

    @property
    def correspondence_table(self) -> tuple:
        return tuple(_collections.namedtuple("correspondence_table", ("video", "audio"))._make(pair)
                     for pair in self._correspondence_table.items())


if __name__ == '__main__':
    print("This is python script with AudioAdder class")
