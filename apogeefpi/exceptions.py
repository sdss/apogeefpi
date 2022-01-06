# !usr/bin/env python
# -*- coding: utf-8 -*-
#
# Licensed under a 3-clause BSD license.
#
# @Author: Brian Cherinka
# @Date:   2017-12-05 12:01:21
# @Last modified by:   Brian Cherinka
# @Last Modified time: 2017-12-05 12:19:32


class APOGEEFPIError(Exception):
    """A custom core APOGEE FPI exception"""

    def __init__(self, message=None):

        message = "There has been an error" if not message else message

        super(APOGEEFPIError, self).__init__(message)


class APOGEEFPINotImplemented(APOGEEFPIError):
    """A custom exception for not yet implemented features."""

    def __init__(self, message=None):

        message = "This feature is not implemented yet." if not message else message

        super(APOGEEFPINotImplemented, self).__init__(message)


class APOGEEFPIMissingDependency(APOGEEFPIError):
    """A custom exception for missing dependencies."""

    pass


class APOGEEFPIWarning(Warning):
    """Base warning for APOGEEFPI."""


class APOGEEFPIUserWarning(UserWarning, APOGEEFPIWarning):
    """The primary warning class."""

    pass


class APOGEEFPIDeprecationWarning(APOGEEFPIUserWarning):
    """A warning for deprecated features."""

    pass
