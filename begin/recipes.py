import sys


def with_exit(fn):
    def _fn():
        sys.exit(fn())
    return _fn


@with_exit
def flake8() -> int:
    from flake8.main.cli import main
    return main(sys.argv[2:])
