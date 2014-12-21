#!/usr/bin/env python2.7
from __future__ import unicode_literals
import os.path
import sys

import pygtk
pygtk.require('2.0')
import gtk
import gobject

import exifread


TITLE = 'Chooser'

IMAGE_EXTENSIONS = {'.jpg', '.jpeg'}


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

    def load_images(self):
        images = read_images(self.source_dir)
        assert len(images) > 3, u'NO IMAGES'
        return images

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
        # self.add_key_handler('Right', self.next)
        # self.add_key_handler('Left', self.prev)
        self.add_key_handler('BackSpace', self.prev)
        self.add_key_handler('d', self.delete_image)
        self.add_key_handler('c', self.copy_image)
        self.add_key_handler('l', self.link_image)
        self.accel_group.lock()
        self.add_accel_group(self.accel_group)

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
            self.images[(self.image_idx + 1) % len(self.images)],
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
            self.images[(self.image_idx - 1) % len(self.images)],
            -1
        )

    def delete_image(self):
        if self.busy:
            return
        print 'DELETE'

    def copy_image(self):
        if self.busy:
            return
        print 'COPY'
        self.notify('COPY')

    def link_image(self):
        if self.busy:
            return
        #target_path = os.path.join(self.target_dir, '')

    def notify(self, msg):
        pass


def main(orig_dir, target_dir):
    if os.path.isfile(orig_dir):
        orig_dir = os.path.basename(orig_dir)
    assert os.path.isdir(orig_dir)
    assert os.path.isdir(target_dir)

    Chooser(orig_dir, target_dir)

    # fixed = gtk.Fixed()
    # fixed.set_size_request(400, 400)
    # fixed.put(image, 0, 0)
    # fixed.show()

    gtk.main()


if __name__ == '__main__':
    main(*sys.argv[1:])
