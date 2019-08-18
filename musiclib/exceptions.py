class CommandError(Exception):
    pass

class RequiresYtdlError(Exception):
    pass

class UnexpectedValueError(Exception):
    def __init__(self, variable, value, context=None):
        if context:
            super().__init__(f'unexpected value for {variable}: {value}. Context: {context}')
        else:
            super().__init__(f'unexpected value for {variable}: {value}')