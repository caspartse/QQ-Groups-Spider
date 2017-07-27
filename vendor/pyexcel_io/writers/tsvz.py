"""
    pyexcel_io.fileformat.tsvz
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    The lower level tsvz file format handler.

    :copyright: (c) 2014-2017 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
from pyexcel_io.constants import (
    FILE_FORMAT_TSVZ,
    KEYWORD_TSV_DIALECT
)

from .csvz import CSVZipBookWriter


class TSVZipBookWriter(CSVZipBookWriter):
    """ write zipped tsv file

    It is similiar to CSVZipBookWriter, but support tab separated values
    """
    def __init__(self):
        CSVZipBookWriter.__init__(self)
        self._file_type = FILE_FORMAT_TSVZ

    def open(self, file_name, **keywords):
        keywords['dialect'] = KEYWORD_TSV_DIALECT
        CSVZipBookWriter.open(self, file_name, **keywords)
