import logging
from unittest import mock

import pytest

from begin.cli import cli
from begin.constants import ExitCodeEnum
from begin.exceptions import BeginError


class TestCli:

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