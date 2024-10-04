'''Exception types for screenshot utilities'''

class NoSupportedScreenshooterError(BaseException):
    '''No supported screenshot utility available'''

    def __init__(self, msg="No supported screenshot backend found", required=None):
        BaseException.__init__(self, msg)
        self.required = required


class ScreenshotError(BaseException):
    '''Generic screenshot error'''
    pass
