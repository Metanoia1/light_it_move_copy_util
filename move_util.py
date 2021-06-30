import shutil
from argparse import ArgumentParser
from threading import Thread


def get_threads_int(threads_arg: int, from_args: list) -> int:
    if not threads_arg or threads_arg < 1:
        return 1
    len_from_args = len(from_args)
    return threads_arg if threads_arg <= len_from_args else len_from_args


def run_move(from_args: list, to_arg: str) -> None:
    print(from_args)
    for arg in from_args:
        shutil.move(arg, to_arg)


def move(from_: list, to: str, threads: int) -> None:
    threads_amount = get_threads_int(threads, from_)
    args_lenght = len(from_) // threads_amount
    step_from = 0
    step_to = args_lenght

    for i in range(threads_amount):

        Thread(target=run_move, args=(from_[step_from:step_to], to)).start()

        step_from += args_lenght
        step_to += args_lenght

        if i + 1 == threads_amount - 1:
            step_to = len(from_)


def main():
    parser = ArgumentParser()
    parser.add_argument("-o", "--operation", help="use with `move` argument")
    parser.add_argument("-f", "--FROM", nargs="*")
    parser.add_argument("-t", "--TO")
    parser.add_argument("-thr", "--threads", type=int)
    args = parser.parse_args()

    if args.operation == "move":
        move(args.FROM, args.TO, args.threads)


if __name__ == "__main__":
    main()
