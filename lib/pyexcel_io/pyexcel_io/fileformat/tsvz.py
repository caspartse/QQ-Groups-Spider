"""
    pyexcel_io.fileformat.tsvz
    ~~~~~~~~~~~~~~~~~~~

    The lower level tsvz file format handler.

    :copyright: (c) 2014-2016 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
from ..constants import (
    FILE_FORMAT_TSVZ,
    KEYWORD_TSV_DIALECT
)

from .csvz import CSVZipBookReader, CSVZipBookWriter


class TSVZipBookReader(CSVZipBookReader):

    def __init__(self):
        CSVZipBookReader.__init__(self)
        self.file_type = FILE_FORMAT_TSVZ

    def open(self, file_name, **keywords):
        keywords['dialect'] = KEYWORD_TSV_DIALECT
        CSVZipBookReader.open(self, file_name, **keywords)

    def open_stream(self, file_content, **keywords):
        keywords['dialect'] = KEYWORD_TSV_DIALECT
        CSVZipBookReader.open_stream(self, file_content, **keywords)


class TSVZipBookWriter(CSVZipBookWriter):

    def __init__(self):
        CSVZipBookWriter.__init__(self)
        self.file_type = FILE_FORMAT_TSVZ

    def open(self, file_name, **keywords):
        keywords['dialect'] = KEYWORD_TSV_DIALECT
        CSVZipBookWriter.open(self, file_name, **keywords)


_registry = {
    "file_type": FILE_FORMAT_TSVZ,
    "reader": TSVZipBookReader,
    "writer": TSVZipBookWriter,
    "stream_type": "binary",
    "mime_type": "application/zip",
    "library": "built-in"
}

exports = (_registry,)
