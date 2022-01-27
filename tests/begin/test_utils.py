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
