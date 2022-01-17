from abc import (
    ABCMeta,
    abstractmethod,
)

from begin.registry import Target


class AbstractFactory(metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    def create(self):
        pass


class TargetFactory(AbstractFactory):

    @staticmethod
    def create(**kwargs):
        return Target(
            function=kwargs.get('function'),
            registry_namespace=kwargs.get('registry_namespace'),
        )

# function_name = 'abc'
# exec(f'def {function_name}(): pass')
# fn = locals()['abc']
