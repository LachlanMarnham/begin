import random
import string
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
    fn_name = fn_name or make_random_function_name()
    exec(f'def {fn_name}(): pass')
    function = locals()[fn_name]
    return function


def make_random_string(no_whitespace=False):
    characters = string.ascii_letters + string.digits + string.punctuation
    if not no_whitespace:
        characters += string.whitespace
    string_length = random.randint(1, 100)
    random_string = ''.join(random.choice(characters) for _ in range(string_length))
    return random_string


class TargetFactory(AbstractFactory):

    @staticmethod
    def create(function=None, registry_namespace=None):
        function = function or create_function()
        registry_namespace = registry_namespace or make_random_string()

        return Target(
            function=function,
            registry_namespace=registry_namespace,
        )
