from dataclasses import dataclass


@dataclass(frozen=True)
class TargetMetaData:
    function_name: str
    registry_namespace: str

    @classmethod
    def create(cls, function, registry_namespace):
        return cls(
            function_name=function.__name__,
            registry_namespace=registry_namespace,
        )


class Target:
    def __init__(self, function, registry_namespace):
        self._function = function
        self._registry_namespace = registry_namespace
        self._metadata = TargetMetaData.create(
            function=self._function,
            registry_namespace=self._registry_namespace,
        )

    def execute(self):
        self.function()

    def __hash__(self):
        return hash(self._metadata)


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
        self.targets[(self.name, function.__name__)] = function
