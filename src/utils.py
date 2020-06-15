import logging as _logging
import datetime as _datetime
import subprocess as _subprocess
import time as _time
import os as _os

from typing import Callable as _Callable, Generator as _Generator, Iterable as _Iterable

_logging.basicConfig(level=_logging.INFO)


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
    except _subprocess.CalledProcessError:
        return False
    else:
        return True


def check_ffprobe_installation() -> bool:
    try:
        _subprocess.check_call(("ffprobe", "-version"),
                               stdout=_subprocess.DEVNULL,
                               stderr=_subprocess.DEVNULL)
    except _subprocess.CalledProcessError:
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
            break


def is_video(file_name: str) -> bool:
    video_extensions = (".mkv", ".mp4", ".avi")
    return file_name.endswith(video_extensions)


def is_audio(file_name: str) -> bool:
    audio_extensions = (".mka", ".aac", ".mp3", ".m4a")
    return file_name.endswith(audio_extensions)


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

