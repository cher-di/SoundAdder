import requests as _requests


def get_versions() -> dict:
    with _requests.get('https://ffbinaries.com/api/v1/versions') as request:
        request.raise_for_status()
        data = request.json()
        return data['versions']


def get_binaries_links(version: str) -> dict:
    with _requests.get(f'https://ffbinaries.com/api/v1/version/{version}') as request:
        request.raise_for_status()
        data = request.json()
        return data['bin']


def get_latest_binaries_links() -> dict:
    return get_binaries_links('latest')
