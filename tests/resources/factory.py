import random
import string
from abc import (
    ABCMeta,
    abstractmethod,
)
from pathlib import Path
from typing import (
    Any,
    Callable,
    List,
    Optional,
)

from begin.cli.parser import Request
from begin.registry import (
    Registry,
    Target,
)


def make_random_function_name() -> str:
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


def make_random_function(fn_name: Optional[str] = None) -> Callable:
    fn_name = fn_name or make_random_function_name()
    exec(f'def {fn_name}(): pass')
    function = locals()[fn_name]
    return function


def make_random_string(no_whitespace: bool = False, disallowed_punctuation: str = '') -> str:
    punctuation = ''.join(p for p in string.punctuation if p not in disallowed_punctuation)
    characters = string.ascii_letters + string.digits + punctuation
    if not no_whitespace:
        characters += string.whitespace
    characters += punctuation
    string_length = random.randint(1, 100)
    random_string = ''.join(random.choice(characters) for _ in range(string_length))
    return random_string


def make_random_target_name() -> str:
    return make_random_string(disallowed_punctuation=':@')


def make_random_registry_name() -> str:
    return make_random_string(disallowed_punctuation=':')


def make_random_dir_path() -> Path:
    """ Creates a fully-qualified Path to a fake directory. The directory path is
    guarantee to begin with / and starts with no special characters other than /.
    The branch_depth of the path (ie /one/two/three has a depth of 3) is random and
    lies between 2 and 10 inclusive. Each node in the branch has between 1 and 10
    characters, which comprise upper- and lower-case characters and numbers. """
    characters = string.ascii_letters + string.digits
    branch_depth = random.randint(2, 10)
    dirs = []
    for _ in range(branch_depth):
        string_length = random.randint(1, 10)
        random_string = ''.join(random.choice(characters) for _ in range(string_length))
        dirs.append(random_string)
    dir_str = '/' + '/'.join(dirs)
    return Path(dir_str)


def make_random_targets_file_path() -> Path:
    random_dir = make_random_dir_path()
    targets_file = random_dir.joinpath('targets.py')
    return targets_file


def make_random_target_identifier() -> str:
    target_name = make_random_target_name()
    registry_name = make_random_registry_name()
    return f'{target_name}@{registry_name}'


def make_random_target_arg():
    arg_name = make_random_string(no_whitespace=True, disallowed_punctuation=string.punctuation)
    arg_value = make_random_string()
    return f'{arg_name}:{arg_value}'


class AbstractFactory(metaclass=ABCMeta):

    @abstractmethod
    def create(self) -> Any:
        pass


class TargetFactory(AbstractFactory):

    def create(
        self,
        function: Optional[Callable] = None,
        registry_namespace: Optional[str] = None,
        function_name: Optional[str] = None,
    ) -> Target:
        """ Creates an instance of Target, given the target function and a
        namespace."""
        function = function or make_random_function(function_name)
        registry_namespace = registry_namespace or make_random_registry_name()

        return Target(
            function=function,
            registry_namespace=registry_namespace,
        )

    def create_multi(
        self,
        target_count: Optional[int] = None,
        registry_namespace: Optional[str] = None,
    ) -> List[Target]:
        """ Creates a list of Target instances. The list has length target_count,
        but if target_count is not provided the length will be some random int between
        1 and 10 inclusive. If the registry_namespace is provided all targets will
        have the same namespace, otherwise each target will have a randomly-generated
        namespace. """
        target_count = target_count or random.randint(1, 10)
        targets = []
        for _ in range(target_count):
            new_target = self.create(registry_namespace=registry_namespace)
            targets.append(new_target)
        return targets


class RegistryFactory(AbstractFactory):

    def __init__(self) -> None:
        self.target_factory = TargetFactory()

    def create(
        self,
        name: Optional[str] = None,
        target_functions: Optional[List[Callable]] = None,
        calling_context_path: Optional[Path] = None,
    ) -> Registry:
        """ Create a Registry instance. If name is not provided, the registry namespace
        will be generated at random. If the calling_context_path is not provided, it will
        be generated at random. If a list of target_functions are not provided, a random
        list will be generated with length between 1 and 10 inclusive. """
        name = name or make_random_registry_name()
        registry = Registry(name)
        registry.path = calling_context_path or make_random_targets_file_path()
        if target_functions is None:
            fn_list_len = random.randint(1, 10)
            target_functions = [make_random_function() for _ in range(fn_list_len)]
        for function in target_functions:
            registry.register_target(function)
        return registry

    def create_multi(self, registry_count: Optional[int] = None) -> List[Registry]:
        """ Creates a list of Registry instances. The list has length registry_count,
        but if registry_count is not provided the length will be some random int between
        1 and 10 inclusive. """
        registry_count = registry_count or random.randint(1, 10)
        registries = []
        for _ in range(registry_count):
            new_registry = self.create()
            registries.append(new_registry)
        return registries


class RequestFactory(AbstractFactory):

    def create(
        self,
        target_identifier: Optional[str] = None,
        options: Optional[List[str]] = None,
    ) -> Request:
        target_identifier = target_identifier if target_identifier is not None else make_random_target_identifier()
        options = options if options is not None else [make_random_target_arg() for _ in range(random.randint(1, 10))]
        request = Request(target_identifier)
        for option in options:
            request.add_option(option)
        return request

    def create_multi(
        self,
        request_count: Optional[int] = None,
    ) -> List[Request]:
        """ Creates a list of Request instances. The list has length request_count,
        but if request_count is not provided the length will be some random int between
        1 and 10 inclusive. """
        request_count = request_count if request_count is not None else random.randint(1, 10)
        requests = []
        for _ in range(request_count):
            new_request = self.create()
            requests.append(new_request)
        return requests


class Factory:
    target = TargetFactory()
    registry = RegistryFactory()
    request = RequestFactory()
