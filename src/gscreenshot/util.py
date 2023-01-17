'''
Misc utility functions for gscreenshot

Functions:
    find_executable(string, string|None) -> string
'''
#pylint: disable=no-else-return, invalid-name
import os
import sys


class GSCapabilities(object):
    '''
    Define capability flags for use in gscreenshot.
    These are used to determine what features gscreenshot
    supports with the selection of utilities available to it.
    These are returned from functions in screenshooters and
    selectors.
    '''

    REGION_SELECTION = "region_selection"
    REUSE_REGION = "reuse_region"
    WINDOW_SELECTION = "window_selection"
    CURSOR_CAPTURE = "cursor_capture"
    ALTERNATE_CURSOR = "alternate_cursor"
    CAPTURE_FULLSCREEN = "capture_full_screen"

# This is a direct copy and paste of distutil.spawn.is_executable.
# We do this so that we don't need to add a dependency on distutils
# for the use of a single simple function.
def find_executable(executable, path=None):
    """Tries to find 'executable' in the directories listed in 'path'.

    A string listing directories separated by 'os.pathsep'; defaults to
    os.environ['PATH'].  Returns the complete filename or None if not found.
    """
    if path is None:
        path = os.environ['PATH']
    paths = path.split(os.pathsep)
    _, ext = os.path.splitext(executable)

    if (sys.platform == 'win32' or os.name == 'os2') and (ext != '.exe'):
        executable = executable + '.exe'

    if not os.path.isfile(executable):
        for p in paths:
            f = os.path.join(p, executable)
            if os.path.isfile(f):
                # the file exists, we have a shot at spawn working
                return f
        return None
    else:
        return executable

def session_is_wayland():
    '''Determines if the session running is wayland'''
    return ('XDG_SESSION_TYPE' in os.environ and
            os.environ['XDG_SESSION_TYPE'].lower() == 'wayland')
