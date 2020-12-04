'''
Classes and exceptions related to screen region selection
'''

class SelectionError(BaseException):
    '''Generic selection error'''

class SelectionExecError(SelectionError):
    '''Error executing selector'''

class SelectionParseError(SelectionError):
    '''Error parsing selection output'''

class SelectionCancelled(SelectionError):
    '''Selection cancelled error'''
