import random
import string

import pytest


@pytest.fixture(scope='function')
def make_random_string():
    def _make_random_string():
        characters = string.ascii_letters + string.digits + string.punctuation + string.whitespace
        string_length = random.randint(1, 100)
        random_string = ''.join(random.choice(characters) for _ in range(string_length))
        return random_string
    return _make_random_string
