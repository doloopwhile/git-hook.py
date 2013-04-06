#!/usr/bin/env python3
import sys
import os
import re
import shutil
import io
from subprocess import (
    check_output,
    check_call,
    CalledProcessError,
)
from os.path import (
    join,
    abspath,
    relpath,
    basename,
    dirname,
    isfile,
)
from urllib.parse import urlparse
from urllib.request import urlretrieve
import posixpath
from abc import (
    ABCMeta,
    abstractmethod
)

from allfiles import allfiles

def timings():
    return '''
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

ROOT_HOOK_TEMPLATE = '''\
#!/bin/sh
python3 -m "githook.do_hook" {timing} "$@"
'''


class HookParseError(ValueError):
  def __init__(self, hook_class, hook_str):
    super().__init__(self, hook_class, hook_str)
    self._hook_class = hook_class
    self._hook_str = hook_str


class AbstractHook(metaclass=ABCMeta):
  @abstractmethod
  def parse(cls, arg_hook): pass

  @abstractmethod
  def name(self): pass

  @abstractmethod
  def install(self, dest_dir): pass


class AbstractWebHook(AbstractHook):
  @abstractmethod
  def _url(self): pass

  def install(self, dest):
    urlretrieve(self._url(), dest)


class GistHook(AbstractWebHook):
  def __init__(self, number):
    super().__init__(self)
    self._number = number

  @classmethod
  def parse(cls, hook_str):
    m = re.match(r'gist:(\d+)', hook_str, re.I)
    if m is None:
      raise HookParseError(cls, hook_str)
    return cls(int(m.group(1)))

  def name(self):
    return "gist-{}".format(self._number)

  def _url(self):
    return "https://raw.github.com/gist/{}".format(self._number)


class UrlHook(AbstractWebHook):
  def __init__(self, url):
    super().__init__()
    self._url_str = url

  @classmethod
  def parse(cls, hook_str):
    m = re.match(r'http://|https://', hook_str, re.I)
    if m is None:
      raise HookParseError(cls, hook_str)
    return cls(hook_str)

  def name(self):
    return posixpath.basename(urlparse(self._url()).path)

  def _url(self):
    return self._url_str


class FileHook(AbstractHook):
  def __init__(self, path):
    super().__init__()
    self._path = path

  @classmethod
  def parse(cls, arg_hook):
    return cls(arg_hook)

  def name(self):
    return basename(self._path)

  def install(self, dest):
    os.makedirs(dirname(dest), 0o755, True)
    shutil.copy2(self._path, dest)


def parse_hook_str(hook_str):
  for klass in [GistHook, UrlHook]:
    try:
      return klass.parse(hook_str)
    except HookParseError:
      pass
  return FileHook.parse(hook_str)


def git_dir():
    output = check_output(['git', 'rev-parse', '--git-dir'])
    path = output.decode(sys.getfilesystemencoding()).strip()
    return abspath(path)


def all_hook_dirs():
    return [(timing, hook_dir(timing)) for timing in timings()]


def hook_dir(timing):
    return join(git_dir(), 'hooks', 'installed', timing)


def root_hook_script(timing):
    return join(git_dir(), 'hooks', timing)


def install_root_hook_script(timing):
    path = root_hook_script(timing)
    if isfile(path):
        return

    code = ROOT_HOOK_TEMPLATE.format(timing=timing)
    with io.open(path, 'w', encoding='ascii') as fp:
        fp.write(code)
    os.chmod(path, 0o755)


def install_hook(hook_str, timing, name=None):
    hook = parse_hook_str(hook_str)
    if name is None:
        name = hook.name()
    hook.install(join(hook_dir(timing), name))


def hook_names(timing):
    d = hook_dir(timing)
    for f in allfiles(d):
        yield relpath(f, d)

def hook_executables(timing):
    return allfiles(hook_dir(timing))


def uninstall_hook(timing, name):
    path = join(hook_dir(timing), name)
    os.remove(path)


def test(timing, args):
    cmd = [root_hook_script(timing)] + args
    try:
        check_call(cmd)
    except CalledProcessError as e:
        sys.exit(e.returncode)

