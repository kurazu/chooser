import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GObject', '2.0')

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject



def go_to_next():
    pass


def go_to_prev():
    pass


KEY_ACTIONS = {
    Gdk.KEY_Escape: Gtk.main_quit,
    Gdk.KEY_space: go_to_next,
    Gdk.KEY_Right: go_to_next,
    Gdk.KEY_Left: go_to_prev
}


def on_keypress(widget, event, data=None):
    keyval = event.keyval
    try:
        callback = KEY_ACTIONS[keyval]
    except KeyError:
        return False
    else:
        callback()
        return True


def on_picture_loaded(window, picture):
    print("UI notified about image", picture, "loaded")
    pass


STYLE_DATA = b"""
GtkLabel {
    color: black;
    text-shadow: 1px 1px 2px white, -1px -1px 2px white, 1px -1px 2px white, -1px 1px 2px white;
    padding: 2px;
}

GtkLabel#star {
    color: yellow;
    text-shadow: 1px 1px 2px black, -1px -1px 2px black, 1px -1px 2px black, -1px 1px 2px black;
}

GtkWindow {
    background: black;
}
"""


def create_ui(task_queue):
    style_provider = Gtk.CssProvider()
    assert style_provider.load_from_data(STYLE_DATA)
    Gtk.StyleContext.add_provider_for_screen(
         Gdk.Screen.get_default(),
         style_provider,
         Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    win = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)

    win.connect("delete-event", Gtk.main_quit)
    win.connect("key-press-event", on_keypress)

    overlay = Gtk.Overlay()
    image = Gtk.Image()
    overlay.add(image)

    star_label = Gtk.Label("\u2605\u2606")
    star_label.set_name('star')

    filename_label = Gtk.Label("FILENAME")
    filename_label.set_name('filename')

    hbox = Gtk.HBox()
    hbox.add(star_label)
    hbox.add(filename_label)

    hbox.props.valign = Gtk.Align.START
    hbox.props.halign = Gtk.Align.START
    overlay.add_overlay(hbox)

    loading_label = Gtk.Label("Loading...")
    loading_label.set_name('loading')
    loading_label.props.valign = Gtk.Align.CENTER
    loading_label.props.halign = Gtk.Align.CENTER
    overlay.add_overlay(loading_label)

    win.add(overlay)

    win.show_all()
    win.fullscreen()

    GObject.signal_new(
        'picture-loaded',
        win,
        GObject.SignalFlags.RUN_LAST,
        GObject.TYPE_PYOBJECT,
        (GObject.TYPE_PYOBJECT, )
    )

    win.connect('picture-loaded', on_picture_loaded)

    return win
