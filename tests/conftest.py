import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List
from unittest import mock

import pytest

from tests.resources import factory


@pytest.fixture(scope='function')
def make_random_string():
    return factory.make_random_string


@dataclass
class TargetTreeConfig:
    home_dir: Path
    cwd_dir: Path
    expected_target_files: List[Path]
    file_with_registry: Path


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

    # This particular file actually has a Registry instance in it, with a single
    # target.
    file_with_registry = tmp_path.joinpath('home/.begin/targets.py')

    return TargetTreeConfig(
        home_dir=home_dir,
        cwd_dir=cwd_dir,
        expected_target_files=expected_target_files,
        file_with_registry=file_with_registry,
    )


@pytest.fixture(scope='function')
def resource_factory():
    return factory.Factory()


@pytest.fixture(scope='function')
def mock_missing_injected_dependency():
    """This is intended for use in `tests/begin/test_recipes.py`. Recipes sometimes
    use dependency injection (ie, to provide an interface in front of a package which
    is not a dependency of `begin`). This fixture can be used to mock the injected
    package. """
    _module_name = None

    def _mock_missing_injected_dependency(module_name):
        """ If the recipe contains `from package.module.submodule import main`, module
        should be `'package.module.submodule'`"""
        mock_module = mock.MagicMock()
        sys.modules[module_name] = mock_module
        nonlocal _module_name
        _module_name = module_name
        return mock_module

    yield _mock_missing_injected_dependency
    del sys.modules[_module_name]
