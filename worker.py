import collections
import functools
import threading
import os.path
import tempfile
import shutil

import exifread

import gi
gi.require_version('Gdk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
gi.require_version('GLib', '2.0')
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GLib

import model


PRIORITY_LOW = 200
PRIORITY_MEDIUM = 100
PRIORITY_HIGH = 50
PRIORITY_VERY_HIGH = 0

WorkerTask = collections.namedtuple(
    'WorkerTask', ('priority', 'argument')
)


class StopTask(WorkerTask):

    def __new__(cls):
        return WorkerTask.__new__(cls, PRIORITY_LOW, None)

    def process(self, window):
        raise StopIteration()


class LoadPixmapTask(WorkerTask):

    PRIORITY = PRIORITY_HIGH

    def __new__(cls, pic):
        return WorkerTask.__new__(cls, cls.PRIORITY, pic)

    def notify_window(self, window, item):
        window.emit('picture-loaded', item)
        return False

    def process(self, window):
        item = self.argument
        print("Worker handling item", item)
        if item.pixbuf:
            print("Image already loaded")
            return
        print("Loading image", item)
        item.pixbuf = self.load_pixmap(item.file_path)
        print("Loaded image", item)
        GLib.idle_add(self.notify_window, window, item)

    @staticmethod
    def load_pixmap(path):
        screen_width = Gdk.Screen.width()
        screen_height = Gdk.Screen.height()

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


class LoadCurrentPixmapTask(LoadPixmapTask):

    PRIORITY = PRIORITY_VERY_HIGH


class CopyPicsTask(WorkerTask):

    def __new__(cls, pics):
        return WorkerTask.__new__(cls, PRIORITY_MEDIUM, pics)

    def process(self, window):
        pics = self.argument
        target_directory = tempfile.mkdtemp('', 'pictures')
        print('Created target directory', target_directory)
        for pic in pics:
            in_path = pic.file_path
            out_path = shutil.copy2(in_path, target_directory)
            print('Copied', in_path, 'to', out_path)
        print('Copy finished')


class ScalePicsTask(WorkerTask):

    def __new__(cls, pics):
        return WorkerTask.__new__(cls, PRIORITY_MEDIUM, pics)

    def process(self, window):
        pass


def work(task_queue, window):
    print("Worker thread started")
    while True:
        task = task_queue.get()
        assert isinstance(task, WorkerTask)

        try:
            task.process(window)
        except StopIteration:
            break
        finally:
            task_queue.task_done()


def create_worker(task_queue, window):
    callback = functools.partial(work, task_queue, window)
    return threading.Thread(target=callback)
