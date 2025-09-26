'''
Shared utilities for gscreenshot's various frontends
'''
import logging
import logging.config
import signal
import sys
from gscreenshot.frontend import cli
from gscreenshot.frontend import gtk
from .cli.args import get_args


log = logging.getLogger(__name__)


try:
    import gscreenshot.frontend.presenter
    GTK_CAPABLE = True
except ValueError:
    GTK_CAPABLE = False


class SignalHandler():
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
        args = get_args()

        class GscreenshotLogFilter(logging.Filter):
            '''Gscreenshot log filter'''
            def filter(self, record):
                if "-vvv" in sys.argv:
                    return True
                return 'gscreenshot' in record.pathname

        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
                },
            },
            'filters': {
                'global_filter': {
                    '()': GscreenshotLogFilter,
                }
            },
            'handlers': {
                'default': {
                    'level': 'DEBUG',
                    'formatter': 'standard',
                    'class': 'logging.StreamHandler',
                    'filters': ['global_filter']
                },
            },
            'loggers': {
                '': {  # root logger
                    'handlers': ['default'],
                    'level': args.log_level,
                    'propagate': True
                }
            }
        }
        logging.config.dictConfig(logging_config)

        app = gscreenshot.frontend.cli.main()

        if args.gui and GTK_CAPABLE:
            gtk.main(app)
        elif (len(sys.argv) > 1) or 'gscreenshot-cli' in sys.argv[0] or not GTK_CAPABLE:
            gscreenshot.frontend.cli.resume(app)
        else:
            gtk.main(app)
