__all__ = ["FFMPEGWrapper"]

import subprocess

import src.utils as utils

from typing import Generator, Iterable


class FFMPEGWrapper:
    def __init__(self, ffmpeg_executable: str, args: Iterable):
        self._ffmpeg_executable = utils.check_ffmpeg_executable(ffmpeg_executable)
        self._exit_code = None
        self._args = (self._ffmpeg_executable,) + tuple(args)

    def execute(self) -> int:
        self._exit_code = subprocess.call(self._args,
                                          stdout=subprocess.DEVNULL,
                                          stderr=subprocess.DEVNULL)
        return self._exit_code

    def execute_verbose(self) -> Generator[str, None, None]:
        process = subprocess.Popen(self._args,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   universal_newlines=True)
        while True:
            try:
                yield next(process.stdout)
            except StopIteration:
                break

    def get_exit_code(self):
        return self._exit_code
