#!/usr/bin/env python2.7
from __future__ import unicode_literals
import os
import os.path
import sys
import shutil
import functools

import pygtk
pygtk.require('2.0')
import gtk
import gobject

import exifread


TITLE = 'Chooser'

IMAGE_EXTENSIONS = {'.jpg', '.jpeg'}

TARGET_DIR_NAME = 'selected'


def read_images(source_dir):
    images = []
    for filename in os.listdir(source_dir):
        _, ext = os.path.splitext(filename)
        lowercase_ext = ext.lower()
        if not lowercase_ext in IMAGE_EXTENSIONS:
            # Skip non-images.
            continue
        images.append(filename)
    images.sort()
    return images


def file_op(create_target_dir=True, go_next=True):
    def file_op_decorator(func):
        @functools.wraps(func)
        def wrapper(self):
            if self.busy:
                return
            if create_target_dir and not os.path.exists(self.target_dir):
                os.mkdir(self.target_dir)
            filename = self.images[self.image_idx % len(self.images)]
            source_path = os.path.join(self.source_dir, filename)
            target_path = os.path.join(self.target_dir, filename)
            func(self, source_path, target_path)
            if go_next:
                self.next()
        return wrapper
    return file_op_decorator


class cyclist(list):

    def __getitem__(self, idx):
        return super(cyclist, self).__getitem__(idx % len(self))


class Chooser(gtk.Window):

    def __init__(self, source_dir, target_dir):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        black = gtk.gdk.color_parse("black")
        self.modify_bg(gtk.STATE_NORMAL, black)
        self.busy = 0
        self.screen_width = gtk.gdk.screen_width()
        self.screen_height = gtk.gdk.screen_height()
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.images = self.load_images()
        self.set_title(TITLE)
        self.image = gtk.Image()
        self.pixbufs = self.load_buffers()
        self.image_idx = 0
        self.image.set_from_pixbuf(self.pixbufs[0])
        self.image.show()

        self.add(self.image)
        self.show()
        self.fullscreen()

        self.connect_keys()

        self.connect("delete_event", self.on_delete_event)
        self.connect("destroy", self.on_destroy)
        self.connect("key-press-event", self.on_key_press_event)

    def on_key_press_event(self, widget, event):
        if event.keyval == gtk.keysyms.Right:
            self.next()
            return gtk.TRUE
        elif event.keyval == gtk.keysyms.Left:
            self.prev()
            return gtk.TRUE
        else:
            return gtk.FALSE

    def load_images(self):
        images = read_images(self.source_dir)
        if not images:
            placeholder_path = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                'no-image-found.jpg'
            )
            images = [placeholder_path]
        return cyclist(images)

    def load_buffers(self):
        buffers = {
            -1: self.load_pixmap(self.images[-1]),
            0: self.load_pixmap(self.images[0]),
            1: self.load_pixmap(self.images[1])
        }
        return buffers

    def on_delete_event(self, widget, event, data=None):
        return False

    def on_destroy(self, widget, data=None):
        gtk.main_quit()

    def add_key_handler(self, key, callback):
        def full_callback(accel_group, acceleratable, keyval, modifier):
            callback()
        key, mod = gtk.accelerator_parse(key)
        self.accel_group.connect_group(
            key, mod, gtk.ACCEL_VISIBLE, full_callback)

    def connect_keys(self):
        self.accel_group = gtk.AccelGroup()
        self.add_key_handler('Escape', self.quit)
        self.add_key_handler('space', self.next)
        self.add_key_handler('Right', self.right)
        self.add_key_handler('Left', self.left)
        self.add_key_handler('Up', self.up)
        self.add_key_handler('BackSpace', self.prev)
        self.add_key_handler('d', self.delete_image)
        self.add_key_handler('c', self.copy_image)
        self.add_key_handler('l', self.link_image)
        self.accel_group.lock()
        self.add_accel_group(self.accel_group)

    def up(self):
        print 'UP'

    def left(self):
        print 'LEFT'

    def right(self):
        print 'RIGHT'

    def quit(self):
        gtk.main_quit()

    def load_pixmap(self, filename):
        path = os.path.join(self.source_dir, filename)

        with open(path, 'rb') as f:
            tags = exifread.process_file(f)

        orientation = tags.get('Image Orientation')
        orientation = orientation.printable if orientation else None
        if orientation == 'Horizontal (normal)':
            width, height = self.screen_width, self.screen_height
            rotation = 0
        elif orientation == 'Rotated 90 CW':
            width, height = self.screen_height, self.screen_width
            rotation = 90
        else:
            print('Unrecognizable orientation {}'.format(orientation))
            width, height = self.screen_width, self.screen_height
            rotation = 0

        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, width, height)
        if rotation:
            pixbuf = pixbuf.rotate_simple(rotation)

        return pixbuf

    def next(self):
        if self.busy:
            return
        self.image.set_from_pixbuf(self.pixbufs[1])
        self.pixbufs[-1] = self.pixbufs[0]
        self.pixbufs[0] = self.pixbufs[1]
        self.image_idx += 1
        self.schedule_load(
            self.images[self.image_idx + 1],
            1
        )

    def schedule_load(self, filename, idx):
        self.busy += 1

        def callback():
            pixmap = self.load_pixmap(filename)
            self.pixbufs[idx] = pixmap
            self.busy -= 1
            return gtk.FALSE

        gobject.idle_add(callback)

    def prev(self):
        if self.busy:
            return
        self.image.set_from_pixbuf(self.pixbufs[-1])
        self.pixbufs[1] = self.pixbufs[0]
        self.pixbufs[0] = self.pixbufs[-1]
        self.image_idx -= 1
        self.schedule_load(
            self.images[self.image_idx - 1],
            -1
        )

    @file_op(create_target_dir=False)
    def delete_image(self, source_path, target_path):
        os.unlink(source_path)
        # TODO actually remove from watched images

    @file_op()
    def copy_image(self, source_path, target_path):
        shutil.copyfile(source_path, target_path)

    @file_op()
    def link_image(self, source_path, target_path):
        os.symlink(source_path, target_path)


def main(orig_dir):
    orig_dir = os.path.expanduser(orig_dir)
    if os.path.isfile(orig_dir):
        orig_dir = os.path.dirname(orig_dir)

    target_dir = os.path.join(orig_dir, TARGET_DIR_NAME)
    assert os.path.isdir(orig_dir), '{} is not a dir'.format(orig_dir)

    Chooser(orig_dir, target_dir)

    gtk.main()


if __name__ == '__main__':
    main(*sys.argv[1:])
