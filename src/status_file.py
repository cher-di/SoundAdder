import json as _json


class StatusFile:
    def __init__(self, file_path: str):
        self._file_path = file_path
        self._status_list = []

    def __repr__(self):
        return f'StatusFile({self._file_path})'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file_path is not None:
            with open(self._file_path, 'w', encoding='utf-8') as file:
                _json.dump(self._status_list, file, indent=4)

    def add_status(self, video_path: str, audio_path: str, result_path: str, return_code: int):
        self._status_list.append({
            "video_path": video_path,
            "audio_path": audio_path,
            "result_path": result_path,
            "returncode": return_code,
        })
