import sys
from contextlib import contextmanager
from typing import (
    Any,
    Callable,
    NoReturn,
)


@contextmanager
def patched_argv_context(*args):
    """ Used to patch `sys.argv` for the duration of a call
    to a recipe. When wrapping the entry points of packages,
    sometimes the entry-point accepts a list of arguments
    to use instead of `sys.argv` (see, e.g., `recipes.pytest`).
    But sometimes arguments cannot be passed explicitly
    (see, e.g., `recipes.black`). In those cases, we monkeypatch
    `sys.argv` and restore it after the entry-point call.
    Example usage:

        import black
        with patched_argv_contest('black', '--cmd', 'line', '--args'):
            black.main()

    """
    _old_argv = sys.argv.copy()
    sys.argv = list(args)
    try:
        yield
    finally:
        sys.argv = _old_argv


def with_exit(fn: Callable) -> Callable:
    def _fn(*args: Any, **kwargs: Any) -> NoReturn:
        sys.exit(fn(*args, **kwargs))
    return _fn


def str_to_bool(arg: str) -> bool:
    if arg.lower() in {'y', 'yes', 'true', 't', '1'}:
        return True
    return False
