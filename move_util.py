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

    """Interface class for Moving or Copying files utility"""

    def __init__(self, thread_class, func):
        self._thread_class = thread_class
        self._func = func
        self._threads_amount = 1
        self.from_ = None
        self.to_ = None

    @abstractmethod
    def main(self, from_: str, to_: str) -> int:
        """Moving or Copying files logic implementation

        Returns threads amount that was running (int)
        """

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

    def _run_thread(self, from_, to_, thread):
        if isinstance(thread, self._thread_class):
            thread(from_, to_)
            thread.join()
        else:
            thread(from_, to_)

    def main(self, from_: str, to_: str) -> int:
        """Moving files logic implementation method"""
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

        if not self._thread_class.count:
            return 1
        return self._thread_class.count

    def run_main(self, from_: List[str], to_: str, threads_amount=1) -> None:
        self.from_ = from_
        self.to_ = to_
        self._threads_amount = threads_amount
        running_threads_num = None
        for arg in self.from_:
            running_threads_num = self.main(arg, self.to_)
        print("Threads amount that was running at once: ", running_threads_num)


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
