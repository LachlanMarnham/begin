from pathlib import Path
from unittest import mock

import pytest

from begin.exceptions import RegistryNameCollisionError
from begin.registry import (
    Registry,
    RegistryManager,
    Target,
    TargetMap,
    TargetOptions,
)


class TestTarget:

    def test_initialisation(self):
        stub_function = lambda: ...
        stub_namespace = 'namespace'
        stub_name_override = 'name_override'

        target = Target(
            function=stub_function,
            registry_namespace=stub_namespace,
            name_override=stub_name_override,
        )

        # target._function assigned correctly
        assert target._function is stub_function

        # target._registry_namespace assigned correctly
        assert target._registry_namespace is stub_namespace

        # target._option assign correctly
        assert isinstance(target._options, TargetOptions)
        assert target._options.name_override is stub_name_override

    def test_registry_namespace(self):
        registry_namespace = 'namespace'
        target = Target(
            function=lambda: ...,
            registry_namespace=registry_namespace,
        )
        assert target.registry_namespace is registry_namespace

    def test_function_name_without_override(self):
        def stub_function():
            pass

        target = Target(
            function=stub_function,
            registry_namespace='namespace',
        )
        assert target.function_name is 'stub_function'

    def test_function_name_with_override(self):
        def stub_function():
            pass

        stub_name_override = 'name_override'

        target = Target(
            function=stub_function,
            registry_namespace='namespace',
            name_override=stub_name_override,
        )
        assert target.function_name is stub_name_override

    def test_execute(self):
        mock_function = mock.Mock()
        mock_function.__name__ = 'mock_function'
        mock_target = Target(
            function=mock_function,
            registry_namespace='namespace',
        )
        return_value = mock_target.execute()

        # Target.execute should return None
        assert return_value is None

        options = {'key_1': 'val_1', 'key_2': 'val_2'}
        return_value = mock_target.execute(**options)
        assert return_value is None

        # Target.execute should defer to Target._function
        assert mock_function.call_args_list == [mock.call(), mock.call(**options)]

    def test_repr(self):
        def stub_function():
            pass

        stub_namespace = 'stub_namespace'
        target = Target(function=stub_function, registry_namespace=stub_namespace)
        assert repr(target) == '<begin.registry.Target(registry_namespace=stub_namespace,function_name=stub_function)>'

    def test_hash(self):
        def stub_function():
            pass

        stub_namespace = 'stub_namespace'
        target_1 = Target(function=stub_function, registry_namespace=stub_namespace)
        target_1_repr = '<begin.registry.Target(registry_namespace=stub_namespace,function_name=stub_function)>'

        # target.__hash__ should defer to the hash of its on repr
        assert hash(target_1) == hash(target_1_repr)

        # different target instances with the same function name and namespace should have the same hash
        target_2 = Target(function=stub_function, registry_namespace=stub_namespace)
        assert hash(target_1) == hash(target_2)


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

    def test_add_targets_with_same_function_name(self, resource_factory):
        # Create two targets with the same name in different namespaces
        function_name = 'install'
        namespace_1 = 'namespace_1'
        target_1 = resource_factory.target.create(
            function_name=function_name,
            registry_namespace=namespace_1,
        )
        namespace_2 = 'namespace_2'
        target_2 = resource_factory.target.create(
            function_name=function_name,
            registry_namespace=namespace_2,
        )

        # Add them both to a TargetMap
        target_map = TargetMap([])
        target_map.add(target_1)
        target_map.add(target_2)

        # Both targets should be listed under the same function_name
        assert len(target_map._map[function_name]) == 2
        assert target_map._map[function_name][namespace_1] is target_1
        assert target_map._map[function_name][namespace_2] is target_2

    def test_unpack_registry(self, resource_factory):
        registry = resource_factory.registry.create()
        target_map = TargetMap([])
        with mock.patch.object(target_map, 'add') as mock_add:
            target_map.unpack_registry(registry)

        # TargetMap.add should have been called once for each target in the registry
        assert len(mock_add.call_args_list) == len(registry.targets)
        assert all(mock.call(target) in mock_add.call_args_list for target in registry.targets)

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
        assert registry.targets == set()
        assert registry.path is mock_gccp.return_value

    def test_get_calling_context_path(self):
        # Registry._get_calling_context_path returns the pathlib.Path
        # of the file in which that function is called.
        calling_path = Registry._get_calling_context_path()
        assert calling_path == Path(__file__)

    def test_public_register_target_no_kwargs(self):
        registry = Registry()

        with mock.patch.object(registry, '_register_target') as mock_register:
            @registry.register_target
            def foo():
                pass
            assert mock_register.call_args_list == [mock.call(foo)]

    def test_public_register_target_with_kwargs(self):
        registry = Registry()
        options = {'key': 'value'}

        with mock.patch.object(registry, '_register_target') as mock_register:
            @registry.register_target(**options)
            def foo():
                pass

            assert mock_register.call_args_list == [mock.call(foo, **options)]

    def test_public_register_target_with_multiple_registries(self):
        """ A target function should be registerable with multiple registries,
        and should be correctly namespaced by each. """
        registry_1 = Registry(name='registry_1')
        registry_2 = Registry(name='registry_2')

        @registry_1.register_target
        @registry_2.register_target
        def foo():
            pass

        for registry in (registry_1, registry_2):
            assert len(registry.targets) == 1
            target = registry.targets.pop()
            assert target.registry_namespace == registry.name
            assert target._function == foo

    def test_private_register_target_no_kwargs(self):
        registry = Registry()

        @registry.register_target
        def foo():
            pass

        assert len(registry.targets) == 1
        target = registry.targets.pop()
        assert target.registry_namespace == registry.name
        assert target._function == foo
        assert target.function_name == 'foo'


class TestRegistryManager:

    def test_initialisation(self, resource_factory):
        registries = resource_factory.registry.create_multi()
        with mock.patch('begin.registry.TargetMap.create') as mock_target_map_create:
            RegistryManager(registries)
        assert mock_target_map_create.call_args_list == [mock.call(registries)]

    def test_find_namespace_collisions_success(self, resource_factory):
        # In this context, 'success' means there are no namespace collisions
        registries = resource_factory.registry.create_multi()

        # RegistryManager.find_namespace_collisions shouldn't raise when called
        # on a list of registries with different namespaces (the default for
        # resource_factory.registry.create_multi)
        RegistryManager.find_namespace_collisions(registries)

    def test_find_namespace_collisions_failure(self, resource_factory):
        # In this context, 'failure' means there are namespace collisions
        registry_namespace = 'colliding_namespace'
        path_name_1 = Path('/path/to/foo.targets.py')
        path_name_2 = Path('/path/to/bar.targets.py')

        # Create two registries with the name namespace, defined in different
        # targets files
        registry_1 = resource_factory.registry.create(
            name=registry_namespace,
            calling_context_path=path_name_1,
        )
        registry_2 = resource_factory.registry.create(
            name=registry_namespace,
            calling_context_path=path_name_2,
        )

        with pytest.raises(RegistryNameCollisionError) as e_info:
            RegistryManager.find_namespace_collisions([registry_1, registry_2])

        # The error message should contain references to the registry_namespace
        # and both paths
        error_message = e_info.value.message
        assert registry_namespace in error_message
        assert str(path_name_1) in error_message
        assert str(path_name_2) in error_message

    def test_create(self, resource_factory):
        registries = resource_factory.registry.create_multi()
        with mock.patch.object(RegistryManager, 'find_namespace_collisions') as mock_fnc:
            manager = RegistryManager.create(registries)
        assert mock_fnc.call_args_list == [mock.call(registries)]
        assert isinstance(manager, RegistryManager)

    def test_get_target(self):
        stub_target_name = 'stub_target_name'
        stub_namespace = 'stub_namespace'

        manager = RegistryManager([])
        with mock.patch.object(manager, '_target_map') as mock_target_map:
            manager.get_target(stub_target_name, stub_namespace)

        assert mock_target_map.get.call_args_list == [mock.call(stub_target_name, stub_namespace)]
