"""
    pyexcel_io.fileformat.csvz
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The lower level csvz file format handler.

    :copyright: (c) 2014-2017 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
import zipfile

from pyexcel_io._compact import StringIO, PY2
from pyexcel_io.book import BookReader
from pyexcel_io.constants import FILE_FORMAT_CSVZ

from .csvr import (
    CSVinMemoryReader,
    NamedContent
)


class CSVZipBookReader(BookReader):
    """csvz reader

    Read zipped csv file that was zipped up by pyexcel-io. It support
    single csv file and multiple csv files.
    """
    def __init__(self):
        BookReader.__init__(self)
        self._file_type = FILE_FORMAT_CSVZ
        self.zipfile = None

    def open(self, file_name, **keywords):
        BookReader.open(self, file_name, **keywords)
        self._native_book = self._load_from_file_alike_object(self._file_name)

    def open_stream(self, file_stream, **keywords):
        BookReader.open_stream(self, file_stream, **keywords)
        self._native_book = self._load_from_file_alike_object(
            self._file_stream)

    def read_sheet(self, native_sheet):
        content = self.zipfile.read(native_sheet.payload)
        if PY2:
            sheet = StringIO(content)
        else:
            sheet = StringIO(content.decode('utf-8'))

        reader = CSVinMemoryReader(
            NamedContent(
                native_sheet.name,
                sheet
            ),
            **self._keywords
        )
        return reader.to_array()

    def close(self):
        if self.zipfile:
            self.zipfile.close()

    def _load_from_file_alike_object(self, file_alike_object):
        try:
            self.zipfile = zipfile.ZipFile(file_alike_object, 'r')
            sheets = [NamedContent(_get_sheet_name(name), name)
                      for name in self.zipfile.namelist()]
            return sheets
        except zipfile.BadZipfile:
            print("StringIO instance was passed by any chance?")
            raise


def _get_sheet_name(filename):
    len_of_a_dot = 1
    len_of_csv_word = 3
    name_len = len(filename) - len_of_a_dot - len_of_csv_word
    return filename[:name_len]
