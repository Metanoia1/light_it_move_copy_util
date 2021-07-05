"""Moving files command-line utility"""
import os
import shutil
from typing import List
from threading import Thread
from argparse import ArgumentParser
from abc import ABCMeta, abstractmethod


class MovingFilesThread(Thread):

    """This class implements moving files thread"""

    count = 0

    def __init__(self, from_=None, to_=None) -> None:
        super().__init__()
        self.from_ = from_
        self.to_ = to_

    def run(self) -> None:
        self.__class__.count += 1
        try:
            shutil.move(self.from_, self.to_)
            self.__class__.count -= 1
        except FileNotFoundError:
            self.__class__.count -= 1

    def __call__(self, from_: str, to_: str) -> None:
        self.from_ = from_
        self.to_ = to_
        self.start()


class FileManager(metaclass=ABCMeta):

    """Interface class for Moving or Copying files utility"""

    def __init__(self, thread_class, func):
        self._thread_class = thread_class
        self._func = func
        self._threads_amount = 1
        self.from_ = None

    @abstractmethod
    def main(self, from_: str, to_: str) -> None:
        """Moving or Copying files logic implementation"""

    @abstractmethod
    def run_main(self, from_: List[str], to_: str, threads_amount=1) -> None:
        """The self.main running method"""


class FileMover(FileManager):

    """This class implements moving files logic"""

    def _get_thread(self):
        threads_running = self._thread_class.count
        threads_amount = self._threads_amount
        if threads_running < threads_amount and threads_amount != 1:
            return self._thread_class()
        return self._func

    def main(self, from_: str, to_: str) -> None:
        """Moving files logic implementation method"""
        thread = self._get_thread()

        try:
            files_list = os.listdir(from_)
            thread(from_, to_)

            for file_name in files_list:
                try:
                    self.main(f"{self.from_}/{file_name}", to_)
                except FileNotFoundError:
                    pass

        except NotADirectoryError:
            thread(from_, to_)

    def run_main(self, from_: List[str], to_: str, threads_amount=1) -> None:
        self.from_ = from_
        self._threads_amount = threads_amount
        for arg in from_:
            self.main(arg, to_)


def get_threads_amount(arg_threads: int) -> int:
    """Returns threads amount number"""
    if arg_threads:
        return max(arg_threads, 1)
    return 1


def main() -> None:
    """Parses the arguments from the command line and runs this utility"""
    parser = ArgumentParser()
    parser.add_argument("-o", "--operation", help="use with `move` argument")
    parser.add_argument("-f", "--FROM", nargs="*", help="path `from`")
    parser.add_argument("-t", "--TO", help="path `to`")
    parser.add_argument("-thr", "--threads", type=int, help="threads amount")
    args = parser.parse_args()
    threads_amount = get_threads_amount(args.threads)

    if args.operation == "move":
        mover = FileMover(MovingFilesThread, shutil.move)
        mover.run_main(args.FROM, args.TO, threads_amount)


if __name__ == "__main__":
    main()
