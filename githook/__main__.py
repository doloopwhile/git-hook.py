#!/usr/bin/env python3
from argparse import ArgumentParser
import githook

def install_main(args):
    githook.install_root_hook_script(args.timing)
    githook.install_hook(args.hook, args.timing, args.name)


def uninstall_main(args):
    githook.uninstall_hook(args.timing, args.name)


def list_main(args):
    for timing in githook.timings():
        if args.timing and timing not in args.timing:
            continue
        print(timing + ':')
        for name in githook.hook_names(timing):
            print('  ' + name)


def test_main(args):
    githook.test(args.timing, args.test_args)


def main():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    p = subparsers.add_parser('install')
    p.set_defaults(func=install_main)
    p.add_argument('timing')
    p.add_argument('hook')
    p.add_argument('--name', dest='name')
    p.add_argument('--force')
    p.add_argument('--link')

    p = subparsers.add_parser('uninstall')
    p.set_defaults(func=uninstall_main)
    p.add_argument('timing')
    p.add_argument('name')

    p = subparsers.add_parser('list')
    p.set_defaults(func=list_main)
    p.add_argument('timing', nargs='*')

    p = subparsers.add_parser('test')
    p.set_defaults(func=test_main)
    p.add_argument('timing')
    p.add_argument('test_args', nargs='*')

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
