"""
base class for screenshot actions
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, Optional, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from gscreenshot.screenshot import Screenshot

R = TypeVar('R')

@dataclass
class ParamClass():
    pass


class ScreenshotAction(ABC, Generic[R]):
    """base screenshot action class"""

    param_class: Any = None

    def __init__(self, **kwargs):
        if self.param_class:
            #pylint:disable=not-callable
            self.params = self.param_class(**kwargs)
        elif len(kwargs) > 0:
            raise ScreenshotActionInvalid

    @abstractmethod
    def execute(self, screenshot: Optional["Screenshot"]) -> R:
        """run this action on the provided screenshot"""
        raise NotImplementedError


class ScreenshotActionError(Exception):
    pass

class ScreenshotActionInvalid(Exception):
    pass
