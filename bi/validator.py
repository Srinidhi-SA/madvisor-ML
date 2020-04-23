from bi.common.exception import BIException


class Validator:
    """
    Utilitiy class for common validations
    """

    @staticmethod
    def assert_non_negative_parameter(param_type, param_name, param_value, raise_exception=True):
        if type(param_value) != param_type:
            if raise_exception:
                raise BIException.parameter_invalid_type(param_name, param_type, type(param_value))
            else:
                return False

        if param_value < 0:
            if raise_exception:
                raise BIException.parameter_has_negative_value(param_name, param_value)
            else:
                return False

        return True
