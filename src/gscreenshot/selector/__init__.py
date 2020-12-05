'''
Classes and exceptions related to screen region selection
'''

class SelectionError(BaseException):
    '''Generic selection error'''

class SelectionExecError(BaseException):
    '''Error executing selector'''

class SelectionParseError(BaseException):
    '''Error parsing selection output'''

class SelectionCancelled(BaseException):
    '''Selection cancelled error'''
