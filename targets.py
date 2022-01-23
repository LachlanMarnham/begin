from begin import Registry


registry = Registry()
# registry_2 = Registry()
# registry_3 = Registry(name='global')


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
