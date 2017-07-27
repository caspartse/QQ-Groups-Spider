"""
    pyexcel_io.writers.csvw
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The lower level csv file format writer

    :copyright: (c) 2014-2017 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
import csv
import codecs

from pyexcel_io.book import BookWriter
from pyexcel_io.sheet import SheetWriter
import pyexcel_io._compact as compact
import pyexcel_io.constants as constants


class UnicodeWriter(object):
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, file_handle, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = compact.StringIO()
        self.writer = csv.writer(self.queue, **kwds)
        self.stream = file_handle
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        """ write row into the csv file """
        self.writer.writerow([compact.text_type(s).encode("utf-8")
                              for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        """ write multiple rows into csv file """
        for row in rows:
            self.writerow(row)


class CSVSheetWriter(SheetWriter):
    """
    csv file writer

    """
    def __init__(self, filename, name,
                 encoding="utf-8", single_sheet_in_book=False,
                 sheet_index=None, **keywords):
        self._encoding = encoding
        self._sheet_name = name
        self._single_sheet_in_book = single_sheet_in_book
        self.__line_terminator = constants.DEFAULT_CSV_NEWLINE
        if constants.KEYWORD_LINE_TERMINATOR in keywords:
            self.__line_terminator = keywords.get(
                constants.KEYWORD_LINE_TERMINATOR)
        if single_sheet_in_book:
            self._sheet_name = None
        self._sheet_index = sheet_index
        self.writer = None
        self.file_handle = None
        SheetWriter.__init__(
            self, filename, self._sheet_name, self._sheet_name,
            **keywords)

    def write_row(self, array):
        """
        write a row into the file
        """
        self.writer.writerow(array)


class CSVFileWriter(CSVSheetWriter):
    """ Write csv to a physical file """
    def close(self):
        self.file_handle.close()

    def set_sheet_name(self, name):
        if name != constants.DEFAULT_SHEET_NAME:
            names = self._native_book.split(".")
            file_name = "%s%s%s%s%s.%s" % (
                names[0],
                constants.DEFAULT_MULTI_CSV_SEPARATOR,
                name,              # sheet name
                constants.DEFAULT_MULTI_CSV_SEPARATOR,
                self._sheet_index,  # sheet index
                names[1])
        else:
            file_name = self._native_book
        if compact.PY2:
            self.file_handle = open(file_name, "wb")
            self.writer = UnicodeWriter(self.file_handle,
                                        encoding=self._encoding,
                                        **self._keywords)
        else:
            self.file_handle = open(file_name, "w", newline="",
                                    encoding=self._encoding)
            self.writer = csv.writer(self.file_handle, **self._keywords)


class CSVMemoryWriter(CSVSheetWriter):
    """ Write csv to a memory stream """
    def __init__(self, filename, name,
                 encoding="utf-8", single_sheet_in_book=False,
                 sheet_index=None, **keywords):
        CSVSheetWriter.__init__(self, filename, name,
                                encoding=encoding,
                                single_sheet_in_book=single_sheet_in_book,
                                sheet_index=sheet_index, **keywords)

    def set_sheet_name(self, name):
        if compact.PY2:
            self.file_handle = self._native_book
            self.writer = UnicodeWriter(self.file_handle,
                                        encoding=self._encoding,
                                        **self._keywords)
        else:
            self.file_handle = self._native_book
            self.writer = csv.writer(self.file_handle, **self._keywords)
        if not self._single_sheet_in_book:
            self.writer.writerow(
                [constants.DEFAULT_CSV_STREAM_FILE_FORMATTER % (
                    self._sheet_name, "")]
            )

    def close(self):
        if self._single_sheet_in_book:
            #  on purpose, the this is not done
            #  because the io stream can be used later
            pass
        else:
            self.writer.writerow(
                [constants.SEPARATOR_FORMATTER % ""])


class CSVBookWriter(BookWriter):
    """ write csv with unicode support """
    def __init__(self):
        BookWriter.__init__(self)
        self._file_type = constants.FILE_FORMAT_CSV
        self.__index = 0

    def create_sheet(self, name):
        writer_class = None
        if compact.is_string(type(self._file_alike_object)):
            writer_class = CSVFileWriter
        else:
            writer_class = CSVMemoryWriter
        writer = writer_class(
            self._file_alike_object,
            name,
            sheet_index=self.__index,
            **self._keywords)
        self.__index = self.__index + 1
        return writer
