"""
    pyexcel_io._compact
    ~~~~~~~~~~~~~~~~~~~

    Compatibles

    :copyright: (c) 2014-2017 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
# flake8: noqa
# pylint: disable=import-error
# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=ungrouped-imports
# pylint: disable=redefined-variable-type
import sys
import types
import logging

PY2 = sys.version_info[0] == 2
PY3_ABOVE = sys.version_info[0] >= 3
PY26 = PY2 and sys.version_info[1] < 7
PY27 = PY2 and sys.version_info[1] == 7
PY27_ABOVE = PY27 or PY3_ABOVE

if PY26:
    from ordereddict import OrderedDict
else:
    from collections import OrderedDict

try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

if PY2:
    from StringIO import StringIO
    from StringIO import StringIO as BytesIO
    text_type = unicode
    irange = xrange

    class Iterator(object):
        def next(self):
            return type(self).__next__(self)

else:
    from io import StringIO, BytesIO
    text_type = str
    Iterator = object
    irange = range


def isstream(instance):
    """ check if a instance is a stream """
    i_am_not_mmap_obj = True
    if not PY26:
        import mmap
        i_am_not_mmap_obj = not isinstance(instance, mmap.mmap)
    return hasattr(instance, 'read') and i_am_not_mmap_obj


def is_string(atype):
    """find out if a type is str or not"""
    if atype == str:
        return True
    elif PY2:
        if atype == unicode:
            return True
    return False
