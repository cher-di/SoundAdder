import subprocess as _subprocess

import src.utils as _utils

from typing import Iterable as _Iterable, Generator as _Generator


class RunnerError(Exception):
    pass


class NeverRanError(RunnerError):
    def __str__(self):
        return 'Runner has not ever ran'


class Runner:
    def __init__(self, args: _Iterable[str]):
        self._args = tuple(args)
        self._return_code = None

    def __repr__(self):
        return f'Runner({self._args})'

    def run_verbose(self) -> _Generator[str, None, None]:
        self._return_code = 0
        try:
            for output in _utils.execute_verbose(self._args):
                yield output
        except _subprocess.CalledProcessError as e:
            self._return_code = e.returncode

    def run_silent(self) -> int:
        self._return_code = _utils.execute(self._args)
        return self._return_code

    @property
    def return_code(self) -> int:
        if self._return_code in None:
            raise NeverRanError
        return self._return_code
