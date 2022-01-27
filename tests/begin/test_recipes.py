from random import randint
from unittest import mock

import pytest

from begin import recipes


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


class TestPoetry:

    def test_get_local_poetry_entrypoint_module_not_found(
        self,
        mock_missing_injected_dependency,
    ):
        """ If poetry isn't importable, the `ModuleNotFoundError` should
        be caught and `None` returned. We can't be sure that no developers
        will use a local poetry install, therefore we mock `poetry` to be sure
        despite it being a dev dependency of `begin`. Note that, with the mock:
            this will work: `import poetry`
            this will fail: `from poetry.console import main`
        """
        mock_missing_injected_dependency(module_name='poetry')
        assert recipes._get_local_poetry_entrypoint() is None

    def test_get_local_poetry_entrypoint_module_is_found(
        self,
        mock_missing_injected_dependency,
    ):
        mock_poetry = mock_missing_injected_dependency(
            module_name='poetry.console',
        )

        assert recipes._get_local_poetry_entrypoint() is mock_poetry.main

    @mock.patch('begin.recipes.subprocess')
    def test_get_global_poetry_entrypoint_module_not_found(self, mock_subprocess):
        mock_subprocess.run.return_value.return_code = 1
        assert recipes._get_global_poetry_entrypoint() is None



@mock.patch('pip._internal.cli.main.main')
def test_pip(mock_pip_internal_main):
    exit_code = randint(0, 100)
    mock_pip_internal_main.return_value = exit_code
    stub_args = ['--some', 'command', '--line', 'args']

    with pytest.raises(SystemExit) as err_info:
        recipes.pip(*stub_args)

    assert mock_pip_internal_main.call_args_list == [mock.call(stub_args)]
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
