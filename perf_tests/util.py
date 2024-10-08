import time

from pytest_order.sorter import Sorter


class TimedSorter(Sorter):
    elapsed = 0.0
    nr_marks = 1000

    def sort_items(self):
        self.__class__.elapsed = 0.0
        start_time = time.time()
        items = super().sort_items()
        self.__class__.elapsed = (time.time() - start_time) / self.nr_marks * 1000
        print(f"\nTime per test: {self.__class__.elapsed:.3f} ms")
        return items
