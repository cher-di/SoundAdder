import datetime
import subprocess
import os
import re
import enum
import platform
import typing

from src import FFMPEG, FFPROBE

__all__ = [
    'check_ffmpeg_installation',
    'check_ffprobe_installation',
    'get_media_duration',
    'execute',
    'execute_verbose',
    'get_file_type',
    'is_video',
    'is_audio',
    'parse_path',
    'parse_dir_path',
    'parse_file_path',
    'parse_writable_filepath',
    'parse_duration_delta',
]


@enum.unique
class FileType(enum.Enum):
    AUDIO = enum.auto()
    VIDEO = enum.auto()
    UNKNOWN = enum.auto()


def check_ffmpeg_installation() -> bool:
    try:
        subprocess.check_call((FFMPEG, "-version"),
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    else:
        return True


def check_ffprobe_installation() -> bool:
    try:
        subprocess.check_call((FFPROBE, "-version"),
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    else:
        return True


def get_media_duration(filename: str) -> datetime.timedelta:
    result = subprocess.run((FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    video_length = float(result.stdout)
    return datetime.timedelta(seconds=int(video_length))


def execute(args: typing.Iterable[str]) -> int:
    return subprocess.call(tuple(args),
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)


def execute_verbose(args: typing.Iterable[str]) -> typing.Generator[str, None, None]:
    process = subprocess.Popen(tuple(args),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               universal_newlines=True)
    while True:
        try:
            yield next(process.stdout)
        except StopIteration:
            if process.returncode:
                raise subprocess.CalledProcessError(process.returncode, tuple(args))
            else:
                break


def get_file_type(file_name: str) -> FileType:
    pattern_video = re.compile('Stream #0:0\\(?[a-z]{0,3}\\)?: Video')
    pattern_audio = re.compile('Stream #0:0\\(?[a-z]{0,3}\\)?: Audio')

    process = subprocess.Popen((FFPROBE, file_name),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               universal_newlines=True)
    while True:
        try:
            string = next(process.stdout)
            if re.search(pattern_video, string) is not None:
                return FileType.VIDEO
            if re.search(pattern_audio, string) is not None:
                return FileType.AUDIO
        except StopIteration:
            return FileType.UNKNOWN


def is_video(file_name: str) -> bool:
    return get_file_type(file_name) == FileType.VIDEO


def is_audio(file_name: str) -> bool:
    return get_file_type(file_name) == FileType.AUDIO


def parse_path(path: str) -> str:
    if not os.path.exists(path):
        raise ValueError('Nonexistent path')
    return os.path.abspath(path)


def parse_dir_path(path: str) -> str:
    if not os.path.isdir(path):
        raise ValueError(f'Nonexistent directory: {path}')
    return os.path.abspath(path)


def parse_file_path(path: str) -> str:
    if not os.path.isfile(path):
        raise ValueError(f'Nonexistent file: {path}')
    return os.path.abspath(path)


def parse_writable_filepath(path: str) -> str:
    if os.path.isfile(path):
        if not os.access(path, os.W_OK):
            raise ValueError(f"Don't have permission to rewrite file: {path}")
    else:
        dir_path = parse_dir_path(os.path.dirname(path))
        if not os.access(dir_path, os.W_OK):
            raise ValueError(f"Don't have permissions to write file in this directory: {dir_path}")
    return os.path.abspath(path)


def parse_duration_delta(duration: str) -> int:
    duration = int(duration)
    if duration < 0:
        raise ValueError(f'Duration delta can not be negative')
    return duration


def get_arch():
    arch = platform.machine()
    if arch in ('x86_64', 'AMD64'):
        return 'x64'
    elif arch in ('i386', 'i686'):
        return 'x86'
    else:
        return arch


def get_system():
    return platform.system().lower()
