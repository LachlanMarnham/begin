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

    def test_target_name(self, resource_factory):
        request = resource_factory.request.create('target@registry')
        assert request.target_name == request._target_name == 'target'

    def test_registry_namespace(self, resource_factory):
        request = resource_factory.request.create('target@registry')
        assert request.registry_namespace == request._registry_namespace == 'registry'

    def test_options(self, resource_factory):
        request = resource_factory.request.create(options=['key_1:value_1', 'key_2:value_2'])
        assert request.options == request._options == {
            'key_1': 'value_1',
            'key_2': 'value_2',
        }


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


def test_parse_requests_one_request_no_namespace_no_args():
    requests = parser._parse_requests(['install'])
    assert len(requests) == 1
    assert requests[0].target_name == 'install'
    assert requests[0].registry_namespace == DEFAULT_REGISTRY_NAME
    assert requests[0]._options == {}


def test_parse_requests_one_request_with_namespace_no_args():
    requests = parser._parse_requests(['install@global'])
    assert len(requests) == 1
    assert requests[0].target_name == 'install'
    assert requests[0].registry_namespace == 'global'
    assert requests[0]._options == {}


@pytest.mark.parametrize('request_args, target_names, namespaces, options', (
    (
        ['install'],
        ['install'],
        [DEFAULT_REGISTRY_NAME],
        [{}],
    ),
    (
        ['install@global'],
        ['install'],
        ['global'],
        [{}],
    ),
    (
        ['install@global', 'key:value'],
        ['install'],
        ['global'],
        [{'key': 'value'}],
    ),
    (
        ['install@global', 'key1:value1', 'key2:value2'],
        ['install'],
        ['global'],
        [{'key1': 'value1', 'key2': 'value2'}],
    ),
    (
        ['install@global', 'key1:value1', 'key2:value2'],
        ['install'],
        ['global'],
        [{'key1': 'value1', 'key2': 'value2'}],
    ),
    (
        ['install@global', 'key1:value1', 'key2:value2', 'tests@code-quality'],
        ['install', 'tests'],
        ['global', 'code-quality'],
        [{'key1': 'value1', 'key2': 'value2'}, {}],
    ),
    (
        ['install@global', 'key1:value1', 'key2:value2', 'tests@code-quality', 'flake8@code-quality'],
        ['install', 'tests', 'flake8'],
        ['global', 'code-quality', 'code-quality'],
        [{'key1': 'value1', 'key2': 'value2'}, {}, {}],
    ),
    (
        ['install@global', 'key1:value1', 'key2:value2', 'tests@code-quality', 'flake8@code-quality', 'key3:value3'],
        ['install', 'tests', 'flake8'],
        ['global', 'code-quality', 'code-quality'],
        [{'key1': 'value1', 'key2': 'value2'}, {}, {'key3': 'value3'}],
    ),
))
def test_parse_requests(request_args, target_names, namespaces, options):
    requests = parser._parse_requests(request_args)

    # All requests have the right type
    assert all(isinstance(r, parser.Request) for r in requests)

    # Returned the right number of requests
    assert len(requests) == len(target_names)

    # Each request has the right target_name, namespace, and options
    for i in range(len(requests)):
        request = requests[i]
        assert request.target_name == target_names[i]
        assert request.registry_namespace == namespaces[i]
        assert request._options == options[i]
