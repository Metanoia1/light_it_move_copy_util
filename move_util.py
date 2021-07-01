import os
import shutil
import threading
from argparse import ArgumentParser


class FileManager(threading.Thread):

    count = 1

    def __init__(self, from_=None, to_=None):
        super().__init__()
        self.__class__.count += 1
        self.from_ = from_
        self.to_ = to_

    def run(self):
        shutil.move(self.from_, self.to_)
        self.__class__.count -= 1

    def __call__(self, from_, to_):
        self.from_ = from_
        self.to_ = to_
        self.start()


def get_thread(threads_amount):
    if FileManager.count < threads_amount:
        return FileManager()
    return shutil.move


def move_files(from_, to_, threads_amount=1):
    thread = get_thread(threads_amount)
    try:
        files_list = os.listdir(from_)
        thread(from_, to_)
        for file_name in files_list:
            move_files(f"{from_}/{file_name}", to_, threads_amount)
    except NotADirectoryError:
        thread(from_, to_)


def main():
    parser = ArgumentParser()
    parser.add_argument("-o", "--operation", help="use with `move` argument")
    parser.add_argument("-f", "--FROM", nargs="*")
    parser.add_argument("-t", "--TO")
    parser.add_argument("-thr", "--threads", type=int)
    args = parser.parse_args()

    if args.operation == "move":
        for arg in args.FROM:
            move_files(arg, args.TO, args.threads)


if __name__ == "__main__":
    main()
