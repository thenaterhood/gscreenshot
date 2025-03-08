
from dataclasses import asdict, dataclass
import gettext
import json
import logging
import os


_ = gettext.gettext
log = logging.getLogger(__name__)


class CacheException(Exception):
    pass


@dataclass
class GscreenshotCache():
    """
    Cache for misc gscreenshot data between sessions

    If adding to this cache class, please ensure all your
    additional fields either have a default value or are marked
    as optional
    """

    last_save_dir: str = os.path.expanduser("~")
    """Last directory gscreenshot saved a screenshot to"""

    def write(self) -> bool:
        """Writes the cache to disk"""
        try:
            with open(GscreenshotCache.get_cache_path(), "w", encoding="UTF-8") as cachefile:
                json.dump(asdict(self), cachefile)
                log.debug("wrote cache file '%s'", GscreenshotCache.get_cache_path())
                return True
        except FileNotFoundError:
            log.warning(_("unable to save cache file - file not found"))

        return False

    def update_values(self, write=False, **kwargs) -> bool:
        """
        Convenience method to update values in the cache.
        Raises an exception if you try to update an unknown field.

        You can also update the values by setting the class
        properties directly, then call write to save to disk.
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise CacheException(f"invalid cache attribute: '{key}'")

        if write:
            return self.write()

        return True

    @staticmethod
    def load() -> "GscreenshotCache":
        """Write the cache data to disk"""
        cache = GscreenshotCache()

        if os.path.isfile(GscreenshotCache.get_cache_path()):
            with open(GscreenshotCache.get_cache_path(), "r", encoding="UTF-8") as cachefile:
                try:
                    cache = GscreenshotCache(**json.load(cachefile))
                except (json.JSONDecodeError, TypeError) as exc:
                    log.warning(exc)
                    cache.write()
        else:
            cache.write()

        return cache

    @staticmethod
    def get_cache_path() -> str:
        """
        Find the gscreenshot cache file and return its path
        """
        if 'XDG_CACHE_HOME' in os.environ:
            return os.environ['XDG_CACHE_HOME'] + "/gscreenshot"
        return os.path.expanduser("~/.gscreenshot")
