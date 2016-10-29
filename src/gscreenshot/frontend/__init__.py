import signal


class SignalHandler(object):
    """
    Does graceful signal handling
    """
    def __init__(self, quit_method=signal.SIG_DFL):
        self.quit_method = quit_method

    def __enter__(self):
        signal.signal(signal.SIGQUIT, self.quit_method)
        signal.signal(signal.SIGTERM, self.quit_method)
        signal.signal(signal.SIGINT, self.quit_method)

    def __exit__(self, typeof, value, traceback):
        # Ideally this would restore the original
        # signal handlers, but that isn't functionality
        # that's needed right now, so we'll do nothing.
        pass
