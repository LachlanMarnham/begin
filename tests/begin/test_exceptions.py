from pathlib import Path

import pytest

from begin import exceptions
from begin.constants import ExitCodeEnum


class TestExceptions:

    def test_exit_code_enum_not_implemented(self):
        """ A class which inherits from `BeginError`, and which
        doesn't implement cls._exit_code_enum, should raise at
        instantiation-time. """
        class StubError(exceptions.BeginError):
            pass

        with pytest.raises(NotImplementedError) as e_info:
            StubError('Some message...')

        assert str(e_info.value) == 'StubError does not implement _exit_code_enum'

    def test_exit_code_enum_has_wrong_type(self):
        """ A class which inherits from `BeginError` should raise if
        cls._exit_code_enum does not have type ExitCodeEnum. """
        class StubError(exceptions.BeginError):
            _exit_code_enum = "this should't be a str"

        with pytest.raises(ValueError) as e_info:
            StubError('Some message...')

        assert str(e_info.value) == 'StubError._exit_code_enum does not have type ExitCodeEnum'

    def test_registry_name_collision_error_properties(self, make_random_string):
        # make_random_string is called with no_whitespace=True to avoid newlines,
        # so that the number of lines in the error message can be counted correctly
        stub_namespaces = [make_random_string(no_whitespace=True) for _ in range(2)]
        stub_paths = [Path(make_random_string(no_whitespace=True)) for _ in range(5)]
        colliding_namespaces = {
            stub_namespaces[0]: stub_paths[:2],
            stub_namespaces[1]: stub_paths[2:],
        }

        err = exceptions.RegistryNameCollisionError(colliding_namespaces)

        # Exception has the correct exit code
        assert err.exit_code == ExitCodeEnum.REGISTRY_NAME_COLLISION.value

        # All namespaces and paths should appear in the error message
        random_strings = stub_namespaces + stub_paths
        assert all(str(s) in err.message for s in random_strings)

        # There should be one block in the message for each namespace
        assert err.message.count('Found multiple registries with name') == len(stub_namespaces)

        # Error message has the correct number of lines
        assert len(err.message.splitlines()) == len(stub_namespaces) + len(stub_paths)

    def test_child_classes_raise_correctly(self):
        # Because metaclasses and inheritance from Exception doesn't play
        # well together (see docstring for exceptions.ExitCodeMeta), we should
        # check that all childclasses retain the ability to raise correctly.
        tested_subclasses = 0

        with pytest.raises(exceptions.RegistryNameCollisionError):
            tested_subclasses += 1
            raise exceptions.RegistryNameCollisionError({})

        # Make the test fail if a new exception is added without an explicit
        # `with pytest.raises ...` check. Note: we can't just look use
        # exceptions.ExitCodeMeta.__sublcasses__ to count the subclasses, because
        # pytest injects TestExceptions
        subclasses = []
        for attribute in dir(exceptions):
            obj = getattr(exceptions, attribute)
            if obj == exceptions.BeginError:
                continue
            elif isinstance(obj, exceptions.ExitCodeMeta):
                subclasses.append(obj)

        assert len(subclasses) == tested_subclasses, 'There are un-tested subclasses of BeginError'
