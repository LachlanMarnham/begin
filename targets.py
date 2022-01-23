from begin import Registry
from begin.recipes import (
    flake8,
    pytest,
)


registry = Registry()


@registry.register_target
def check_style():
    flake8()


@registry.register_target
def tests():
    pytest(['--cov', 'begin'])


@registry.register_target
def install():
    print('default install')


@registry.register_target
def tests_with_setup():
    install()
    tests()
