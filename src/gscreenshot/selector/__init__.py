class SelectionError(BaseException):
    pass

class SelectionExecError(SelectionError):
    pass

class SelectionParseError(SelectionError):
    pass

class SelectionCancelled(SelectionError):
    pass
