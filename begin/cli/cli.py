from pathlib import Path
import importlib.util
from begin.scripts.pymake import Registry


def get_targets_paths():
    cwd = Path.cwd()
    yield from cwd.rglob('*targets.py')
    # global_targets_dir = Path.home().joinpath('.begin')
    # if global_targets_dir.exists():
    #     yield from global_targets_dir.rglob('*targets.py')


def load_targets():
    targets = []
    for path in get_targets_paths():
        spec = importlib.util.spec_from_file_location("module.name", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for item in dir(module):
            attribute = getattr(module, item)
            if isinstance(attribute, Registry):
                targets.append(attribute)
    return targets
