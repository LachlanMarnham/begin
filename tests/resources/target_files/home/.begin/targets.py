# This should be collected because it is in $HOME/.begin/**
# and is named *targets.py
from begin.registry import Registry


registry = Registry(name='resource_global')


@registry.register_target
def install():
    pass
