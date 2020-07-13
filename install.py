import os as _os
import zipfile as _zipfile
import tempfile as _tempfile
import stat as _stat
import platform as _platform
import functools as _functools
import logging as _logging

import src.ffbinaries.download as _download_ff
import src.utils as _utils

from typing import Callable as _Callable

from src import tools_path, ffmpeg, ffprobe

_logging.basicConfig(level=_logging.INFO,
                     format='[%(levelname)s][%(name)s][%(asctime)s] %(message)s',
                     datefmt='%d.%m.%Y %H:%M:%S')
logger = _logging.getLogger(__name__)


def install(binary_name: str, binary_path: str, download_method: _Callable):
    _os.makedirs(_os.path.dirname(binary_path), exist_ok=True)
    with _tempfile.TemporaryDirectory(dir=tools_path) as temp_dir:
        filepath = _os.path.join(temp_dir, 'temp.zip')

        logger.info(f'Downloading {binary_name}')
        download_method(filepath)

        logger.info(f'Extracting {binary_name}')
        with _zipfile.ZipFile(filepath) as zipfile:
            zipfile.extract(binary_name, path=temp_dir)
        _os.rename(_os.path.join(temp_dir, binary_name), binary_path)

        if _platform.system().lower() == 'linux':
            logger.info(f'Make {binary_name} executable')
            _os.chmod(binary_path, _stat.S_IRWXU)


def if_not_verified(binary_name: str, _verifier: _Callable):
    def decorator(func: _Callable):
        @_functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not _verifier():
                logger.info(f'Installing {binary_name}')
                return func(*args, **kwargs)
            else:
                logger.info(f'{binary_name} already installed')
        return wrapper
    return decorator


def rollback_if_error(binary_name: str, binary_path: str, _verifier: _Callable):
    def decorator(func: _Callable):
        @_functools.wraps(func)
        def wrapper(*args, **kwargs):
            def rollback():
                logger.error(f'An error occurred, while installing {binary_name}')
                logger.error(f'Rollback all changes with {binary_name}')
                if _os.path.exists(binary_path):
                    _os.remove(binary_path)

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


def install_wrapper(binary_name: str, binary_path: str, _verifier: _Callable):
    def decorator(func: _Callable):
        @if_not_verified(binary_name, _verifier)
        @rollback_if_error(binary_name, binary_path, _verifier)
        @_functools.wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
        return wrapper
    return decorator


@install_wrapper('ffmpeg', ffmpeg, _utils.check_ffmpeg_installation)
def install_ffmpeg():
    install('ffmpeg', ffmpeg, _download_ff.download_ffmpeg_for_local_machine)


@install_wrapper('ffprobe', ffprobe, _utils.check_ffprobe_installation)
def install_ffprobe():
    install('ffprobe', ffprobe, _download_ff.download_ffprobe_for_local_machine)


def main():
    install_ffmpeg()
    install_ffprobe()


if __name__ == '__main__':
    main()
