import itertools
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List

import pytest

from tests.resources import factory


@pytest.fixture(scope='function')
def make_random_string():
    return factory.make_random_string


@dataclass
class TargetTreeConfig:
    home_dir: Path
    cwd_dir: Path
    override_dir: Path
    expected_target_files: List[Path]
    expected_target_files_overriden: List[Path]
    file_with_registry: Path


@pytest.fixture(autouse=True)
def begin_home(monkeypatch):
    """Clear the BEGIN_HOME env var for testing"""
    monkeypatch.delenv('BEGIN_HOME', raising=False)


@pytest.fixture(scope='function')
def target_file_tmp_tree(tmp_path):
    # Create a home directory, cwd directory and override directory in the tmp_path.
    # These should be used to monkeypatch Path.cwd, Path.home or the BEGIN_HOME
    # environment variable respectively.
    home_dir = tmp_path / 'home'
    cwd_dir = tmp_path / 'cwd'
    override_dir = tmp_path / 'override'

    # tests/resources/target_files contains three directories, home, cwd and override.
    # These contain a bunch of targets files, plus a bunch of files which
    # are not valid target files
    resources = Path(__file__).parent.joinpath('resources/target_files')
    shutil.copytree(resources / 'home', home_dir)
    shutil.copytree(resources / 'cwd', cwd_dir)
    shutil.copytree(resources / 'override', override_dir)

    # These constitute valid targets files. They are in tests/resources/target_files
    # but will be copied to tmp_path during tests (see above). Note that these values
    # are sensitive to the contents of tests/resources/target_files, and any change to
    # the resources should be reflected here.
    expected_target_subpaths_cwd = [
        'cwd/targets.py',
        'cwd/sub_dir/sub_dir_targets.py',
    ]
    expected_target_subpaths_home = [
        'home/.begin/targets.py',
        'home/.begin/other_targets.py',
        'home/.begin/sub_dir/sub_dir_targets.py',
    ]
    expected_target_subpaths_overriden = [
        'override/targets.py',
    ]

    expected_target_subpaths = itertools.chain(
        expected_target_subpaths_cwd,
        expected_target_subpaths_home,
    )
    expected_target_subpaths_overriden = itertools.chain(
        expected_target_subpaths_cwd,
        expected_target_subpaths_overriden,
    )

    expected_target_files = [tmp_path.joinpath(subpath) for subpath in expected_target_subpaths]
    expected_target_files_overriden = [tmp_path.joinpath(subpath) for subpath in expected_target_subpaths_overriden]

    # This particular file actually has a Registry instance in it, with a single
    # target.
    file_with_registry = tmp_path.joinpath('home/.begin/targets.py')

    return TargetTreeConfig(
        home_dir=home_dir,
        cwd_dir=cwd_dir,
        override_dir=override_dir,
        expected_target_files=expected_target_files,
        expected_target_files_overriden=expected_target_files_overriden,
        file_with_registry=file_with_registry,
    )


@pytest.fixture(scope='function')
def resource_factory():
    return factory.Factory()
