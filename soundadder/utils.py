import datetime
import subprocess
import os
import re
import enum
import platform

from typing import Generator, Iterable

from soundadder import FFMPEG, FFPROBE


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
    cmd = (FFPROBE, "-v", "error", "-show_entries", "format=duration",
           "-of", "default=noprint_wrappers=1:nokey=1", filename)
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    video_length = float(result.stdout)
    return datetime.timedelta(seconds=int(video_length))


def execute(args: Iterable[str]) -> int:
    return subprocess.call(
        tuple(args), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def execute_verbose(args: Iterable[str]) -> Generator[str, None, None]:
    process = subprocess.Popen(tuple(args),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               universal_newlines=True)
    while True:
        try:
            yield next(process.stdout)
        except StopIteration:
            if process.returncode:
                raise subprocess.CalledProcessError(
                    process.returncode, tuple(args))
            else:
                break


def get_file_type(file_name: str) -> FileType:
    pattern_video = re.compile(r'Stream #\d+:\d+\(?[a-z]{0,3}\)?: Video')
    pattern_audio = re.compile(r'Stream #\d+:\d+\(?[a-z]{0,3}\)?: Audio')

    process = subprocess.Popen((FFPROBE, file_name),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               universal_newlines=True)
    found_audio = False
    while True:
        try:
            string = next(process.stdout)
            if re.search(pattern_video, string) is not None:
                return FileType.VIDEO
            if re.search(pattern_audio, string) is not None:
                found_audio = True
        except StopIteration:
            return FileType.AUDIO if found_audio else FileType.UNKNOWN


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
            raise ValueError(f"Don't have permissions to write "
                             f"file in this directory: {dir_path}")
    return os.path.abspath(path)


def parse_duration_delta(duration: str) -> int:
    duration = int(duration)
    if duration < 0:
        raise ValueError('Duration delta can not be negative')
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
