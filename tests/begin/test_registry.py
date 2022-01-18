from pathlib import Path
from unittest import mock

from begin.registry import (
    Registry,
    Target,
    TargetMap,
    TargetMetaData,
)


class TestTargetMetaData:

    def test_init(self, make_random_string):
        dummy_function_name = make_random_string()
        dummy_registry_namespace = make_random_string()

        metadata = TargetMetaData(
            function_name=dummy_function_name,
            registry_namespace=dummy_registry_namespace,
        )
        assert metadata.function_name == dummy_function_name
        assert metadata.registry_namespace == dummy_registry_namespace
        assert metadata.__dataclass_params__.frozen

    def test_required_autogenerated_methods(self, make_random_string):
        # Note: this tests a few auto-generated methods on the TargetMetaData.
        # This is not intended to test the dataclasses library, but these auto-methods
        # can be switched off, and this is to ensure that they aren't.
        dummy_function_name = make_random_string()
        dummy_registry_namespace = make_random_string()

        metadata_instances = [
            TargetMetaData(function_name=dummy_function_name, registry_namespace=dummy_registry_namespace)
            for _ in range(10)
        ]

        # All instances should be equal
        assert all(instance == metadata_instances[0] for instance in metadata_instances)

        # All instances should hash to the same value
        assert all(hash(instance) == hash(metadata_instances[0]) for instance in metadata_instances)

    def test_from_target_function(self, make_random_string):
        # Tests the TargetMetaData.from_target_function factory to ensure instances
        # are correctly generated using the function name (and registry_namespace)
        dummy_registry_namespace = make_random_string()

        metadata = TargetMetaData.from_target_function(
            function=lambda: ...,
            registry_namespace=dummy_registry_namespace,
        )

        assert metadata.function_name == '<lambda>'
        assert metadata.registry_namespace is dummy_registry_namespace

    def test_from_target_name(self, make_random_string):
        dummy_function_name = make_random_string()
        dummy_registry_namespace = make_random_string()

        metadata = TargetMetaData.from_target_name(
            name=dummy_function_name,
            registry_namespace=dummy_registry_namespace,
        )

        assert metadata.function_name == dummy_function_name
        assert metadata.registry_namespace == dummy_registry_namespace


class TestTarget:

    @mock.patch('begin.registry.TargetMetaData')
    def test_initialisation(self, MockTargetMetaData):
        stub_function = lambda: ...
        stub_namespace = 'namespace'
        target = Target(function=stub_function, registry_namespace=stub_namespace)

        # target._function assigned correctly
        assert target._function is stub_function

        # target._registry_namespace assigned correctly
        assert target._registry_namespace is stub_namespace

        # target._metadata assigned correctly...
        assert target._metadata is MockTargetMetaData.from_target_function.return_value

        # ... and the value was created correctly
        assert MockTargetMetaData.from_target_function.call_args_list == [
            mock.call(
                function=stub_function,
                registry_namespace=stub_namespace,
            ),
        ]

    @mock.patch('begin.registry.TargetMetaData')
    def test_key(self, MockTargetMetaData):
        target = Target(
            function=lambda: ...,
            registry_namespace='namespace',
        )
        mock_metadata = MockTargetMetaData.from_target_function.return_value
        assert target.key is mock_metadata

    @mock.patch('begin.registry.TargetMetaData')
    def test_registry_namespace(self, MockTargetMetaData):
        target = Target(
            function=lambda: ...,
            registry_namespace='namespace',
        )
        metadata = MockTargetMetaData.from_target_function.return_value
        registry_namespace = target.registry_namespace
        assert metadata.registry_namespace is registry_namespace

    @mock.patch('begin.registry.TargetMetaData')
    def test_function_name(self, MockTargetMetaData):
        target = Target(
            function=lambda: ...,
            registry_namespace='namespace',
        )
        metadata = MockTargetMetaData.from_target_function.return_value
        function_name = target.function_name
        assert metadata.function_name is function_name

    def test_execute(self):
        mock_function = mock.Mock()
        mock_function.__name__ = 'mock_function'
        mock_target = Target(
            function=mock_function,
            registry_namespace='namespace',
        )
        return_value = mock_target.execute()

        # Target.execute should defer to Target._function
        assert mock_function.call_args_list == [mock.call()]

        # Target.execute should return None
        assert return_value is None


class TestTargetMap:

    def test_initialisation(self, resource_factory):
        registry_list = resource_factory.registry.create_multi()
        target_map = TargetMap(registry_list)
        assert target_map._registries is registry_list
        assert target_map._map == {}

    def test_create(self, resource_factory):
        registry_list = resource_factory.registry.create_multi()
        with mock.patch.object(TargetMap, 'compile') as mock_compile:
            target_map = TargetMap.create(registry_list)

        # test_create is a factory method which creates and initialises
        # a TargetMap instance...
        assert isinstance(target_map, TargetMap)
        assert target_map._registries is registry_list

        # ... but it also calls TargetMap.compile
        assert mock_compile.call_args_list == [mock.call()]

    def test_get(self, resource_factory):
        target_stub = resource_factory.target.create()
        mock_map = {
            'my_target': {
                'my_namespace': target_stub,
            },
        }
        target_map = TargetMap([])
        target_map._map = mock_map

        assert target_map.get(target_name='my_target', namespace='my_namespace') is target_stub

    def test_add(self, resource_factory):
        function_name = 'fake_name'
        namespace = 'fake_namespace'
        target_stub = resource_factory.target.create(
            function_name=function_name,
            registry_namespace=namespace,
        )

        target_map = TargetMap([])
        target_map.add(target_stub)

        assert target_map._map[function_name][namespace] is target_stub

    def test_unpack_registry(self):
        pass

    def test_compile(self, resource_factory):
        registry_list = resource_factory.registry.create_multi()
        with mock.patch.object(TargetMap, 'unpack_registry') as mock_unpack_registry:
            target_map = TargetMap(registry_list)
            target_map.compile()

        # TargetMap.compile should defer to TargetMap.unpack_registry once for each registry
        assert mock_unpack_registry.call_args_list == [mock.call(r) for r in registry_list]


class TestRegistry:

    def test_initialisation(self):
        stub_registry_name = 'stub_registry_name'
        with mock.patch.object(Registry, '_get_calling_context_path') as mock_gccp:
            registry = Registry(name='stub_registry_name')
        assert registry.name is stub_registry_name
        assert registry.targets == {}
        assert registry.path is mock_gccp.return_value

    def test_get_calling_context_path(self):
        # Registry._get_calling_context_path returns the pathlib.Path
        # of the file in which that function is called.
        calling_path = Registry._get_calling_context_path()
        assert calling_path == Path(__file__)

    def test_register_target_no_kwargs(self):
        registry = Registry()

        with mock.patch.object(registry, '_register_target') as mock_register:
            @registry.register_target
            def foo():
                pass
            assert mock_register.call_args_list == [mock.call(foo)]

    def test_register_target_with_kwargs(self):
        registry = Registry()
        options = {'key': 'value'}

        with mock.patch.object(registry, '_register_target') as mock_register:
            @registry.register_target(**options)
            def foo():
                pass

            assert mock_register.call_args_list == [mock.call(foo, key='value')]

    def test_get_target(self, resource_factory):
        registry = resource_factory.registry.create()

        # Manually unpack the targets from the registry
        for target_metadata, target in registry.targets.items():
            function_name = target_metadata.function_name
            registry_namespace = target_metadata.registry_namespace

            # Registry.get_target should return the manually-unpacked target by
            # function name and namespace
            assert registry.get_target(function_name, registry_namespace) is target
