"""
    pyexcel_io
    ~~~~~~~~~~~~~~~~~~~

    Uniform interface for reading/writing different excel file formats

    :copyright: (c) 2014-2017 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
import logging
from ._compact import NullHandler
logging.getLogger(__name__).addHandler(NullHandler())  # noqa

from .io import get_data, iget_data, save_data  # noqa
import pyexcel_io.plugins as plugins


BLACK_LIST = [__name__, 'pyexcel_webio', 'pyexcel_text']
WHITE_LIST = [
    'pyexcel_io.readers',
    'pyexcel_io.writers',
    'pyexcel_io.database']
PREFIX = 'pyexcel_'

plugins.load_plugins(PREFIX, __path__, BLACK_LIST, WHITE_LIST)
