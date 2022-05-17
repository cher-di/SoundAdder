import json


class StatusFile:
    def __init__(self, file_path: str):
        self._file_path = file_path
        self._status_list = []

    def __repr__(self):
        return f'{self.__class__.__name__}({self._file_path!r})'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file_path is not None:
            with open(self._file_path, 'w', encoding='utf-8') as file:
                json.dump(self._status_list, file, indent=4)

    def add_status(self, video_path: str, audio_path: str,
                   result_path: str, return_code: int):
        self._status_list.append({
            "videoPath": video_path,
            "audioPath": audio_path,
            "resultPath": result_path,
            "returnCode": return_code,
        })
