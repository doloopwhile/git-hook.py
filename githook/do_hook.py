#!/usr/bin/env python3
import githook
from subprocess import (
    check_call,
    CalledProcessError,
)
from argparse import ArgumentParser

def main():
    parser = ArgumentParser()
    parser.add_argument('timing')
    parser.add_argument('arg', nargs='*')
    args = parser.parse_args()

    for executable in githook.hook_executables(args.timing):
        cmd = [executable] + args.arg
        try:
            check_call(cmd)
        except CalledProcessError as e:
            sys.exit(e.returncode)

if __name__ == '__main__':
    main()



