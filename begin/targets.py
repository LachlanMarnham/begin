from begin.registry import Registry


registry = Registry()


@registry.register_target(name='install')
def install():
    print('hello')

