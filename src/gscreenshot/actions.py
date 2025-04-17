"""
base class for gscreenshot actions
"""

from abc import ABC, abstractmethod
import gettext
import logging
import subprocess
from typing import Generic, TypeVar

R = TypeVar('R')
_ = gettext.gettext
log = logging.getLogger(__name__)


class GscreenshotAction(ABC, Generic[R]):
    """base screenshot action class"""

    param_class = None

    def __init__(self, **kwargs):
        if self.param_class:
            #pylint:disable=not-callable
            self.params = self.param_class(**kwargs)
        elif len(kwargs) > 0:
            raise GscreenshotActionInvalid

    @abstractmethod
    def execute(self) -> R:
        """run this action"""
        raise NotImplementedError


class NotifyAction(GscreenshotAction[bool]):

    def execute(self) -> bool:
        '''
        Show a notification that a screenshot was taken.
        This method is a "fire-and-forget" and won't
        return a status as to whether it succeeded.
        '''
        try:
            # This has a timeout in case the notification
            # daemon is hanging - don't lock up gscreenshot too
            subprocess.run([
                'notify-send',
                'gscreenshot',
                _('a screenshot was taken from a script or terminal'),
                '--icon',
                'gscreenshot'
            ], check=True, timeout=2)
            return True
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            log.info("notify-send failed: %s", exc)
            return False


class GscreenshotActionError(Exception):
    pass


class GscreenshotActionInvalid(Exception):
    pass
