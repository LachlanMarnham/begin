from begin.scripts.pymake import Registry


registry = Registry()


@registry.register_target(name='install')
def install():
    print('hello')

