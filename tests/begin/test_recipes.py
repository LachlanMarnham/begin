from random import randint
from unittest import mock

import pytest

from begin import recipes


@pytest.mark.parametrize('exit_code', tuple(range(20)))
def test_with_exit(exit_code):
    """ We parametrize over the first few exit codes to
    ensure they are all handled the same. `recipes.with_exit`
    should always raise, even in the case where `foo` ran
    successfully (`exit_code==0`). """
    @recipes.with_exit
    def foo():
        return exit_code

    with pytest.raises(SystemExit) as err_info:
        foo()

    assert err_info.value.code == exit_code


@mock.patch('coverage.cmdline.main')
def test_coverage(mock_coverage_main):
    exit_code = randint(0, 100)
    mock_coverage_main.return_value = exit_code
    stub_args = ['--some', 'command', '--line', 'args']

    with pytest.raises(SystemExit) as err_info:
        recipes.coverage(*stub_args)

    assert mock_coverage_main.call_args_list == [mock.call(stub_args)]
    assert err_info.value.code == exit_code


@mock.patch('flake8.main.cli.main')
def test_flake8(mock_flake8_main):
    exit_code = randint(0, 100)
    mock_flake8_main.return_value = exit_code
    stub_args = ['--some', 'command', '--line', 'args']

    with pytest.raises(SystemExit) as err_info:
        recipes.flake8(*stub_args)

    assert mock_flake8_main.call_args_list == [mock.call(stub_args)]
    assert err_info.value.code == exit_code


@mock.patch('isort.main.main')
def test_isort(mock_isort_main):
    exit_code = randint(0, 100)
    mock_isort_main.return_value = exit_code
    stub_args = ('--some', 'command', '--line', 'args')

    with pytest.raises(SystemExit) as err_info:
        recipes.isort(*stub_args)

    assert mock_isort_main.call_args_list == [mock.call(stub_args)]
    assert err_info.value.code == exit_code


@mock.patch('pytest.main')
def test_pytest(mock_pytest_main):
    exit_code = randint(0, 100)
    mock_pytest_main.return_value = exit_code
    stub_args = ['--some', 'command', '--line', 'args']

    with pytest.raises(SystemExit) as err_info:
        recipes.pytest(*stub_args)

    assert mock_pytest_main.call_args_list == [mock.call(stub_args)]
    assert err_info.value.code == exit_code


@mock.patch('begin.recipes.patched_argv_context')
def test_black(mock_patched_argv_ctx, mock_missing_injected_dependency):
    mock_black = mock_missing_injected_dependency(
        module_name='black',
    )
    exit_code = randint(0, 100)
    mock_black.patched_main.return_value = exit_code
    stub_args = ['--some', 'command', '--line', 'args']

    with pytest.raises(SystemExit) as err_info:
        recipes.black(*stub_args)

    assert mock_black.patched_main.call_args_list == [mock.call()]
    assert mock_patched_argv_ctx.call_args_list == [mock.call('black', *stub_args)]
    assert err_info.value.code == exit_code
