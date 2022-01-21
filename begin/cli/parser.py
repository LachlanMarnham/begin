import argparse
from typing import (
    Dict,
    List,
)

from begin.constants import DEFAULT_REGISTRY_NAME


class Request:
    def __init__(self, target_identifier: str) -> None:
        target_name, _, registry_namespace = target_identifier.partition('@')
        self._target_name = target_name
        self._registry_namespace = registry_namespace or DEFAULT_REGISTRY_NAME
        self._options: Dict[str, str] = {}

    def add_option(self, param_identifier: str) -> None:
        key, _, value = param_identifier.partition(':')
        self._options[key] = value


def parse_requests(args: List[str]) -> List[Request]:
    # TODO things to formalise:
    # - params must be seperated by a colon
    # - target names and registry names must not contain a colon
    # - target names and registry names must not contain an @
    # - if a target, a registry or an argument contains whitespace, it must be wrapped in '...'
    # For now, this algorithm can only handle one target request
    requests = [] 
    request = None
    for arg in args:
        if ':' not in arg:
            # Not a key:value argument pair, must be either target or target@namespace
            if request is not None:
                requests.append(request)
            request = Request(arg)
        else:
            request.add_option(arg)
    requests.append(request)
    return requests


parser = argparse.ArgumentParser(description='A utility for running targets in a targets.py file.')

parser.add_argument(
    '-e',
    '--extension',
    default='*targets.py',
    help='The suffix to match target file patterns against.',
)

parser.add_argument(
    '-g',
    '--global-dir',
    default='home',
    help='The location of the directory holding global targets files.',
)
parsed_args, extra_args = parser.parse_known_args()

def foo(key):
    print(key)

def bar(key, key_2):
    print(key)

def baz():
    pass
import pdb; pdb.set_trace()
print(parsed_args, extra_args)
