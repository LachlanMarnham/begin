from begin.registry import Registry


registry = Registry()
registry_2 = Registry()
registry_3 = Registry(name='global')


@registry.register_target(name='install')
def install():
    print('default install')


@registry.register_target(name='tests')
def tests():
    print('default tests')
