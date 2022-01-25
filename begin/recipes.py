import sys


def with_exit(fn):
    def _fn(*args, **kwargs):
        sys.exit(fn(*args, **kwargs))
    return _fn


@with_exit
def flake8(*args) -> int:
    from flake8.main.cli import main as _flake8_main

    # flake8.main.cli.main expects a list of strings
    args_list = list(args)

    return _flake8_main(args_list)


@with_exit
def pytest(*args) -> int:
    from pytest import main as _pytest_main

    # pytest.main expects a list of strings
    args_list = list(args)

    return _pytest_main(args_list)
