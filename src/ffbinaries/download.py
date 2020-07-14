import requests as _requests

import src.ffbinaries.ffbinaries as _ffbinaries
import src.utils as _utils


def _download_binary(url: str, filepath: str):
    with _requests.get(url, stream=True) as request:
        request.raise_for_status()
        with open(filepath, 'wb') as file:
            for chunk in request.iter_content(chunk_size=8192):
                file.write(chunk)


def _download_ff_binary(binary_name: str, system: str, arch: str, filepath: str, version: str = None):
    binaries = _ffbinaries.get_latest_binaries_links() if version is None else _ffbinaries.get_binaries_links(version)
    system_code = f'{system.lower()}-{arch[1:]}'
    url = binaries[system_code][binary_name]
    _download_binary(url, filepath)


def _download_ff_binary_for_local_machine(binary_name: str, filepath: str, version: str = None):
    _download_ff_binary(binary_name, _utils.get_system(), _utils.get_arch(), filepath, version)


def download_ffmpeg(system: str, arch: str, filepath: str, version: str = None):
    _download_ff_binary('ffmpeg', system, arch, filepath, version)


def download_ffprobe(system: str, arch: str, filepath: str, version: str = None):
    _download_ff_binary('ffprobe', system, arch, filepath, version)


def download_ffmpeg_for_local_machine(filepath: str, version: str = None):
    _download_ff_binary_for_local_machine('ffmpeg', filepath, version)


def download_ffprobe_for_local_machine(filepath: str, version: str = None):
    _download_ff_binary_for_local_machine('ffprobe', filepath, version)
