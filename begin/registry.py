import inspect
import logging
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Callable,
    List,
)

from begin.exceptions import RegistryNameCollisionError


logger = logging.getLogger(__name__)


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

    def __init__(self, function: Callable, registry_namespace: str) -> None:
        self._function = function
        self._registry_namespace = registry_namespace
        self._metadata = TargetMetaData.from_target_function(
            function=self._function,
            registry_namespace=self._registry_namespace,
        )

    @property
    def key(self) -> TargetMetaData:
        return self._metadata

    @property
    def registry_namespace(self) -> str:
        return self._metadata.registry_namespace

    @property
    def function_name(self) -> str:
        return self._metadata.function_name

    def execute(self) -> None:
        self._function()

    def __repr__(self) -> str:
        class_name = f'{self.__class__.__module__}.{self.__class__.__name__}'
        return f'<{class_name}(registry_namespace={self.registry_namespace},function_name={self.function_name})>'


class Registry:

    def __init__(self, name='default'):
        self.name = name
        self.targets = {}
        self.path = self._get_calling_context_path()

    @staticmethod
    def _get_calling_context_path() -> Path:
        """ Gets the `Path` of the first context in the stack to not be __file__.
        Intended to be called at instantiation-time to track the filenames of different
        targets.py files.
        Example:
            # /path/to/foo.py
            Registry._get_calling_context_path()  # Path('/path/to/foo.py')
        """
        stack = inspect.stack()
        calling_context = next(context for context in stack if context.filename != __file__)
        return Path(calling_context.filename)

    def register_target(self, *args, **kwargs):
        if args:
            # For calls like @registry.register_target
            function = args[0]
            self._register_target(function)
            return function
        else:
            # For calls like @registry.register_target(...)
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


class TargetMap:

    def __init__(self, registries):
        self._registries = registries
        self._map = {}

    @classmethod
    def create(cls, registries):
        target_map = cls(registries)
        target_map.compile()
        return target_map

    def compile(self):
        for registry in self._registries:
            self.unpack_registry(registry)

    def unpack_registry(self, registry):
        targets = registry.targets
        for _, target in targets.items():
            self.add(target)

    def add(self, target):
        target_name = target.function_name
        namespace = target.registry_namespace
        if target_name not in self._map:
            self._map[target_name] = {
                namespace: target,
            }
        else:
            self._map[target_name][namespace] = target

    def get(self, target_name, namespace):
        return self._map[target_name][namespace]


class RegistryManager:

    def __init__(self, registries: List[Registry]) -> None:
        self._target_map = TargetMap.create(registries)

    @classmethod
    def create(cls, registries: List[Registry]) -> 'RegistryManager':
        cls.find_namespace_collisions(registries)
        return cls(registries)

    @staticmethod
    def find_namespace_collisions(registries: List[Registry]) -> None:
        registry_path_map = defaultdict(list)
        for registry in registries:
            registry_path_map[registry.name].append(registry.path)

        colliding_namespaces = {name: paths for name, paths in registry_path_map.items() if len(paths) > 1}

        if colliding_namespaces:
            raise RegistryNameCollisionError(colliding_namespaces=colliding_namespaces)

    def get_target(self, requested_target_name: str, requested_namespace: str) -> Target:
        return self._target_map.get(requested_target_name, requested_namespace)
