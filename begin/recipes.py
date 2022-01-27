import sys
from typing import (
    Any,
    Callable,
    NoReturn,
)

from begin.utils import patched_argv_context


def with_exit(fn: Callable) -> Callable:
    def _fn(*args: Any, **kwargs: Any) -> NoReturn:
        sys.exit(fn(*args, **kwargs))
    return _fn


@with_exit
def black(*args: str) -> int:
    from black import patched_main as _black_main

    # black.main expects a list of strings
    args_list = list(args)

    with patched_argv_context('black', *args_list):
        return _black_main()


@with_exit
def coverage(*args: str) -> int:
    from coverage.cmdline import main as _coverage_main

    # coverage.cmdline.main expects a list of strings
    args_list = list(args)

    return _coverage_main(args_list)


@with_exit
def flake8(*args: str) -> int:
    from flake8.main.cli import main as _flake8_main

    # flake8.main.cli.main expects a list of strings
    args_list = list(args)

    return _flake8_main(args_list)


@with_exit
def isort(*args: str) -> int:
    from isort.main import main

    return main(args)


@with_exit
def pytest(*args: str) -> int:
    from pytest import main as _pytest_main

    # pytest.main expects a list of strings
    args_list = list(args)

    return _pytest_main(args_list)
