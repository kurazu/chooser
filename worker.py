import functools
import threading


STOP_WORKER = object()


def worker_handle(item):
    print("Worker handling item", item)


def work(task_queue):
    print("Worker thread started")
    while True:
        priority, item = task_queue.get()
        if item is STOP_WORKER:
            task_queue.task_done()
            print("Worker STOP signal received")
            break
        else:
            worker_handle(item)
            task_queue.task_done()


def create_worker(task_queue):
    callback = functools.partial(work, task_queue)
    return threading.Thread(target=callback)
