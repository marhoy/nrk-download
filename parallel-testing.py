import multiprocessing
import time
import random
import tqdm

import logging

logging.basicConfig(format='{levelname}: {message}', level=logging.INFO, style='{')
LOG = logging.getLogger()


def worker(item):
    LOG.debug('Starting working on item {}'.format(item.number))
    for i in range(item.work):
        time.sleep(1)
        queue.put([item.number, i+1])
    LOG.debug('Finished working on item {} after {} seconds'.format(item.number, item.work))


class Item:
    def __init__(self, number, work):
        self.number = number
        self.work = work
        self.progress = 0


if __name__ == '__main__':

    work_items = []
    total_workload = 0
    for i in range(6):
        work = random.randint(2, 6)
        work_items.append(Item(i, work))
        total_workload += work
    LOG.debug('Total workload: {}'.format(total_workload))

    progress_bar = tqdm.tqdm(total=total_workload, unit='s')
    total_progress = 0
    queue = multiprocessing.Queue()
    with multiprocessing.Pool(processes=4) as pool:
        LOG.debug('Starting workers')
        result = pool.map_async(worker, work_items)

        while True:
            try:
                i, progress = queue.get(block=True, timeout=2)
                work_items[i].progress = progress
            except Exception as e:
                LOG.debug('Queue is empty, got {}'.format(e))
                LOG.debug('Result is ready: {}'.format(result.get()))
                break

            previous_progress = total_progress
            total_progress = 0
            for item in work_items:
                total_progress += item.progress
            progress_bar.update(total_progress - previous_progress)
        progress_bar.close()
    print('All workers finished')
