import multiprocessing
import time
import random


def worker(item):
    print('Starting working on item', item.value)
    number = random.randint(2, 8)
    time.sleep(number)
    item.result = number
    print('Finished working on item', item.value)


class Item:
    def __init__(self, value):
        self.value = value

if __name__ == '__main__':

    items = []
    for i in range(10):
        items.append(Item(i))

    print('Starting workers')
    with multiprocessing.Pool(processes=4) as pool:

        # pool.map(worker, items)
        for item in items:
            result = pool.apply_async(worker, item)
        print('After apply-loop', result)

    print('All workers finished')
