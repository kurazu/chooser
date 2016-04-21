#!/usr/bin/env python3.4
import os.path
import sys
import queue
import signal

import worker
import ui
import model

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk


def run(directory, current_file):
    print("Running in dir", directory, 'with file', current_file)

    pictures = model.build_model(directory, current_file)
    print("Loaded pictures", pictures)

    current_pic = pictures.current
    surrounding_pics = pictures.surrounding
    print("Current pic", current_pic)
    print("Surrounding pics", surrounding_pics)

    task_queue = queue.PriorityQueue()

    if current_pic:
        task_queue.put((worker.PRIORITY_HIGH, current_pic))
    for pic in surrounding_pics:
        task_queue.put((worker.PRIORITY_MEDIUM, pic))

    win = ui.create_ui(task_queue, pictures)

    worker_thread = worker.create_worker(task_queue, win)
    worker_thread.start()

    Gtk.main()
    print("UI finished. Stopping worker thread.")
    task_queue.put((worker.PRIORITY_LOW, worker.STOP_WORKER))
    print("Wating for worker thread to finish processing.")
    task_queue.join()
    print("Good bye!")


def main(file_name):
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    assert file_name, "No input file/directory"
    file_name = os.path.expanduser(file_name)
    file_name = os.path.normpath(file_name)
    if os.path.isdir(file_name):
        directory = file_name
        current_file = None
    else:
        directory = os.path.dirname(file_name)
        assert os.path.isdir(directory), "Not a directory"
        current_file = os.path.basename(file_name)
    run(directory, current_file)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
