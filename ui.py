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


def create_ui(task_queue):
    win = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)

    win.connect("delete-event", Gtk.main_quit)
    win.connect("key-press-event", on_keypress)

    #black = Gdk.RGBA(0, 0, 0)
    #win.override_background_color(Gtk.StateFlags.NORMAL, black)

    overlay = Gtk.Overlay()
    image = Gtk.Image()
    overlay.add(image)

    label = Gtk.Label("\u2605\u2606 FILENAME")
    label.props.valign = Gtk.Align.START
    label.props.halign = Gtk.Align.START
    overlay.add_overlay(label)

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
