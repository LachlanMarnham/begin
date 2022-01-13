from dataclasses import dataclass


@dataclass(frozen=True)
class TargetMetaData:
    function_name: str
    registry_namespace: str

    @classmethod
    def from_target_function(cls, function, registry_namespace):
        return cls.from_target_name(
            name=function.__name__,
            registry_namespace=registry_namespace,
        )

    @classmethod
    def from_target_name(cls, name, registry_namespace):
        return cls(
            function_name=name,
            registry_namespace=registry_namespace,
        )


class Target:
    def __init__(self, function, registry_namespace):
        self._function = function
        self._registry_namespace = registry_namespace
        self._metadata = TargetMetaData.from_target_function(
            function=self._function,
            registry_namespace=self._registry_namespace,
        )

    @property
    def key(self):
        return self._metadata

    def execute(self):
        self._function()


class Registry:

    def __init__(self, name='default'):
        self.name = name
        self.targets = {}

    def register_target(self, *args, **kwargs):
        if args:
            function = args.pop()
            self._register_target(function)
        else:
            def decorator(function):
                self._register_target(function, **kwargs)
                return function
            return decorator

    def _register_target(self, function, **kwargs):
        new_target = Target(
            function=function,
            registry_namespace=self.name,
        )
        self.targets[new_target.key] = new_target

    def get_target(self, target_name, registry_namespace):
        key = TargetMetaData.from_target_name(
            name=target_name,
            registry_namespace=registry_namespace,
        )
        return self.targets.get(key)
