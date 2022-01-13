import importlib.util
import sys
from pathlib import Path

from begin.registry import Registry


def get_targets_paths():
    cwd = Path.cwd()
    yield from cwd.rglob('*targets.py')
    global_targets_dir = Path.home().joinpath('.begin')
    if global_targets_dir.exists():
        yield from global_targets_dir.rglob('*targets.py')


def load_targets():
    targets = []
    for path in get_targets_paths():
        spec = importlib.util.spec_from_file_location('module.name', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for item in dir(module):
            attribute = getattr(module, item)
            if isinstance(attribute, Registry):
                targets.append(attribute)
    return targets


def main():
    requested_target = sys.argv[1]
    requested_namespace = 'global'
    registries = load_targets()
    registry_0 = registries[0]
    registry_1 = registries[1]
    target_0 = registry_0.get_target(requested_target, requested_namespace)
    target_1 = registry_1.get_target(requested_target, requested_namespace)

    if target_0 is not None:
        target_0.execute()
    if target_1 is not None:
        target_1.execute()
