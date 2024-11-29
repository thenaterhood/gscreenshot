"""Functions to handle scaled displays"""

import os
import typing

from gscreenshot.util import session_is_wayland


def get_scaling() -> typing.Tuple[str, float]:
    """Get the scaling method and factor"""
    methods = [
        get_scaling_from_env,
        get_scaling_from_xft_dpi,
        get_scaling_from_gtk,
        get_scaling_from_qt,
    ]

    if session_is_wayland():
        methods = [
            get_scaling_from_env,
            get_scaling_from_wlr_randr,
            get_scaling_from_xft_dpi,  # Technically for X, but works with an X bridge
            get_scaling_from_gtk,
            get_scaling_from_qt,
        ]

    for method in methods:
        try:
            scaling = method()

            if scaling:
                name, scale = scaling
                if scale and abs(scale - 1) > 0.01:  # Check if scale is significantly different from 1
                    return name, scale if scale >= 1 else 1
        # pylint: disable=bare-except
        except:
            pass

    return "None", 1


def get_scaling_method_name() -> str:
    """Get the name of the method used to find the scaling factor"""
    return get_scaling()[0]


def get_scaling_factor() -> float:
    """Get the scaling factor for the display"""

    return get_scaling()[1]


def get_scaling_from_env() -> typing.Optional[typing.Tuple[str, float]]:

    gdk_scale = os.environ.get("GDK_SCALE")
    if gdk_scale:
        try:
            return "GDK_SCALE", float(gdk_scale)
        except:
            pass

    qt_scale = os.environ.get("QT_SCALE_FACTOR")
    if qt_scale:
        try:
            return "QT_SCALE_FACTOR", float(qt_scale)
        except:
            pass

    return None


def get_scaling_from_gtk() -> typing.Optional[typing.Tuple[str, float]]:
    """Get scaling factor from Gtk"""
    # pylint: disable=import-outside-toplevel
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk # type: ignore

    window = Gtk.Window()
    screen = window.get_screen()
    display = screen.get_display()
    monitor = (
        display.get_monitor_at_window(screen.get_root_window())
        or display.get_primary_monitor()
        or display.get_monitor(0)
    )
    if monitor:
        return "GTK", monitor.get_scale_factor()
    return None


def get_scaling_from_wlr_randr() -> typing.Optional[typing.Tuple[str, float]]:
    import subprocess
    try:
        output = subprocess.check_output(['wlr-randr'], text=True)
        for line in output.splitlines():
            if 'current' in line and 'scale' in line:
                return "wlr-randr", float(line.split('scale')[1].strip())
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        return None


def get_scaling_from_xft_dpi() -> typing.Optional[typing.Tuple[str, float]]:
    """Get scaling factor from xrdb"""
    # pylint: disable=import-outside-toplevel
    import subprocess
    try:
        output = subprocess.check_output(['xrdb', '-query']).decode('utf-8')
        for line in output.split('\n'):
            if line.startswith('Xft.dpi:'):
                dpi = float(line.split(':')[1].strip())
                return "xrdb", dpi / 96  # Assuming 96 DPI as the base
    except subprocess.CalledProcessError:
        return None

    return None


def get_scaling_from_qt() -> typing.Optional[typing.Tuple[str, float]]:
    """Get scaling factor from Qt"""
    try:
        # pylint: disable=import-outside-toplevel
        from PyQt5.QtWidgets import QApplication # type: ignore
        app = QApplication.instance() or QApplication([])
        screen = app.primaryScreen()
        return "Qt", screen.devicePixelRatio()
    except ImportError:
        return None
