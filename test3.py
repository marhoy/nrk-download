import multiprocessing
import time
import random


def worker(item, queue):
    print('Starting working on item', item.number, queue)
    for i in range(item.work):
#        queue.put(item.number, i)
        time.sleep(1)
    print('Finished working on item {} after {} seconds'.format(item.number, item.work))


class Item:
    def __init__(self, number, work):
        self.number = number
        self.work = work
        self.progess = 0


if __name__ == '__main__':

    work_items = []
    total_workload = 0
    for i in range(6):
        work = random.randint(5, 10)
        work_items.append(Item(i, work))
        total_workload += work

    print('Total workload: ', total_workload)

    print('Starting workers')
    queue = multiprocessing.Queue()
    with multiprocessing.Pool(processes=4) as pool:
        result = pool.map_async(worker, (work_items, 2))

        while not result.ready():
#            item, progress = queue.get()
#            work_items[item].progress = progress

            total_progress = 0
            for item in work_items:
                total_progress += item.progess
            time.sleep(1)
            print('Total progress: ', total_progress)
        print(result.get())
    print('All workers finished')
