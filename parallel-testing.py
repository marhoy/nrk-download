import multiprocessing
import time
import random


def worker(item):
    print('Starting working on item', item.number)
    for i in range(item.work):
        time.sleep(1)
        worker.queue.put([item.number, i])
    print('Finished working on item {} after {} seconds'.format(item.number, item.work))


def worker_init(queue):
    worker.queue = queue


class Item:
    def __init__(self, number, work):
        self.number = number
        self.work = work
        self.progress = 0


if __name__ == '__main__':

    work_items = []
    total_workload = 0
    for i in range(6):
        work = random.randint(1, 3)
        work_items.append(Item(i, work))
        total_workload += work

    print('Total workload: ', total_workload)

    print('Starting workers')
    queue = multiprocessing.Queue()
    with multiprocessing.Pool(processes=4, initializer=worker_init, initargs=[queue]) as pool:
        result = pool.map_async(worker, work_items)

        while not result.ready():
            i, progress = queue.get(block=True, timeout=2)
            work_items[i].progress = progress

            total_progress = 0
            for item in work_items:
                total_progress += item.progress
#            time.sleep(1)
            print('Total progress: ', total_progress)
        print(result.get())
    print('All workers finished')
