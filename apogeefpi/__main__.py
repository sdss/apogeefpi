#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-01-06
# @Filename: __main__.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import asyncio
import os
import signal
from contextlib import suppress

import click
from click_default_group import DefaultGroup

from clu.tools import cli_coro
from sdsstools.daemonizer import DaemonGroup

from apogeefpi.actor import APOGEEFPIActor


async def shutdown(signal, loop, actor):
    """Cancel tasks, including run_forever()."""

    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]

    with suppress(asyncio.CancelledError):
        await asyncio.gather(*tasks)


@click.group(cls=DefaultGroup, default="actor", default_if_no_args=True)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Debug mode. Use additional v for more details.",
)
@click.pass_context
def apogeefpi(ctx, verbose):
    """APOGEE FPI CLI."""

    ctx.obj = {"verbose": verbose}


@apogeefpi.group(cls=DaemonGroup, prog="apogeefpi_actor", workdir=os.getcwd())
@click.pass_context
@cli_coro
async def actor(ctx):
    """Runs the actor."""

    config_file = os.path.join(os.path.dirname(__file__), "etc/apogeefpi.yml")

    apogeefpi_actor = APOGEEFPIActor.from_config(config_file)

    loop = asyncio.get_event_loop()
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s,
            lambda s=s: asyncio.create_task(shutdown(s, loop, apogeefpi_actor)),
        )

    try:
        await apogeefpi_actor.start()
        await apogeefpi_actor.run_forever()
    except asyncio.CancelledError:
        pass
    finally:
        await apogeefpi_actor.stop()
        loop.stop()


if __name__ == "__main__":
    apogeefpi()
