import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


def run_ui(task_queue):
    win = Gtk.Window()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
