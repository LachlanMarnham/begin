import sys
from pathlib import Path

from begin import (
    Registry,
    recipes,
)


local_registry = Registry()
ci_registry = Registry(name='ci')


@local_registry.register_target
@ci_registry.register_target
def check_style():
    recipes.flake8()


# TODO when target name overrides are implemented, change
# this function to sort_dependencies, override with isort,
# and stop namespacing recipes
@local_registry.register_target
def isort():
    recipes.isort('-y')


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
    recipes.pytest('--cov', 'begin')


@local_registry.register_target
def install():
    try:
        recipes.pip('install', '--upgrade', 'pip')
    except SystemExit as err:
        if err.code != 0:
            raise

    recipes.poetry('install')


@ci_registry.register_target
def setup_poetry_ci():
    try:
        # TODO once config reading is done, we can probably
        # pin the poetry version in `pyproject.toml`, read
        # it from there into settings, and use settings for
        # the version below. That way there's one source of
        # truth.
        recipes.pip('install', 'poetry==1.1.3')
    except SystemExit as err:
        if err.code != 0:
            raise

    recipes.poetry('config', 'virtualenvs.create', 'false')


@ci_registry.register_target
def install_ci():
    try:
        setup_poetry_ci()
    except SystemExit as err:
        if err.code != 0:
            raise

    install()


@ci_registry.register_target
def build():
    recipes.poetry('build')


@ci_registry.register_target
def publish():
    recipes.poetry('publish')
