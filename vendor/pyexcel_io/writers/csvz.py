"""
    pyexcel_io.fileformat.csvz
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The lower level csvz file format handler.

    :copyright: (c) 2014-2017 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
import csv
import zipfile

from pyexcel_io._compact import StringIO
from pyexcel_io.book import BookWriter
from pyexcel_io.constants import DEFAULT_SHEET_NAME, FILE_FORMAT_CSVZ

from .csvw import CSVSheetWriter


class CSVZipSheetWriter(CSVSheetWriter):
    """ handle the zipfile interface """
    def __init__(self, zipfile, sheetname, file_extension, **keywords):
        self.file_extension = file_extension
        keywords['single_sheet_in_book'] = False
        CSVSheetWriter.__init__(self, zipfile, sheetname, **keywords)

    def set_sheet_name(self, name):
        self.content = StringIO()
        self.writer = csv.writer(self.content, **self._keywords)

    def close(self):
        file_name = "%s.%s" % (self._native_sheet, self.file_extension)
        self.content.seek(0)
        self._native_book.writestr(file_name, self.content.read())
        self.content.close()


class CSVZipBookWriter(BookWriter):
    """
    csvz writer

    It is better to store csv files as a csvz as it saves your disk space.
    Pyexcel-io had the facility to unzip it for you or you could use
    any other unzip software.
    """
    def __init__(self):
        BookWriter.__init__(self)
        self._file_type = FILE_FORMAT_CSVZ
        self.zipfile = None

    def open(self, file_name, **keywords):
        BookWriter.open(self, file_name, **keywords)
        self.zipfile = zipfile.ZipFile(file_name, 'w', zipfile.ZIP_DEFLATED)

    def create_sheet(self, name):
        given_name = name
        if given_name is None:
            given_name = DEFAULT_SHEET_NAME
        writer = CSVZipSheetWriter(
            self.zipfile,
            given_name,
            self._file_type[:3],
            **self._keywords
        )
        return writer

    def close(self):
        self.zipfile.close()
