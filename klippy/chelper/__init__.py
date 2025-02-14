# Wrapper around C helper code
#
# Copyright (C) 2016-2021  Kevin O'Connor <kevin@koconnor.net>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
from . import ffi_build

if ffi_build.needs_rebuild():
    ffi_build.compile()

from ._ffi import ffi, lib


# Set the
@ffi.callback("void callback(const char *)")
def logging_callback(msg):
    logging.error(ffi.string(msg))


ffi.init_once(
    lambda: lib.set_python_logging_callback(logging_callback),
    "pyhelper_logging",
)


# Return the Foreign Function Interface api to the caller
def get_ffi():
    return (ffi, lib)


__all__ = (
    "ffi",
    "lib",
    "get_ffi",
)
