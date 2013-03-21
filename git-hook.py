#!/usr/bin/env python3
import sys
from argparse import ArgumentParser
from subprocess import check_output
from allfiles import allfiles
from os.path import (
    join,
    abspath,
    relpath,
)

TIMING_LIST = '''
    applypatch-msg
    pre-applypatch
    post-applypatch
    pre-commit
    prepare-commit-msg
    commit-msg
    post-commit
    pre-rebase
    post-checkout
    post-merge
    pre-receive
    update
    post-update
    pre-auto-gc
    post-rewrite
'''.split()

def git_dir():
    output = check_output(['git', 'rev-parse', '--git-dir'])
    path = output.decode(sys.getfilesystemencoding()).strip()
    return abspath(path)

def hook_dirs():
    installed = join(git_dir(), 'hook', 'installed')
    dirs = {}
    for t in TIMING_LIST:
        dirs[t] = join(installed, t)
    return dirs

def hook_name(hook):


def install_http_to(url, dest, args):
    urlretrieve(url, dest)

def install_gist_to(number, dest, args):
    url = "https://raw.github.com/gist/{}".format(number)
    urlretrieve(url, dest)

def install_file_to(path, dest, args):
    shutil.copy2(path, dest)

Hook = namedtuple('Hook', 'name')
def parse_hook_arg(arg_hook):
    m = re.match(r'gist:(\d+)', arg_hook, re.I)
    if m is not None:
        n=int(m.group(1))
        return Hook(
            name="gist-{}".format(n),
            install_to=partial(install_gist_to, n),
        )

    m = re.match(r'http://|https://', arg_hook, re.I)
    if m is not None:
        return Hook(
            name=unixpath.basename(urlparse(m).path),
            install_to=partial(install_http_to, arg_hook),
        )

    return Hook(
        name=
        install_to
    )


def install_main(args):
    dirs = hook_dirs()
    d = dirs[args.timing]

    hook = parse_hook_arg(args.hook)

    if args.name is not None:
        name = args.name
    else:
        name = hook.name

    hook.install_to(join(d, name), args)


def uninstall_main(args):
    print('uninstall')

def list_main(args):
    dirs = hook_dirs()
    for t, d in dirs.items():
        print("{}:".format(t))
        for f in allfiles(t):
            print('  ' + relpath(f, d))

def main():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    p = subparsers.add_parser('install')
    p.set_defaults(func=install_main)
    p.add_argument('timing')
    p.add_argument('hook')
    p.add_argument('name')
    p.add_argument('--force')
    p.add_argument('--link')

    p = subparsers.add_parser('uninstall')
    p.set_defaults(func=uninstall_main)
    p.add_argument('timing')
    p.add_argument('name')

    p = subparsers.add_parser('list')
    p.set_defaults(func=list_main)
    p.add_argument('--timing')

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
