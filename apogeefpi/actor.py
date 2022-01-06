#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-01-06
# @Filename: actor.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import pathlib
import re

import clu
from clu import Command
from clu.parsers.click import command_parser as apogeefpi_parser

from apogeefpi import __version__
from apogeefpi.tools import CalledProcessError, subprocess_run_async


CommandType = Command["APOGEEFPIActor"]

REGEX = re.compile(r"Apogeefpi says \"message\:shutters\:(high1|low1)\:ok\"")


class APOGEEFPIActor(clu.LegacyActor):
    """The APOGEE FPI SDSS-style actor."""

    def __init__(self, *args, **kwargs):

        schema = pathlib.Path(__file__).parent / "etc/schema.json"
        super().__init__(*args, version=__version__, schema=schema, **kwargs)

        self.shutter_position: str = "?"

    async def start(self, *args, **kwargs):

        await super().start(*args, **kwargs)

        self.write("i", message={"shutter_position": "?"})


@apogeefpi_parser.command()
async def status(command: CommandType):
    """Reports the assumed position of the FPI shutter."""

    command.finish(shutter_position=command.actor.shutter_position)


@apogeefpi_parser.command()
async def open(command: CommandType):
    """Opens the FPI shutter."""

    match = await _process_shutter_command(command, "fpiopenshutter")

    if match is False:
        return
    else:
        if match == "high1":
            return command.finish(shutter_position="open")
        else:
            command.warning("Shutter returned unexpected closed status.")
            return command.finish(shutter_position="closed")


@apogeefpi_parser.command()
async def close(command: CommandType):
    """Closes the FPI shutter."""

    match = await _process_shutter_command(command, "fpicloseshutter")

    if match is False:
        return
    else:
        if match == "low1":
            return command.finish(shutter_position="closed")
        else:
            command.warning("Shutter returned unexpected open status.")
            return command.finish(shutter_position="open")


async def _process_shutter_command(command: CommandType, shutter_command: str):

    try:
        stdout = await subprocess_run_async(shutter_command, shell=True)
    except CalledProcessError as err:
        command.error(
            "Open shutter failed with error code "
            f"{err.returncode}: {err.stderr.decode()}"
        )
        command.fail(shutter_position="?")
        return False

    stdout_clean = stdout.strip().replace('"', "")
    command.debug(f"APOGEE FPI replied with: {stdout_clean}")

    if (match := REGEX.match(stdout)) is None:
        command.error("Cannot parse shutter reply.")
        command.fail(shutter_position="?")
        return False
    else:
        return match.group(1)
