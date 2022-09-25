'''
Shared utilities for gscreenshot's various frontends
'''
import signal
import sys
import gscreenshot.frontend.cli

try:
    import gscreenshot.frontend.gtk
    GTK_CAPABLE = True
except ValueError:
    GTK_CAPABLE = False


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

def delegate():
    '''Choose the appropriate frontend and run it'''
    if sys.version_info.major < 3 or (sys.version_info.major == 3 and  sys.version_info.minor < 5):
        print(" ==> WARNING: gscreenshot no longer supports Python versions older than Python 3.5")
        print(" ==> WARNING: Please upgrade to Python 3.5 or newer")

    with SignalHandler():
        if (len(sys.argv) > 1) or 'gscreenshot-cli' in sys.argv[0] or not GTK_CAPABLE:
            gscreenshot.frontend.cli.run()
        else:
            gscreenshot.frontend.gtk.main()
