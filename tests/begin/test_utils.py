import sys

import pytest

from begin import utils


def test_patched_argv_context():
    stub_args = ['call', '--with', 'args']
    real_argv = sys.argv.copy()
    with utils.patched_argv_context(*stub_args):
        # Inside the with suite, sys.argv should be
        # patched
        assert sys.argv == stub_args
    # Outside the with suite, sys.argv should be
    # reset
    assert sys.argv == real_argv


def test_patched_argv_context_with_raise():
    stub_args = ['call', '--with', 'args']
    real_argv = sys.argv.copy()
    with pytest.raises(Exception):
        with utils.patched_argv_context(*stub_args):
            # Inside the with suite, sys.argv should be
            # patched
            assert sys.argv == stub_args
            raise Exception
    # Outside the with suite, sys.argv should be
    # reset
    assert sys.argv == real_argv


@pytest.mark.parametrize('exit_code', tuple(range(20)))
def test_with_exit(exit_code):
    """ We parametrize over the first few exit codes to
    ensure they are all handled the same. `utils.with_exit`
    should always raise, even in the case where `foo` ran
    successfully (`exit_code==0`). """
    @utils.with_exit
    def foo():
        return exit_code

    with pytest.raises(SystemExit) as err_info:
        foo()

    assert err_info.value.code == exit_code
