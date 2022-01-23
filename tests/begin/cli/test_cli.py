import inspect
import logging
from unittest import mock

import pytest

from begin.cli import cli
from begin.constants import ExitCodeEnum
from begin.exceptions import BeginError


class TestMainPublic:
    """ These are tests for begin.cli.cli.main. The tests for begin.cli.cli._main are in
    TestMainPrivate. """

    @mock.patch('begin.cli.cli._main')
    def test_main_failure(self, mock_private_main, make_random_string, caplog):
        # When begin.cli.cli._main is invoked, make it throw an exception which
        # inherits from BeginError. begin.cli.cli.main should log the exception's
        # message and exit with that exception's exit_code
        class StubException(BeginError):
            _exit_code_enum = ExitCodeEnum.UNSPECIFIED_FAILURE

        stub_error_message = make_random_string()
        mock_private_main.side_effect = StubException(stub_error_message)

        with pytest.raises(SystemExit) as e_info:
            cli.main()

        # cli.main should call cli._main
        assert mock_private_main.call_args_list == [mock.call()]

        # The correct message should be logged with level ERROR
        assert caplog.record_tuples == [
            (
                cli.__name__,
                logging.ERROR,
                stub_error_message,
            ),
        ]

        # The process should exit with the exit_code taken from StubException
        assert e_info.value.code is mock_private_main.side_effect.exit_code

    @mock.patch('begin.cli.cli._main')
    def test_main_success(self, mock_private_main, caplog):
        # When begin.cli.cli._main is invoked without throwing an error
        # inheriting from BeginError, main should exit 0.
        with pytest.raises(SystemExit) as e_info:
            cli.main()

        # cli.main should call cli._main
        assert mock_private_main.call_args_list == [mock.call()]

        # No error message should be logged
        assert caplog.record_tuples == []

        # The process should exit with code 0
        assert e_info.value.code is ExitCodeEnum.SUCCESS.value


class TestMainPrivate:
    def test_main_failure(self):
        pass


@mock.patch('begin.cli.cli.Path.home')
@mock.patch('begin.cli.cli.Path.cwd')
def test_collect_target_file_paths(mock_cwd, mock_home, target_file_tmp_tree):
    mock_cwd.return_value = target_file_tmp_tree.cwd_dir
    mock_home.return_value = target_file_tmp_tree.home_dir
    target_paths_gen = cli.collect_target_file_paths()

    # target_paths_gen should be a generator
    assert inspect.isgenerator(target_paths_gen)

    # collect_target_file_paths should collect the correct paths
    target_paths = set(target_paths_gen)
    assert target_paths == set(target_file_tmp_tree.expected_target_files)


def test_load_module_from_path(target_file_tmp_tree):
    # target_file_tmp_tree.file_with_registry is the path of a targets file
    # which actually contains a registry with a single target, called install.
    module = cli.load_module_from_path(target_file_tmp_tree.file_with_registry)

    # The loaded module should expose attributes like any imported module
    assert module.registry.name == 'resource_global'


def test_get_registries_for_module(resource_factory):
    # Create a couple of registries and attach them to a mocked module
    registry_1, registry_2 = resource_factory.registry.create_multi(registry_count=2)
    mock_module = mock.Mock()
    mock_module.registry_1 = registry_1
    mock_module.registry_2 = registry_2
    result = cli.get_registries_for_module(mock_module)

    # Note: cli.get_registries_for_module builds the list of registries by
    # iterating over dir(module). dir(module) returns results in alphabetical
    # order, so this assert is sensitive to the fact that that [registry_1, registry_2]
    # is an alphabetised list.
    assert result == [registry_1, registry_2]


def test_load_registries(target_file_tmp_tree):
    file = target_file_tmp_tree.file_with_registry
    with mock.patch.object(cli, 'collect_target_file_paths', return_value=[file]) as mock_ctfp:
        registries = cli.load_registries()
    assert mock_ctfp.call_args_list == [mock.call()]
    assert len(registries) == 1
    registry = registries.pop()
    assert registry.name == 'resource_global'
    assert registry.path == file
