import datetime as _datetime
import subprocess as _subprocess
import os as _os
import re as _re
import enum as _enum
import json as _json
import platform as _platform

from typing import Generator as _Generator, Iterable as _Iterable

from src import ffmpeg, ffprobe


@_enum.unique
class FileType(_enum.Enum):
    AUDIO = _enum.auto()
    VIDEO = _enum.auto()
    UNKNOWN = _enum.auto()


def check_ffmpeg_installation() -> bool:
    try:
        _subprocess.check_call((ffmpeg, "-version"),
                               stdout=_subprocess.DEVNULL,
                               stderr=_subprocess.DEVNULL)
    except (_subprocess.CalledProcessError, FileNotFoundError):
        return False
    else:
        return True


def check_ffprobe_installation() -> bool:
    try:
        _subprocess.check_call((ffprobe, "-version"),
                               stdout=_subprocess.DEVNULL,
                               stderr=_subprocess.DEVNULL)
    except (_subprocess.CalledProcessError, FileNotFoundError):
        return False
    else:
        return True


def get_media_duration(filename: str) -> _datetime.timedelta:
    result = _subprocess.run((ffprobe, "-v", "error", "-show_entries", "format=duration", "-of",
                              "default=noprint_wrappers=1:nokey=1", filename),
                             stdout=_subprocess.PIPE,
                             stderr=_subprocess.STDOUT)
    video_length = float(result.stdout)
    return _datetime.timedelta(seconds=int(video_length))


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

    process = _subprocess.Popen((ffprobe, file_name),
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


def parse_duration_delta(duration: str) -> int:
    duration = int(duration)
    if duration < 0:
        raise ValueError(f'Duration delta can not be negative')
    return duration


def get_arch():
    arch = _platform.machine()
    if '64' in arch:
        return 'x64'
    elif '86' in arch:
        return 'x86'
    else:
        return arch


def get_system():
    return _platform.system().lower()
