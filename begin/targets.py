from begin.registry import Registry


registry = Registry()
# registry_2 = Registry()
# registry_3 = Registry(name='global')


@registry.register_target
def install():
    print('default install')


@registry.register_target(name='tests')
def tests():
    print('default tests')


@registry.register_target
def tests_with_setup():
    install()
    tests()


# TODO command line args are all passed as strings. There should be a way to register
# converters in the function. Without converters:
#
# @registry.register_target
# def target_with_params(arg_1, arg_2):
#     print('arg_1 and arg_2 are both strings')
#     pass
#
#
# def to_bool(val):
#     if val.lower() == 'true' or int(val) !== 0 or .... etc:
#         return True
#     return False
#
#
# @registry.register_target(converters={'arg_1': to_bool, 'arg_2': int})
# def target_with_params(arg_1, arg_2):
#     print('arg_1 and arg_2 are both strings')
#     pass
#
