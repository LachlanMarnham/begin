import sys
from pathlib import Path

from begin import Registry
from begin.recipes import (
    flake8,
    pytest,
)


local_registry = Registry()
ci_registry = Registry(name='ci')


@local_registry.register_target
@ci_registry.register_target
def check_style():
    flake8()


# TODO when target name overrides are implemented, change the
# function name to tests_coverage, then override like:
# local invocation: begin tests
# ci invocation: begin test-coverage@ci
# then add a new function called tests which doesn't collect
# coverage data and invoke like tests@ci
@local_registry.register_target
@ci_registry.register_target
def tests():
    """ Note: this approach is only required because we are using `begin` to trigger
    tests of `begin`. When `begin` is used to trigger tests in 3rd party repositories,
    `pytest('--cov', 'package_name')` is sufficient to run tests. `coverage` (and
    therefore `pytest-cov`) reports incorrect coverage data if the package under test
    is imported prior to the invocation of `pytest`. Therefore, immediately before the
    call to `pytest`, we need to remove every `begin` module which was import from
    `sys.modules`. """
    import begin
    begin_dir = Path(begin.__file__).parent

    # Remove all begin modules which have been imported since
    # the interpreter started
    modules = list(sys.modules.items())
    for module_name, module_object in modules:
        module_path = getattr(module_object, '__file__', '')
        if module_name.startswith('begin') and module_path.startswith(str(begin_dir)):
            del sys.modules[module_name]

    # Use the pytest recipe to run the tests with coverage collection
    pytest('--cov', 'begin')


@local_registry.register_target
def install():
    print('default install')
