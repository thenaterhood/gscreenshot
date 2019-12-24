import signal
import sys
import gscreenshot.frontend.cli
import gscreenshot.frontend.gtk


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

class FrontendDelegator(object):
    """
    Delegates a gscreenshot call to the correct frontend
    """
    @staticmethod
    def delegate():
        with SignalHandler():
            if (len(sys.argv) > 1) or 'gscreenshot-cli' in sys.argv[0]:
                gscreenshot.frontend.cli.run()
            else:
                gscreenshot.frontend.gtk.main()

def delegate():
    FrontendDelegator.delegate()
