__all__ = ["check_ffmpeg_installation",
           "check_ffprobe_installation",
           "get_video_length",
           "measure_time",
           "execute_verbose",
           "execute"]

import logging

from datetime import timedelta
from typing import Callable, Generator, Iterable


logging.basicConfig(level=logging.INFO)


def measure_time(task_name: str) -> Callable:
    from functools import wraps

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from time import time

            before = time()
            result = func(*args, **kwargs)
            run_time = timedelta(seconds=time() - before)

            logging.info(f"{task_name} run time: {run_time}")

            return result

        return wrapper

    return decorator


def check_ffmpeg_installation() -> bool:
    import subprocess

    try:
        subprocess.check_call(("ffmpeg", "-version"),
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return False
    else:
        return True


def check_ffprobe_installation() -> bool:
    import subprocess

    try:
        subprocess.check_call(("ffprobe", "-version"),
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return False
    else:
        return True


def get_video_length(filename: str) -> float:
    import subprocess

    result = subprocess.run(("ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)

    return float(result.stdout)


def execute(args: Iterable) -> int:
    import subprocess

    return subprocess.call(tuple(args),
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)


def execute_verbose(args: Iterable) -> Generator[str, None, None]:
    import subprocess

    process = subprocess.Popen(tuple(args),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               universal_newlines=True)
    while True:
        try:
            yield next(process.stdout)
        except StopIteration:
            break
