from abc import (
    ABCMeta,
    abstractmethod,
)
import string
import random

from begin.registry import Target


class AbstractFactory(metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    def create(self):
        pass


def make_random_function_name():
    """ Function names can contain uppercase letters, lowercase letters, numbers and
    underscores, but cannot begin with a number. We will arbitrarily limit function names
    to 20 characters. We will make their minimum length to 10 characters to avoid clashes
    with other stuff in the namespace. """
    allowed_first_characters = string.ascii_letters + '_'
    allowed_characters = allowed_first_characters + string.digits

    string_length = random.randint(10, 20)
    function_name = random.choice(allowed_first_characters)
    function_name += ''.join(random.choice(allowed_characters) for _ in range(string_length - 1))

    return function_name


def create_function(fn_name=None):
    fn_name = fn_name if fn_name is not None else make_random_function_name()
    exec(f'def {fn_name}(): pass')

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
import pdb; pdb.set_trace()