from unittest import mock

import pytest

from begin.cli import parser
from begin.constants import DEFAULT_REGISTRY_NAME


class TestRequest:
    @pytest.mark.parametrize('target_identifier, target_name, registry_namespace', (
        ('foo', 'foo', DEFAULT_REGISTRY_NAME),
        ('foo@', 'foo', DEFAULT_REGISTRY_NAME),
        ('foo@bar', 'foo', 'bar'),
        ('foo@bar baz', 'foo', 'bar baz'),
        ('foo@bar@baz', 'foo', 'bar@baz'),
    ))
    def test_initialisation(self, target_identifier, target_name, registry_namespace):
        request = parser.Request(target_identifier)
        assert request._target_name == target_name
        assert request._registry_namespace == registry_namespace

    @pytest.mark.parametrize('param_identifier, options', (
        ('foo:bar', {'foo': 'bar'}),
        ('foo:bar baz', {'foo': 'bar baz'}),
        ('foo:bar@baz', {'foo': 'bar@baz'}),
    ))
    def test_add_option(self, param_identifier, options):
        request = parser.Request('target@namespace')
        request.add_option(param_identifier)
        assert request._options == options


@mock.patch.object(parser, '_parse_requests')
@mock.patch.object(parser, 'ArgumentParser')
def test_parse_command(MockArgumentParser, mock_parse_requests):
    mock_parser = MockArgumentParser.return_value
    stub_optional_args = mock.Mock()
    stub_request_args = ['arg1', 'arg2']
    mock_parser.parse_known_args.return_value = stub_optional_args, stub_request_args
    result = parser.parse_command()

    # Each of the optional args should be added to the parser
    assert mock_parser.add_argument.call_count == len(parser.OPTIONAL_ARGS)

    # _parse_requests called with result_args
    assert mock_parse_requests.call_args_list == [mock.call(stub_request_args)]

    # ParsedCommand compiled correctly
    assert result.extension == stub_optional_args.extension
    assert result.global_dir == stub_optional_args.global_dir
    assert result.requests == mock_parse_requests.return_value
