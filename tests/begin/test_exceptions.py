import pytest

from begin import exceptions


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
