import requests


__all__ = [
    'get_versions',
    'get_binaries_links',
    'get_latest_binaries_links',
]

FFBINARIES_SERVER_URL = 'https://ffbinaries.com/api/v1'


def get_versions() -> dict:
    resp = requests.get(f'{FFBINARIES_SERVER_URL}/versions')
    resp.raise_for_status()
    data = resp.json()
    return data['versions']


def get_binaries_links(version: str) -> dict:
    resp = requests.get(f'{FFBINARIES_SERVER_URL}/version/{version}')
    resp.raise_for_status()
    data = resp.json()
    return data['bin']


def get_latest_binaries_links() -> dict:
    return get_binaries_links('latest')
