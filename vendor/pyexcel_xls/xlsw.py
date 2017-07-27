"""
    pyexcel_xlsw
    ~~~~~~~~~~~~~~~~~~~

    The lower level xls file format handler using xlwt

    :copyright: (c) 2016-2017 by Onni Software Ltd
    :license: New BSD License
"""
import datetime
import xlrd
from xlwt import Workbook, XFStyle

from pyexcel_io.book import BookWriter
from pyexcel_io.sheet import SheetWriter


DEFAULT_DATE_FORMAT = "DD/MM/YY"
DEFAULT_TIME_FORMAT = "HH:MM:SS"
DEFAULT_DATETIME_FORMAT = "%s %s" % (DEFAULT_DATE_FORMAT, DEFAULT_TIME_FORMAT)


class XLSheetWriter(SheetWriter):
    """
    xls sheet writer
    """
    def set_sheet_name(self, name):
        """Create a sheet
        """
        self._native_sheet = self._native_book.add_sheet(name)
        self.current_row = 0

    def write_row(self, array):
        """
        write a row into the file
        """
        for i, value in enumerate(array):
            style = None
            tmp_array = []
            if isinstance(value, datetime.datetime):
                tmp_array = [
                    value.year, value.month, value.day,
                    value.hour, value.minute, value.second
                ]
                value = xlrd.xldate.xldate_from_datetime_tuple(tmp_array, 0)
                style = XFStyle()
                style.num_format_str = DEFAULT_DATETIME_FORMAT
            elif isinstance(value, datetime.date):
                tmp_array = [value.year, value.month, value.day]
                value = xlrd.xldate.xldate_from_date_tuple(tmp_array, 0)
                style = XFStyle()
                style.num_format_str = DEFAULT_DATE_FORMAT
            elif isinstance(value, datetime.time):
                tmp_array = [value.hour, value.minute, value.second]
                value = xlrd.xldate.xldate_from_time_tuple(tmp_array)
                style = XFStyle()
                style.num_format_str = DEFAULT_TIME_FORMAT
            if style:
                self._native_sheet.write(self.current_row, i, value, style)
            else:
                self._native_sheet.write(self.current_row, i, value)
        self.current_row += 1


class XLSWriter(BookWriter):
    """
    xls writer
    """
    def __init__(self):
        BookWriter.__init__(self)
        self.work_book = None

    def open(self, file_name,
             encoding='ascii', style_compression=2, **keywords):
        BookWriter.open(self, file_name, **keywords)
        self.work_book = Workbook(style_compression=style_compression,
                                  encoding=encoding)

    def create_sheet(self, name):
        return XLSheetWriter(self.work_book, None, name)

    def close(self):
        """
        This call actually save the file
        """
        self.work_book.save(self._file_alike_object)
