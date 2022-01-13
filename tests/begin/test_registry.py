from begin.registry import TargetMetaData


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

        def stub_function():
            pass

        metadata = TargetMetaData.from_target_function(
            function=stub_function,
            registry_namespace=dummy_registry_namespace,
        )

        assert metadata.function_name == 'stub_function'
        assert metadata.registry_namespace == dummy_registry_namespace

    def test_from_target_name(self, make_random_string):
        dummy_function_name = make_random_string()
        dummy_registry_namespace = make_random_string()

        metadata = TargetMetaData.from_target_name(
            name=dummy_function_name,
            registry_namespace=dummy_registry_namespace,
        )

        assert metadata.function_name == dummy_function_name
        assert metadata.registry_namespace == dummy_registry_namespace