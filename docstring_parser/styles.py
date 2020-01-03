"""Style enum declaration."""

import enum

from . import google, rest

try:
    from . import numpy
except ImportError as _e:
    numpy = _e
have_numpy = not isinstance(numpy, Exception)


class Style(enum.Enum):
    rest = enum.auto()
    google = enum.auto()
    auto = enum.auto()
    if have_numpy:
        numpy = enum.auto()


STYLES = {Style.rest: rest.parse, Style.google: google.parse}
if have_numpy:
    STYLES[Style.numpy] = numpy.parse
