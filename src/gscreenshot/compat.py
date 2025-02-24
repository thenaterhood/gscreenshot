"""
Compatibility functions
"""
import warnings

try:
    from importlib.resources import as_file, files
except ImportError:
    from pkg_resources import resource_string, resource_filename


try:
    from importlib.metadata import version
except ImportError:
    from pkg_resources import require


def get_resource_file(resource: str, filename: str):
    """Compatibility function until pkg_resources is fully removed"""
    # pylint: disable=missing-parentheses-for-call-in-test
    if as_file and files:
        with as_file(files(resource).joinpath(filename)) as fpath:
            return fpath

    # pylint: disable=used-before-assignment
    return resource_filename(resource, filename)


def get_resource_string(resource: str, filename: str):
    """Compatibility function until pkg_resources is fully removed"""
    # pylint: disable=missing-parentheses-for-call-in-test
    if as_file and files:
        return files(resource).joinpath(filename).read_text(encoding="UTF-8")

    # pylint: disable=used-before-assignment
    return resource_string(resource, filename).decode("UTF-8")


def get_version():
    """Compatibility function until pkg_resources is fully removed"""
    # pylint: disable=missing-parentheses-for-call-in-test,using-constant-test
    if version:
        return version("gscreenshot")

    # pylint: disable=used-before-assignment
    return require("gscreenshot")[0].version


def deprecated(message):
    """Compatibility function for python < 3.13"""
    def deprecated_decorator(func):
        def deprecated_func(*args, **kwargs):
            warnings.warn(f"{func.__name__} is a deprecated function. {message}",
                category=DeprecationWarning,
                stacklevel=2)
            warnings.simplefilter('default', DeprecationWarning)
            return func(*args, **kwargs)
        return deprecated_func
    return deprecated_decorator
