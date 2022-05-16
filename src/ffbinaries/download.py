import requests
import os

import src.ffbinaries.ffbinaries as ffbinaries

from typing import Generator, Union

__all__ = [
    'Binary',
    'FFBinary',
]


class Binary:
    def __init__(self, url: str):
        self._url = url
        self._size = self.__class__._get_size(url)

    def download(self, filepath: str) -> Generator[int, None, None]:
        with requests.get(self._url, stream=True) as response:
            response.raise_for_status()
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
                    file.flush()
                    yield os.stat(filepath).st_size

    @staticmethod
    def _get_size(url: str) -> int:
        with requests.get(url, stream=True) as response:
            return int(response.headers['Content-Length'])

    @property
    def size(self) -> int:
        return self._size

    @property
    def file_name(self):
        return self._url.split('/')[-1]


class FFBinary(Binary):
    def __init__(self,
                 binary_name: str,
                 system: str,
                 arch: str,
                 version: Union[str, None] = None):
        self._binary_name = binary_name
        self._system = system
        self._arch = arch
        download_link = self.__class__._get_ffbinary_download_link(
            binary_name, system, arch, version)
        super().__init__(download_link)

    @staticmethod
    def _get_ffbinary_download_link(binary_name: str, system: str,
                                    arch: str, version: str):
        binaries = (ffbinaries.get_latest_binaries_links() if version is None
                    else ffbinaries.get_binaries_links(version))
        system_code = f'{system.lower()}-{arch[1:]}'
        return binaries[system_code][binary_name]
