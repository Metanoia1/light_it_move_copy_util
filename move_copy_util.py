"""Moving or Copying files command-line utility"""
import os
import shutil
import threading
import logging
from typing import List
from argparse import ArgumentParser
from abc import ABCMeta, abstractmethod


logging.basicConfig(filename="logs.log", level=logging.DEBUG)


class MovingCopyingThread(threading.Thread):

    """This class implements moving or copying files thread"""

    def __init__(self, func, from_=None, to_=None) -> None:
        super().__init__()
        self._func = func
        self.from_ = from_
        self.to_ = to_

    def run(self) -> None:
        try:
            logging.info("[%s] %s", threading.active_count(), self.from_)
            self._func(self.from_, self.to_)
        except FileNotFoundError:
            pass

    def __call__(self, from_: str, to_: str) -> None:
        self.from_ = from_
        self.to_ = to_
        self.start()


class FileManagerInterface(metaclass=ABCMeta):

    """Interface class for Moving or Copying files utility"""

    def __init__(self, thread_class, func):
        self._thread_class = thread_class
        self._func = func
        self._threads_amount = 1

    @abstractmethod
    def main(self, from_: str, to_: str, init_to_value: str) -> None:
        """Moving or Copying files logic implementation"""

    @abstractmethod
    def run_main(
        self, from_: List[str], to_: str, threads_amount=1, operation=None
    ) -> None:
        """The self.main running method"""


class FileManager(FileManagerInterface):

    """Moving or Copying files logic implementation class"""

    def _get_thread(self):
        if self._threads_amount <= 1:
            return self._func

        if threading.active_count() < self._threads_amount:
            return self._thread_class(self._func)

        return None

    def main(self, from_: str, to_: str, init_to_value: str) -> None:
        thread = self._get_thread()
        while not thread:
            thread = self._get_thread()

        try:
            files_list = os.listdir(from_)
            to_ = f"{init_to_value}/{from_[from_.find('/'):]}"

            try:
                os.makedirs(to_)
            except FileExistsError:
                pass

            for file_name in files_list:
                try:
                    self.main(f"{from_}/{file_name}", to_, init_to_value)
                except FileNotFoundError:
                    pass

        except NotADirectoryError:
            thread(from_, to_)

    def run_main(
        self, from_: List[str], to_: str, threads_amount=1, operation=None
    ) -> None:
        self._threads_amount = threads_amount

        try:
            os.makedirs(to_)
        except FileExistsError:
            pass

        for arg in from_:
            self.main(arg, to_, to_)

        if operation == "move":
            for arg in from_:
                try:
                    shutil.rmtree(arg)
                except (NotADirectoryError, FileNotFoundError):
                    pass


def _get_threads_amount(arg_threads: int) -> int:
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
    threads_amount = _get_threads_amount(args.threads)
    operation = args.operation

    if operation == "move":
        mover = FileManager(MovingCopyingThread, shutil.move)
        mover.run_main(args.FROM, args.TO, threads_amount, operation)
    elif operation == "copy":
        copier = FileManager(MovingCopyingThread, shutil.copy)
        copier.run_main(args.FROM, args.TO, threads_amount, operation)


if __name__ == "__main__":
    main()
