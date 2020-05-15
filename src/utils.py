import logging

from datetime import timedelta
from typing import Callable


def ffmpeg_time_to_timedelta(ffmpeg_time: str) -> timedelta:
    hours, minutes, seconds = (int(i) for i in ffmpeg_time.split(":"))
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


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


def check_ffmpeg_executable(ffmpeg_executable: str) -> str:
    import subprocess

    try:
        subprocess.check_call((f"{ffmpeg_executable}", "-version"),
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        raise Exception(f"FFMPEG executable check failed: {ffmpeg_executable}")

    return ffmpeg_executable


def get_video_length(video_path: str, ffmpeg_executable: str) -> timedelta or None:
    import re

    from src.wrapper import FFMPEGWrapper

    args = ("-i", video_path)
    skip = False
    time = None
    time_pattern = "[0-9]{2}:[0-9]{2}:[0-9]{2}"
    for output in FFMPEGWrapper(ffmpeg_executable, args).execute_verbose():
        if skip:
            continue
        else:
            match = re.search(f"DURATION +: {time_pattern}", output)
            if match is not None:
                match = match.group(0)
                time = re.search(time_pattern, match).group(0)

    if time is None:
        return None
    else:
        return ffmpeg_time_to_timedelta(time)
