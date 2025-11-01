#pylint: disable=wrong-import-order
#pylint: disable=wrong-import-position
#pylint: disable=ungrouped-imports
import typing
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk # type: ignore


class ListWithActions(Gtk.Box):
    def __init__(self, label_text, store, remove_handler, add_handler=None, entry_placeholder=""):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.set_property("margin", 10)
        self.store = store
        self.add_handler = add_handler
        self.remove_handler = remove_handler

        self.treeview = Gtk.TreeView(model=self.store)
        self.treeview.set_size_request(200, 150)

        # Name
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(label_text, renderer, text=0)
        column.set_expand(True)
        self.treeview.append_column(column)

        # Actions
        icon_renderer = Gtk.CellRendererPixbuf()
        icon_renderer.set_property("icon-name", "edit-delete")
        icon_column = Gtk.TreeViewColumn("", icon_renderer)
        self.treeview.append_column(icon_column)
        self.treeview.connect("button-press-event", self._on_icon_clicked)

        scroll_window = Gtk.ScrolledWindow()
        scroll_window.set_vexpand(True)
        scroll_window.add(self.treeview)
        self.pack_start(scroll_window, True, True, 5)

        if add_handler:
            self.entry = Gtk.Entry()
            self.entry.set_placeholder_text(entry_placeholder)
            self.pack_start(self.entry, False, False, 5)

            add_button = Gtk.Button(
                label=f"Add {label_text[:-1] if label_text.endswith('s') else label_text}",
            )
            add_button.connect("clicked", add_handler)
            self.pack_start(add_button, False, False, 5)

    def _on_icon_clicked(self, treeview, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            x = int(event.x)
            y = int(event.y)
            path_info = treeview.get_path_at_pos(x, y)
            if path_info is not None:
                path, column, _cell_x, _cell_y = path_info
                # icon column is the last column
                if treeview.get_columns().index(column) == 1:
                    self.remove_handler(self, path)
        return False


class SettingsDialog(Gtk.Dialog):
    def __init__(self, stored_regions: dict, on_delete_region: typing.Callable):
        super().__init__(title="Gscreenshot Settings")

        self.on_delete_region = on_delete_region
        self.set_default_size(500, 300)

        self.main_box = self.get_content_area()

        self.region_store = Gtk.ListStore(str)
        for region_name in stored_regions.keys():
            self.region_store.append((region_name,))

        self.region_box = ListWithActions(
            label_text="Saved Regions",
            store=self.region_store,
            remove_handler=self.on_region_icon_clicked,
        )

        self.main_box.pack_start(self.region_box, True, True, 0)
        self.main_box.show_all()

    def on_region_icon_clicked(self, _widget, path):
        liststore_iter = self.region_store.get_iter(path)
        region_name = self.region_store.get_value(liststore_iter, 0)
        self.on_delete_region(region_name)
        if liststore_iter:
            self.region_store.remove(liststore_iter)
