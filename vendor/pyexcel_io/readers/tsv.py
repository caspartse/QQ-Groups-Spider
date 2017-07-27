"""
    pyexcel_io.readers.tsv
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The lower level tsv file format handler.

    :copyright: (c) 2014-2017 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
import pyexcel_io.constants as constants
from .csvr import CSVBookReader


class TSVBookReader(CSVBookReader):
    """ Read tab separated values """
    def __init__(self):
        CSVBookReader.__init__(self)
        self._file_type = constants.FILE_FORMAT_TSV

    def open(self, file_name, **keywords):
        keywords['dialect'] = constants.KEYWORD_TSV_DIALECT
        CSVBookReader.open(self, file_name, **keywords)

    def open_stream(self, file_content, **keywords):
        keywords['dialect'] = constants.KEYWORD_TSV_DIALECT
        CSVBookReader.open_stream(self, file_content, **keywords)
