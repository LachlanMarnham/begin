import sys
from pathlib import Path

from begin import (
    Registry,
    recipes,
)
from begin.utils import str_to_bool


local_registry = Registry()
ci_registry = Registry(name='ci')


@local_registry.register_target
@ci_registry.register_target
def check_style():
    recipes.flake8()


@local_registry.register_target(name_override='sort_imports')
def isort():
    recipes.isort('-y')


@local_registry.register_target(name_override='tests')
def tests_with_coverage(xml_coverage_report=False):
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

    # TODO do this with arg converters
    if not isinstance(xml_coverage_report, bool):
        xml_coverage_report = str_to_bool(xml_coverage_report)

    # Use the pytest recipe to run the tests with coverage collection
    if xml_coverage_report:
        recipes.pytest('--cov', 'begin', '--cov-report', 'xml')
    else:
        recipes.pytest('--cov', 'begin')


@ci_registry.register_target(name_override='test-coverage')
def ci_tests_with_coverage():
    tests_with_coverage(xml_coverage_report=True)


@ci_registry.register_target(name_override='tests')
def tests_without_coverage():
    recipes.pytest()


@local_registry.register_target
def install():
    try:
        recipes.pip('install', '--upgrade', 'pip')
    except SystemExit as err:
        if err.code != 0:
            raise

    recipes.poetry('install')


@local_registry.register_target
def release():
    recipes.changelog_gen()


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


@local_registry.register_target(name_override='dummy2')
def dummy(arg1, arg2):
    print('default dummy', arg1, arg2)
