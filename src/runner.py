import subprocess

from typing import Generator, Iterable

import src.utils as utils


class RunnerError(Exception):
    pass


class NeverRanError(RunnerError):
    def __str__(self):
        return 'Runner has not ever ran'


class Runner:
    def __init__(self, args: Iterable[str]):
        self._args = tuple(args)
        self._return_code = None

    def __repr__(self):
        return f'{self.__class__.__name__}({self._args!r})'

    def run_verbose(self) -> Generator[str, None, None]:
        self._return_code = 0
        try:
            for output in utils.execute_verbose(self._args):
                yield output
        except subprocess.CalledProcessError as e:
            self._return_code = e.returncode

    def run_silent(self) -> int:
        self._return_code = utils.execute(self._args)
        return self._return_code

    @property
    def return_code(self) -> int:
        if self._return_code is None:
            raise NeverRanError
        return self._return_code
