import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk
from gi.repository import Gdk


KEY_ACTIONS = {
    Gdk.KEY_Escape: Gtk.main_quit
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


def run_ui(task_queue):
    screen_width = Gdk.Screen.width()
    screen_height = Gdk.Screen.height()

    win = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
    win.connect("delete-event", Gtk.main_quit)
    win.connect("key-press-event", on_keypress)

    win.show()
    win.fullscreen()

    Gtk.main()
