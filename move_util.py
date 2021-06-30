import os
import shutil
import threading
from argparse import ArgumentParser
from threading import Thread


class FileManager(Thread):

    count = 0

    def __init__(self, from_, to_):
        super().__init__()
        self.__class__.count += 1
        self.from_ = from_
        self.to_ = to_

    def run(self):
        try:
            shutil.move(self.from_, self.to_)
        except FileNotFoundError:
            pass
        self.__class__.count -= 1


def get_threads_int(threads_arg: int, from_args: list) -> int:
    if not threads_arg or threads_arg < 1:
        return 1
    len_from_args = len(from_args)
    return threads_arg if threads_arg <= len_from_args else len_from_args


def move_files(from_, to_, threads_amount=1):
    print(threading.active_count())
    thread = FileManager(from_, to_)
    files_list = []

    try:
        files_list = os.listdir(from_)
        thread.start()
    except NotADirectoryError:
        thread.start()

    for file_name in files_list:
        move_files(f"{from_}/{file_name}", to_, threads_amount)


def main():
    parser = ArgumentParser()
    parser.add_argument("-o", "--operation", help="use with `move` argument")
    parser.add_argument("-f", "--FROM", nargs="*")
    parser.add_argument("-t", "--TO")
    parser.add_argument("-thr", "--threads", type=int)
    args = parser.parse_args()
    threads_amount = get_threads_int(args.threads, args.FROM)

    if args.operation == "move":
        for arg in args.FROM:
            move_files(arg, args.TO, threads_amount)


if __name__ == "__main__":
    main()
