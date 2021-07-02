import os
import shutil
from typing import List
from threading import Thread
from argparse import ArgumentParser
from collections.abc import Callable
from abc import ABCMeta, abstractmethod


class MoveFileThread(Thread):

    count = 0

    def __init__(self, from_=None, to_=None) -> None:
        super().__init__()
        self.__class__.count += 1
        self.from_ = from_
        self.to_ = to_

    def run(self) -> None:
        try:
            shutil.move(self.from_, self.to_)
        except FileNotFoundError:
            pass

        self.__class__.count -= 1

    def __call__(self, from_: str, to_: str) -> None:
        self.from_ = from_
        self.to_ = to_
        self.start()


class FileManager(metaclass=ABCMeta):
    @abstractmethod
    def main(self, from_: str, to_: str) -> None:
        """Move or Copy logic implementation"""

    @abstractmethod
    def run_main(self, from_: List[str], to_: str, threads_amount=1) -> None:
        """The self.main running method"""


class FileMover(FileManager):
    def __init__(self, thread_class: Thread, func: Callable) -> None:
        self.from_ = None
        self.to_ = None
        self._threads_amount = 1
        self._thread_class = thread_class
        self._func = func

    def _get_thread(self) -> Callable:
        threads_running = self._thread_class.count
        threads_amount = self._threads_amount
        if threads_running <= threads_amount and threads_amount != 1:
            return self._thread_class()
        return self._func

    def _run_thread(self, from_: str, to_: str, thread: Thread) -> None:
        if isinstance(thread, self._thread_class):
            thread(from_, to_)
            thread.join()
        else:
            thread(from_, to_)

    def main(self, from_: str, to_: str) -> None:
        thread = self._get_thread()

        try:
            files_list = os.listdir(from_)
            self._run_thread(from_, to_, thread)

            for file_name in files_list:
                try:
                    self.main(f"{self.from_}/{file_name}", self.to_)
                except FileNotFoundError:
                    pass

        except NotADirectoryError:
            self._run_thread(from_, to_, thread)

    def run_main(self, from_: List[str], to_: str, threads_amount=1) -> None:
        self.from_ = from_
        self.to_ = to_
        self._threads_amount = threads_amount
        for arg in self.from_:
            self.main(arg, self.to_)


def get_threads_amount(arg_threads: int) -> int:
    if arg_threads:
        return max(arg_threads, 1)
    return 1


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("-o", "--operation", help="use with `move` argument")
    parser.add_argument("-f", "--FROM", nargs="*")
    parser.add_argument("-t", "--TO")
    parser.add_argument("-thr", "--threads", type=int)
    args = parser.parse_args()
    threads_amount = get_threads_amount(args.threads)

    if args.operation == "move":
        mover = FileMover(MoveFileThread, shutil.move)
        mover.run_main(args.FROM, args.TO, threads_amount)


if __name__ == "__main__":
    main()
