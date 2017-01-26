import multiprocessing
import time
import random
import tqdm

import logging

logging.basicConfig(format='{levelname}: {message}', level=logging.INFO, style='{')
LOG = logging.getLogger()


class Item:
    def __init__(self, number, work):
        self.number = number
        self.work = work
        self.progress = 0


def worker(args):
    item, shared_progress = args
    LOG.debug('Starting work on item {}'.format(item.number))
    for i in range(item.work):
        time.sleep(1)
        shared_progress[item.number] = i + 1
    LOG.debug('Finished work on item {} after {} seconds'.format(item.number, item.work))


def parallel_worker(items):

    total_workload = 0
    for item in items:
        total_workload += item.work
    LOG.debug('Total workload: {}'.format(total_workload))

    with multiprocessing.Pool(processes=3) as pool, multiprocessing.Manager() as manager:

        shared_progress = manager.list([0]*len(items))
        progress_bar = tqdm.tqdm(desc='Downloading', total=total_workload, unit='s')

        LOG.debug('Starting pool of {} workers'.format(pool._processes))
        args = [(item, shared_progress) for item in items]
        result = pool.map_async(worker, args)

        while not result.ready():
            LOG.debug('Progress: {}'.format(shared_progress))
            time.sleep(0.1)
            progress_bar.update(sum(shared_progress) - progress_bar.n)
        progress_bar.close()

    LOG.debug('All workers finished. Result: {}'.format(result.get()))


if __name__ == '__main__':

    work_items = []
    for i in range(6):
        work = random.randint(2, 6)
        work_items.append(Item(i, work))

    parallel_worker(work_items)
