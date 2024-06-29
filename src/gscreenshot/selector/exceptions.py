class SelectionError(BaseException):
    '''Generic selection error'''

class SelectionExecError(BaseException):
    '''Error executing selector'''

class SelectionParseError(BaseException):
    '''Error parsing selection output'''

class SelectionCancelled(BaseException):
    '''Selection cancelled error'''

class NoSupportedSelectorError(BaseException):
    '''No region selection tool available'''
