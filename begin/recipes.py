import sys


def with_exit(fn):
    def _fn(*args, **kwargs):
        sys.exit(fn(*args, **kwargs))
    return _fn


@with_exit
def flake8() -> int:
    from flake8.main.cli import main
    return main(sys.argv[2:])


@with_exit
def pytest(*args) -> int:
    import pytest

    # pytest.main expects a list of strings
    args_list = list(args)

    return pytest.main(args_list)
