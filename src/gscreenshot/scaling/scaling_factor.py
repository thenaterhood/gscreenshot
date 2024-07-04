def get_scaling_factor():
    methods = [
        get_scaling_from_gdk,
        get_scaling_from_qt,
        get_scaling_from_xft_dpi,
    ]
    
    for method in methods:
        try:
            scale = method()
            if scale and abs(scale - 1) > 0.01:  # Check if scale is significantly different from 1
                return scale if scale >= 1 else 1
        except Exception:
            pass
    
    return 1

def get_scaling_from_gdk():
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gdk # type: ignore
    display = Gdk.Display.get_default()
    monitor = display.get_primary_monitor() or display.get_monitor(0)
    if monitor:
        return monitor.get_scale_factor(0)
    return None

def get_scaling_from_xft_dpi():
    import subprocess
    try:
        output = subprocess.check_output(['xrdb', '-query']).decode('utf-8')
        for line in output.split('\n'):
            if line.startswith('Xft.dpi:'):
                dpi = float(line.split(':')[1].strip())
                return dpi / 96  # Assuming 96 DPI as the base
    except Exception:
        return None

def get_scaling_from_qt():
    try:
        from PyQt5.QtWidgets import QApplication # type: ignore
        app = QApplication.instance() or QApplication([])
        screen = app.primaryScreen()
        return screen.devicePixelRatio()
    except ImportError:
        return None
