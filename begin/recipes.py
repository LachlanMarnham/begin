import logging
import subprocess
import sys
from pathlib import Path
from typing import (
    Callable,
    Optional,
)

from begin.utils import (
    patched_argv_context,
    with_exit,
)


logger = logging.getLogger(__name__)


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
def pip(*args) -> int:
    from pip._internal.cli.main import main

    # pip._internal.main expects a list of strings
    args_list = list(args)

    return main(args_list)


PoetryMainType = Callable[[], int]


def _get_local_poetry_entrypoint() -> Optional[PoetryMainType]:
    """ Try a regular import of `poetry.console.main`. This will
    work if, e.g., `poetry` is installed in the local virtualenv. """
    try:
        from poetry.console import main
        return main
    except ModuleNotFoundError:
        return None


def _get_global_poetry_entrypoint() -> Optional[PoetryMainType]:
    """ Try a global import of `poetry.console.main`. This will work if the
    user followed the (recommended) global `poetry` install method with
    get-poetry.py. It looks up the location of the `poetry` script, and then
    adds the package and vendored dependencies to `sys.path`. """

    # Find the location of the script which is executed when running
    # `poetry ...` from the console.
    which_poetry = subprocess.run(['which', 'poetry'], capture_output=True)
    return_code = which_poetry.returncode
    std_out = which_poetry.stdout.decode().strip()
    std_err = which_poetry.stderr.decode().strip()

    # Something went wrong with the lookup
    if return_code != 0:
        logger.info(std_out)
        logger.error(std_err)
        return None

    poetry_path = Path(std_out).resolve()
    lib = poetry_path.joinpath('../../lib').resolve()
    vendors = lib.joinpath('poetry/_vendor')
    major, minor = sys.version_info[:2]
    current_vendors = vendors.joinpath(f'py{major}.{minor}')

    sys.path.append(str(lib))
    sys.path.append(str(current_vendors))

    from poetry.console import main
    return main


@with_exit
def poetry(*args: str) -> int:
    main = _get_local_poetry_entrypoint() or _get_global_poetry_entrypoint()

    if main is None:
        raise ModuleNotFoundError("No module named 'poetry'")

    with patched_argv_context('poetry', *args):
        return main()


@with_exit
def pytest(*args: str) -> int:
    from pytest import main as _pytest_main

    # pytest.main expects a list of strings
    args_list = list(args)

    return _pytest_main(args_list)
