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
    pass


def create_ui(task_queue):
    win = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
    win.connect("delete-event", Gtk.main_quit)
    win.connect("key-press-event", on_keypress)

    win.show()
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
