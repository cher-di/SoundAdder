import logging as _logging
import datetime as _datetime
import subprocess as _subprocess
import time as _time
import os as _os
import re as _re
import enum as _enum
import json as _json

from typing import Callable as _Callable, Generator as _Generator, Iterable as _Iterable

_logging.basicConfig(level=_logging.INFO)


@_enum.unique
class FileType(_enum.Enum):
    AUDIO = _enum.auto()
    VIDEO = _enum.auto()
    UNKNOWN = _enum.auto()


class StatusFile:
    def __init__(self, file_path: str):
        self._file_path = file_path
        self._status_list = []

    def add_status(self, video_path: str, audio_path: str, result_path: str, returncode: int):
        self._status_list.append({
            "video_path": video_path,
            "audio_path": audio_path,
            "result_path": result_path,
            "returncode": returncode,
        })

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file_path is not None:
            with open(self._file_path, 'w', encoding='utf-8') as file:
                _json.dump(self._status_list, file, indent=4)


def measure_time(task_name: str) -> _Callable:
    from functools import wraps

    def decorator(func: _Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            before = _time.time()
            result = func(*args, **kwargs)
            run_time = _datetime.timedelta(seconds=_time.time() - before)

            _logging.info(f"{task_name} run time: {run_time}")

            return result

        return wrapper

    return decorator


def check_ffmpeg_installation() -> bool:
    try:
        _subprocess.check_call(("ffmpeg", "-version"),
                               stdout=_subprocess.DEVNULL,
                               stderr=_subprocess.DEVNULL)
    except (_subprocess.CalledProcessError, FileNotFoundError):
        return False
    else:
        return True


def check_ffprobe_installation() -> bool:
    try:
        _subprocess.check_call(("ffprobe", "-version"),
                               stdout=_subprocess.DEVNULL,
                               stderr=_subprocess.DEVNULL)
    except (_subprocess.CalledProcessError, FileNotFoundError):
        return False
    else:
        return True


def get_video_length(filename: str) -> float:
    result = _subprocess.run(("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                              "default=noprint_wrappers=1:nokey=1", filename),
                             stdout=_subprocess.PIPE,
                             stderr=_subprocess.STDOUT)

    return float(result.stdout)


def execute(args: _Iterable[str]) -> int:
    return _subprocess.call(tuple(args),
                            stdout=_subprocess.DEVNULL,
                            stderr=_subprocess.DEVNULL)


def execute_verbose(args: _Iterable[str]) -> _Generator[str, None, None]:
    process = _subprocess.Popen(tuple(args),
                                stdout=_subprocess.PIPE,
                                stderr=_subprocess.STDOUT,
                                universal_newlines=True)
    while True:
        try:
            yield next(process.stdout)
        except StopIteration:
            if process.returncode:
                raise _subprocess.CalledProcessError(process.returncode, tuple(args))
            else:
                break


def get_file_type(file_name: str) -> FileType:
    pattern_video = _re.compile('Stream #0:0\\(?[a-z]{0,3}\\)?: Video')
    pattern_audio = _re.compile('Stream #0:0\\(?[a-z]{0,3}\\)?: Audio')

    process = _subprocess.Popen(('ffprobe', file_name),
                                stdout=_subprocess.PIPE,
                                stderr=_subprocess.STDOUT,
                                universal_newlines=True)
    while True:
        try:
            string = next(process.stdout)
            if _re.search(pattern_video, string) is not None:
                return FileType.VIDEO
            if _re.search(pattern_audio, string) is not None:
                return FileType.AUDIO
        except StopIteration:
            return FileType.UNKNOWN


def is_video(file_name: str) -> bool:
    return get_file_type(file_name) == FileType.VIDEO


def is_audio(file_name: str) -> bool:
    return get_file_type(file_name) == FileType.AUDIO


def parse_path(path: str) -> str:
    if not _os.path.exists(path):
        raise ValueError('Nonexistent path')
    return _os.path.abspath(path)


def parse_dir_path(path: str) -> str:
    if not _os.path.isdir(path):
        raise ValueError(f'Nonexistent directory: {path}')
    return _os.path.abspath(path)


def parse_file_path(path: str) -> str:
    if not _os.path.isfile(path):
        raise ValueError(f'Nonexistent file: {path}')
    return _os.path.abspath(path)


def parse_writable_filepath(path: str) -> str:
    if _os.path.isfile(path):
        if not _os.access(path, _os.W_OK):
            raise ValueError(f"Don't have permission to rewrite file: {path}")
    else:
        dir_path = parse_dir_path(_os.path.dirname(path))
        if not _os.access(dir_path, _os.W_OK):
            raise ValueError(f"Don't have permissions to write file in this directory: {dir_path}")
    return _os.path.abspath(path)
