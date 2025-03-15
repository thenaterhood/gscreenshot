import io
from gi import require_version

require_version('Gtk', '3.0')
from gi.repository import GLib # type: ignore
from gi.repository import GdkPixbuf # type: ignore


def image_to_pixbuf(image):
    pixbuf = None
    for img_format in [("pnm", "ppm"), ("png", "png"), ("jpeg", "jpeg")]:
        try:
            loader = GdkPixbuf.PixbufLoader()
            descriptor = io.BytesIO()
            image = image.convert("RGB")
            image.save(descriptor, img_format[1])
            contents = descriptor.getvalue()
            descriptor.close()

            loader.write(contents)
            pixbuf = loader.get_pixbuf()
            break
        except GLib.GError:
            continue
        finally:
            try:
                loader.close()
            except GLib.GError:
                pass

    return pixbuf