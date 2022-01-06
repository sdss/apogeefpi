#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-01-06
# @Filename: tools.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import asyncio
from subprocess import CalledProcessError


__all__ = ["subprocess_run_async"]


async def subprocess_run_async(*args, shell: bool = False):
    """Runs a command asynchronously.

    If ``shell=True`` the command will be executed through the shell. In that case
    the argument must be a single string with the full command. Otherwise, must receive
    a list of program arguments. Returns the output of stdout.
    """

    if shell:
        cmd = await asyncio.create_subprocess_shell(
            args[0],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        cmd_str = args[0]

    else:
        cmd = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        cmd_str = " ".join(args)

    stdout, stderr = await cmd.communicate()
    if cmd.returncode and cmd.returncode > 0:
        raise CalledProcessError(
            cmd.returncode,
            cmd=cmd_str,
            output=stdout,
            stderr=stderr,
        )

    if stdout:
        return stdout.decode()
    else:
        return ""
