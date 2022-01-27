from random import randint
from unittest import mock
import sys

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
        """ If poetry is importable, `poetry.console.main` should be returned """
        mock_poetry = mock_missing_injected_dependency(
            module_name='poetry.console',
        )

        assert recipes._get_local_poetry_entrypoint() is mock_poetry.main

    @mock.patch('begin.recipes.subprocess')
    def test_get_global_poetry_entrypoint_module_not_found(self, mock_subprocess):
        """ If the call to `which poetry` returns a non-zero exit code, `None` 
        should be returned. """
        mock_subprocess.run.return_value.returncode = 1
        assert recipes._get_global_poetry_entrypoint() is None
        assert mock_subprocess.run.call_args_list == [mock.call(['which', 'poetry'], capture_output=True)]

    @mock.patch('begin.recipes.subprocess')
    def test_get_global_poetry_entrypoint_module_is_found(
        self,
        mock_subprocess,
        mock_missing_injected_dependency,
        tmp_path,
    ):
        """ If the call to `which poetry` returns an exit code of zero, mock the
        `poetry` path with a `tmp_path` and make sure its derivatives are added
        to the `sys.path` and the module can be imported. """
        mock_poetry = mock_missing_injected_dependency(
            module_name='poetry.console',
        )
        mock_which_poetry = mock_subprocess.run.return_value

        # `which poetry` was successful: exit code should be 0 and a (`bytes`) path
        # to the `poetry` entrypoint should be returned.
        mock_which_poetry.returncode = 0
        mock_which_poetry.stdout = bytes(tmp_path)
        expected_lib = tmp_path.joinpath('../../lib').resolve()
        expected_current_vendors = expected_lib.joinpath(
            'poetry/_vendor/py{0[0]}.{0[1]}'.format(sys.version_info),
        )

        # `poetry.console.main` should be returned
        assert recipes._get_global_poetry_entrypoint() == mock_poetry.main

        # A couple of derivates of the `tmp_path` should have been added to the
        # `sys.path`
        assert str(expected_current_vendors) in sys.path
        assert str(expected_lib) in sys.path

    @mock.patch('begin.recipes.patched_argv_context')
    @mock.patch('begin.recipes._get_global_poetry_entrypoint')
    @mock.patch('begin.recipes._get_local_poetry_entrypoint')
    @pytest.mark.parametrize('local_main, global_main', (
        (mock.Mock(), mock.Mock()),
        (mock.Mock(), None),
        (None, mock.Mock()),
    ))
    def test_recipe_poetry_importable(self,
        mock_get_local_poetry,
        mock_get_global_poetry,
        mock_patched_argv_ctx,
        local_main,
        global_main,
    ):
        """ Mock out `recipes._get_local_poetry_entrypoint` and
        `recipes._get_global_poetry_entrypoint`, and parametrize over whether
        they do/don't return a function. When neither return a function
        the recipe behaviour is different. That case is covered in
        `test_recipe_poetry_not_importable`. """
        exit_code = randint(0, 100)

        if isinstance(local_main, mock.Mock):
            local_main.return_value = exit_code
        if isinstance(global_main, mock.Mock):
            global_main.return_value = exit_code
        mock_get_local_poetry.return_value = local_main
        mock_get_global_poetry.return_value = global_main
        stub_args = ['--some', 'command', '--line', 'args']

        # The recipe should exit with the correct status
        with pytest.raises(SystemExit) as err_info:
            recipes.poetry(*stub_args)
        assert err_info.value.code == exit_code

        # Checks how many times `_get_global_poetry_entrypoint` and
        # `_get_local_poetry_entrypoint`, and their returned `main`
        # functions, are called
        if local_main is not None:
            assert mock_get_local_poetry.call_args_list == [mock.call()]
            assert mock_get_global_poetry.call_args_list == []
            assert local_main.call_args_list == [mock.call()]
        else:
            assert mock_get_local_poetry.call_args_list == [mock.call()]
            assert mock_get_global_poetry.call_args_list == [mock.call()]
            assert global_main.call_args_list == [mock.call()]

        # Arguments passed to the recipe should propagate to patched_argv_context
        assert mock_patched_argv_ctx.call_args_list == [mock.call('poetry', *stub_args)]

    @mock.patch('begin.recipes._get_global_poetry_entrypoint', return_value=None)
    @mock.patch('begin.recipes._get_local_poetry_entrypoint', return_value=None)
    def test_recipe_poetry_not_importable(self, mock_get_local, mock_get_global):
        with pytest.raises(ModuleNotFoundError) as err_info:
            recipes.poetry('--some', 'command', '--line', 'args')
        assert mock_get_local.call_args_list == [mock.call()]
        assert mock_get_global.call_args_list == [mock.call()]

        # The error message should match the standard ModuleImportError message,
        # but is raised manually
        assert str(err_info.value) == "No module named 'poetry'"


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
