import functools
import threading
import os.path
import exifread

import gi
gi.require_version('Gdk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
gi.require_version('GLib', '2.0')
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GLib

PRIORITY_LOW = 100
PRIORITY_MEDIUM = 50
PRIORITY_HIGH = 0

STOP_WORKER = object()


def load_pixmap(source_dir, filename):
    screen_width = Gdk.Screen.width()
    screen_height = Gdk.Screen.height()

    path = os.path.join(source_dir, filename)

    with open(path, 'rb') as f:
        tags = exifread.process_file(f)

    orientation = tags.get('Image Orientation')
    orientation = orientation.printable if orientation else None
    if orientation == 'Horizontal (normal)':
        width, height = screen_width, screen_height
        rotation = 0
    elif orientation == 'Rotated 90 CW':
        width, height = screen_height, screen_width
        rotation = 90
    else:
        print('Unrecognizable orientation {}'.format(orientation))
        width, height = screen_width, screen_height
        rotation = 0

    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(path, width, height)
    if rotation:
        pixbuf = pixbuf.rotate_simple(rotation)

    return pixbuf


def notify_window(window, item):
    window.emit('picture-loaded', item)
    return False


def worker_handle(item, window):
    print("Worker handling item", item)
    if item.pixbuf:
        print("Image already loaded")
        return
    print("Loading image", item)
    item.pixbuf = load_pixmap(item.directory, item.filename)
    print("Loaded image", item)
    GLib.idle_add(notify_window, window, item)


def work(task_queue, window):
    print("Worker thread started")
    while True:
        priority, item = task_queue.get()
        if item is STOP_WORKER:
            task_queue.task_done()
            print("Worker STOP signal received")
            break
        else:
            worker_handle(item, window)
            task_queue.task_done()


def create_worker(task_queue, window):
    callback = functools.partial(work, task_queue, window)
    return threading.Thread(target=callback)
