import random
import shutil
import string
from dataclasses import dataclass
from pathlib import Path
from typing import List
from unittest import mock

import pytest

from begin.registry import Registry


@pytest.fixture(scope='function')
def make_random_string():
    def _make_random_string(no_whitespace=False):
        characters = string.ascii_letters + string.digits + string.punctuation
        if not no_whitespace:
            characters += string.whitespace
        string_length = random.randint(1, 100)
        random_string = ''.join(random.choice(characters) for _ in range(string_length))
        return random_string
    return _make_random_string


@pytest.fixture(scope='function')
def make_random_dir_path():
    def _make_random_dir_path():
        characters = string.ascii_letters + string.digits
        tree_depth = random.randint(2, 5)
        dirs = []
        for _ in range(tree_depth):
            string_length = random.randint(1, 10)
            random_string = ''.join(random.choice(characters) for _ in range(string_length))
            dirs.append(random_string)
        dir_str = '/' + '/'.join(dirs)
        return Path(dir_str)
    return _make_random_dir_path


@dataclass
class TargetTreeConfig:
    home_dir: Path
    cwd_dir: Path
    expected_target_files: List[Path]


@pytest.fixture(scope='function')
def target_file_tmp_tree(tmp_path):
    # Create a home directory and cwd directory in the tmp_path. These
    # should be used to monkeypatch Path.cwd and Path.home
    home_dir = tmp_path / 'home'
    cwd_dir = tmp_path / 'cwd'

    # tests/resources/target_files contains two directories, home and cwd.
    # These contain a bunch of targets files, plus a bunch of files which
    # are not valid target files
    resources = Path(__file__).parent.joinpath('resources/target_files')
    shutil.copytree(resources / 'home', home_dir)
    shutil.copytree(resources / 'cwd', cwd_dir)

    # These constitute valid targets files. They are in tests/resources/target_files
    # but will be copied to tmp_path during tests (see above). Note that these values
    # are sensitive to the contents of tests/resources/target_files, and any change to
    # the resources should be reflected here.
    expected_target_subpaths = [
        'cwd/targets.py',
        'cwd/sub_dir/sub_dir_targets.py',
        'home/.begin/targets.py',
        'home/.begin/other_targets.py',
        'home/.begin/sub_dir/sub_dir_targets.py',
    ]
    expected_target_files = [tmp_path.joinpath(subpath) for subpath in expected_target_subpaths]

    return TargetTreeConfig(
        home_dir=home_dir,
        cwd_dir=cwd_dir,
        expected_target_files=expected_target_files,
    )


@pytest.fixture(scope='function')
def registry_list(make_random_dir_path):
    registry_list = []
    for _ in range(10):
        _mock_get_calling_context_path = lambda _: make_random_dir_path()
        with mock.patch.object(Registry, '_get_calling_context_path', _mock_get_calling_context_path):
            new_registry = Registry()
        registry_list.append(new_registry)
    return registry_list
