import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GObject', '2.0')

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject


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


class PictureWindow(Gtk.Window):

    KEY_ACTIONS = {
        Gdk.KEY_Escape: 'quit',
        Gdk.KEY_space: 'go_to_next',
        Gdk.KEY_Right: 'go_to_next',
        Gdk.KEY_Left: 'go_to_prev'
    }

    FAVOURITE_CHAR = '\u2605'
    NOT_FAVOURITE_CHAR = '\u2606'
    LOADING_TEXT = 'Loading...'
    EMPTY_TEXT = 'No pictures'

    def __init__(self, task_queue, pictures):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.task_queue = task_queue
        self.pictures = pictures

        self.connect("delete-event", Gtk.main_quit)
        self.connect("key-press-event", self.on_keypress)

        self.overlay = Gtk.Overlay()
        self.image = Gtk.Image()
        self.overlay.add(self.image)

        self.star_label = Gtk.Label(self.NOT_FAVOURITE_CHAR)
        self.star_label.set_name('star')

        self.filename_label = Gtk.Label("FILENAME")
        self.filename_label.set_name('filename')

        self.hbox = Gtk.HBox()
        self.hbox.add(self.star_label)
        self.hbox.add(self.filename_label)

        self.hbox.props.valign = Gtk.Align.START
        self.hbox.props.halign = Gtk.Align.START
        self.overlay.add_overlay(self.hbox)

        self.loading_label = Gtk.Label(self.LOADING_TEXT)
        self.loading_label.set_name('loading')
        self.loading_label.props.valign = Gtk.Align.CENTER
        self.loading_label.props.halign = Gtk.Align.CENTER
        self.overlay.add_overlay(self.loading_label)

        self.add(self.overlay)

        self.show_all()
        self.fullscreen()

        GObject.signal_new(
            'picture-loaded',
            self,
            GObject.SignalFlags.RUN_LAST,
            GObject.TYPE_PYOBJECT,
            (GObject.TYPE_PYOBJECT, )
        )

        self.connect('picture-loaded', self.on_picture_loaded)

    def quit(self):
        Gtk.main_quit()

    def on_keypress(self, widget, event, data=None):
        keyval = event.keyval
        try:
            callback_name = self.KEY_ACTIONS[keyval]
        except KeyError:
            return False

        callback = getattr(self, callback_name)
        callback()
        return True

    def go_to_next(self):
        pass

    def go_to_prev(self):
        pass

    def on_picture_loaded(self, window, picture):
        print("UI notified about image", picture, "loaded")
        self.refresh_ui()

    def refresh_ui(self):
        current = self.pictures.current
        if current is None:
            self.show_empty()
        else:
            self.show_picture(current)

    def show_empty(self):
        self.filename_label.set_text("")
        self.star_label.set_text("")
        self.loading_label.set_visible(True)
        self.loading_label.set_text(self.EMPTY_TEXT)
        self.image.set_from_pixbuf(None)

    def show_picture(self, current):
        self.filename_label.set_text(current.filename)
        self.star_label.set_text(
            self.FAVOURITE_CHAR
            if current.favourite else
            self.NOT_FAVOURITE_CHAR
        )
        if current.pixbuf:
            self.loading_label.set_visible(False)
            self.image.set_from_pixbuf(current.pixbuf)
        else:
            self.loading_label.set_visible(True)
            self.loading_label.set_text(self.LOADING_TEXT)
            self.image.set_from_pixbuf(None)


def create_ui(task_queue, pictures):
    style_provider = Gtk.CssProvider()
    assert style_provider.load_from_data(STYLE_DATA)
    Gtk.StyleContext.add_provider_for_screen(
         Gdk.Screen.get_default(),
         style_provider,
         Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    win = PictureWindow(task_queue, pictures)
    win.refresh_ui()

    return win
