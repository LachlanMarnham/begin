from begin import Registry
from begin.recipes import flake8


registry = Registry()


@registry.register_target
def check_style():
    flake8()


@registry.register_target
def install():
    print('default install')


@registry.register_target(name='tests')
def tests(str_1, str_2):
    print(f'{str_1}, {str_2}!')


@registry.register_target
def tests_with_setup():
    install()
    tests()
