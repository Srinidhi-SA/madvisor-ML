class BIException(Exception):
    """
    Utility class for creating custom exceptions

        static method naming convention: "componentName_errorDescription"
    """

    @staticmethod
    def dataframe_invalid():
        err_msg = 'Invalid DataFrame'
        return BIException(err_msg)

    @staticmethod
    def column_does_not_exist(column_name):
        err_msg = 'Column, %s, is not present in the dataframe' % (column_name,)
        return BIException(err_msg)

    @staticmethod
    def non_numeric_column(column_name):
        err_msg = 'Column, %s, is non numeric' %(column_name,)
        return BIException(err_msg)

    @staticmethod
    def non_string_column(column_name):
        err_msg = 'Column, %s, is not a string column' %(column_name,)
        raise BIException(err_msg)

    @staticmethod
    def parameter_invalid_type(param_name, expected_type, actual_type):
        err_msg = 'Parameter, %s, expecting %s but got %s' % (param_name, expected_type, actual_type)
        return BIException(err_msg)

    @staticmethod
    def parameter_has_negative_value(param_name, param_value):
        err_msg = 'Parameter, %s, has negative value, %f' % (param_name, param_value)
        return BIException(err_msg)
