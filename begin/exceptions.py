from pathlib import Path
from typing import (
    List,
    Mapping,
)
from begin.constants import ExitCodeEnum


class InterfaceMeta(type):
    def __call__(cls, *args, **kwargs):
        if not isinstance(cls._exit_code_enum, ExitCodeEnum):
            raise NotImplementedError
        return super(InterfaceMeta, cls).__call__(*args, **kwargs)


class BeginError(Exception, metaclass=InterfaceMeta):

    _exit_code_enum = None

    @property
    def exit_code(self) -> int:
        return self._exit_code_enum.value


class RegistryNameCollisionError(BeginError):

    _exit_code_enum = ExitCodeEnum.REGISTRY_NAME_COLLISION

    def __init__(self, colliding_namespaces: Mapping[str, List[Path]]) -> None:
        """ `colliding_namespaces` has registry names for keys and a list of paths
        for values. The paths in the list point to files where the namespace was defined.
        The length of each list is assumed to be greater than 1 (otherwise there is no
        namespace collision. """
        lines = []
        for name, paths in colliding_namespaces.items():
            lines.append(f'Found multiple registries with name `{name}` in files:')
            for path in paths:
                lines.append(f'\t{path}')
        message = '\n'.join(lines)
        super().__init__(message)
    
    @property
    def message(self):
        return str(self)
