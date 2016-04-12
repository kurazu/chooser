#!/usr/bin/env python3.4
import os.path
import sys
import queue

import worker
import ui


task_queue = queue.PriorityQueue()
worker_thread = worker.create_worker(task_queue)


def run(directory):
    print("Running in", directory)
    worker_thread.start()

    task_queue.put((0, 7))

    ui.run_ui(task_queue)
    print("UI finished. Stopping worker thread.")
    task_queue.put((100, worker.STOP_WORKER))
    print("Wating for worker thread to finish processing.")
    task_queue.join()
    print("Good bye!")


def main(file_name):
    assert file_name, "No input file"
    file_name = os.path.expanduser(file_name)
    file_name = os.path.normpath(file_name)
    if os.path.isdir(file_name):
        directory = file_name
    else:
        directory = os.path.dirname(file_name)
        assert os.path.isdir(directory), "Not a directory"
    run(directory)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
