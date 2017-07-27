"""
    pyexcel_io.fileformat.tsv
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The lower level tsv file format handler.

    :copyright: (c) 2014-2017 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
import pyexcel_io.constants as constants
from .csvw import CSVBookWriter


class TSVBookWriter(CSVBookWriter):
    """ write tsv """
    def __init__(self):
        CSVBookWriter.__init__(self)
        self._file_type = constants.FILE_FORMAT_TSV

    def open(self, file_name, **keywords):
        keywords['dialect'] = constants.KEYWORD_TSV_DIALECT
        CSVBookWriter.open(self, file_name, **keywords)
