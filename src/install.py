import os
import zipfile
import tempfile
import stat
import platform
import functools
import progressbar
import shutil
import logging

import src.ffbinaries.download as download
import src.utils as utils

from typing import Callable

from src import FFMPEG, FFPROBE, APP_NAME

__all__ = [
    'install_ffmpeg',
    'install_ffprobe',
]

logger = logging.getLogger('SoundAdder')

progressbar.streams.wrap_stderr()


def install(binary_name: str, binary_path: str):
    os.makedirs(os.path.dirname(binary_path), exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=APP_NAME) as temp_dir:
        filepath = os.path.join(temp_dir, 'temp.zip')

        binary = download.FFBinary(
            binary_name, utils.get_system(), utils.get_arch())
        logger.info(f'Downloading {binary.file_name}')
        widgets = [
            f'{binary.file_name}: ', progressbar.Percentage(),
            ' ', progressbar.Bar(),
            ' ', progressbar.ETA(),
            ' ', progressbar.FileTransferSpeed(),
        ]
        with progressbar.ProgressBar(widgets=widgets,
                                     max_value=binary.size) as bar:
            for downloaded_size in binary.download(filepath):
                bar.update(downloaded_size)

        archive_path = binary_name
        if platform.system() == 'Windows':
            archive_path += '.exe'
        logger.info(f'Extracting {archive_path} from {binary.file_name}')
        with zipfile.ZipFile(filepath) as file:
            file.extract(archive_path, path=temp_dir)
        shutil.move(os.path.join(temp_dir, archive_path), binary_path)

        if platform.system().lower() == 'linux':
            logger.info(f'Make {binary_name} executable')
            os.chmod(binary_path, stat.S_IRWXU)


def if_not_verified(binary_name: str, _verifier: Callable):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not _verifier():
                logger.info(f'Installing {binary_name}')
                return func(*args, **kwargs)
            else:
                logger.info(f'{binary_name} already installed')

        return wrapper

    return decorator


def rollback_if_error(binary_name: str, binary_path: str,
                      _verifier: Callable):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            def rollback():
                logger.error(f'An error occurred, '
                             f'while installing {binary_name}')
                logger.error(f'Rollback all changes with {binary_name}')
                if os.path.exists(binary_path):
                    os.remove(binary_path)

            try:
                result = func(*args, **kwargs)
            except Exception as e:
                rollback()
                raise e
            else:
                logger.info(f'Verifying {binary_name} installation')
                if not _verifier():
                    logger.error(f'{binary_name} installation failed')
                    rollback()
                else:
                    logger.info(f'{binary_name} installation OK')
                    return result

        return wrapper

    return decorator


def install_wrapper(binary_name: str, binary_path: str, _verifier: Callable):
    def decorator(func: Callable):
        @if_not_verified(binary_name, _verifier)
        @rollback_if_error(binary_name, binary_path, _verifier)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)

        return wrapper

    return decorator


@install_wrapper('ffmpeg', FFMPEG, utils.check_ffmpeg_installation)
def install_ffmpeg():
    install('ffmpeg', FFMPEG)


@install_wrapper('ffprobe', FFPROBE, utils.check_ffprobe_installation)
def install_ffprobe():
    install('ffprobe', FFPROBE)
