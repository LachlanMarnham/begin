import importlib.util
import logging
import sys
from pathlib import Path
from typing import List

from begin.exceptions import BeginError
from begin.registry import (
    Registry,
    RegistryManager,
)


logger = logging.getLogger(__name__)


def get_targets_paths():
    cwd = Path.cwd()
    yield from cwd.rglob('*targets.py')
    global_targets_dir = Path.home().joinpath('.begin')
    if global_targets_dir.exists():
        yield from global_targets_dir.rglob('*targets.py')


def load_registries() -> List[Registry]:
    registries = []
    for path in get_targets_paths():
        spec = importlib.util.spec_from_file_location('module.name', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if isinstance(attribute, Registry):
                registries.append(attribute)
    return registries


def _main():
    requested_target = sys.argv[1]
    requested_namespace = sys.argv[2]
    registries = load_registries()
    manager = RegistryManager(registries)
    target = manager.get_target(requested_target, requested_namespace)
    target.execute()


def main():
    try:
        _main()
    except BeginError as ex:
        logger.error(ex.message)
        sys.exit(ex.exit_code)
    else:
        sys.exit(0)


# TODO
# >>> begin install
# The target `install` was found in multiple registries. Please select one to continue:
# [1] default
# [2] global
