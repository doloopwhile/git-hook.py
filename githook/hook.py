#!/usr/bin/env python3
import sys
from os.path basename
import githook
from subprocess import (
    check_call,
    CalledProcessError
)

timing = basename(sys.argv[0])
for hook_script in githook.hook_scripts(timing):
    cmd = [hook_script] + sys.argv[1:]
    try:
        check_call(cmd)
    except CalledProcessError:
        sys.exit(1)
