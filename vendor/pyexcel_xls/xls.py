"""
    pyexcel_xls
    ~~~~~~~~~~~~~~~~~~~

    The lower level xls/xlsm file format handler using xlrd/xlwt

    :copyright: (c) 2016-2017 by Onni Software Ltd
    :license: New BSD License
"""
import sys
import math
import datetime
import xlrd
from xlwt import Workbook, XFStyle

from pyexcel_io.book import BookReader, BookWriter
from pyexcel_io.sheet import SheetReader, SheetWriter

PY2 = sys.version_info[0] == 2
if PY2 and sys.version_info[1] < 7:
    from ordereddict import OrderedDict
else:
    from collections import OrderedDict


DEFAULT_DATE_FORMAT = "DD/MM/YY"
DEFAULT_TIME_FORMAT = "HH:MM:SS"
DEFAULT_DATETIME_FORMAT = "%s %s" % (DEFAULT_DATE_FORMAT, DEFAULT_TIME_FORMAT)


class XLSheet(SheetReader):
    """
    xls, xlsx, xlsm sheet reader

    Currently only support first sheet in the file
    """
    def __init__(self, sheet, auto_detect_int=True, **keywords):
        SheetReader.__init__(self, sheet, **keywords)
        self.__auto_detect_int = auto_detect_int

    @property
    def name(self):
        return self._native_sheet.name

    def number_of_rows(self):
        """
        Number of rows in the xls sheet
        """
        return self._native_sheet.nrows

    def number_of_columns(self):
        """
        Number of columns in the xls sheet
        """
        return self._native_sheet.ncols

    def cell_value(self, row, column):
        """
        Random access to the xls cells
        """
        cell_type = self._native_sheet.cell_type(row, column)
        value = self._native_sheet.cell_value(row, column)
        if cell_type == xlrd.XL_CELL_DATE:
            value = xldate_to_python_date(value)
        elif cell_type == xlrd.XL_CELL_NUMBER and self.__auto_detect_int:
            if is_integer_ok_for_xl_float(value):
                value = int(value)
        return value


class XLSBook(BookReader):
    """
    XLSBook reader

    It reads xls, xlsm, xlsx work book
    """
    def __init__(self):
        BookReader.__init__(self)
        self._file_content = None

    def open(self, file_name, **keywords):
        BookReader.open(self, file_name, **keywords)
        self._get_params()

    def open_stream(self, file_stream, **keywords):
        BookReader.open_stream(self, file_stream, **keywords)
        self._get_params()

    def open_content(self, file_content, **keywords):
        self._keywords = keywords
        self._file_content = file_content
        self._get_params()

    def close(self):
        if self._native_book:
            self._native_book.release_resources()

    def read_sheet_by_index(self, sheet_index):
        self._native_book = self._get_book(on_demand=True)
        sheet = self._native_book.sheet_by_index(sheet_index)
        return self.read_sheet(sheet)

    def read_sheet_by_name(self, sheet_name):
        self._native_book = self._get_book(on_demand=True)
        try:
            sheet = self._native_book.sheet_by_name(sheet_name)
        except xlrd.XLRDError:
            raise ValueError("%s cannot be found" % sheet_name)
        return self.read_sheet(sheet)

    def read_all(self):
        result = OrderedDict()
        self._native_book = self._get_book()
        for sheet in self._native_book.sheets():
            if self.skip_hidden_sheets and sheet.visibility != 0:
                continue
            data_dict = self.read_sheet(sheet)
            result.update(data_dict)
        return result

    def read_sheet(self, native_sheet):
        sheet = XLSheet(native_sheet, **self._keywords)
        return {sheet.name: sheet.to_array()}

    def _get_book(self, on_demand=False):
        if self._file_name:
            xls_book = xlrd.open_workbook(self._file_name, on_demand=on_demand)
        elif self._file_stream:
            self._file_stream.seek(0)
            file_content = self._file_stream.read()
            xls_book = xlrd.open_workbook(
                None,
                file_contents=file_content,
                on_demand=on_demand
            )
        elif self._file_content is not None:
            xls_book = xlrd.open_workbook(
                None,
                file_contents=self._file_content,
                on_demand=on_demand
            )
        else:
            raise IOError("No valid file name or file content found.")
        return xls_book

    def _get_params(self):
        self.skip_hidden_sheets = self._keywords.get(
            'skip_hidden_sheets', True)


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


def is_integer_ok_for_xl_float(value):
    """check if a float value had zero value in digits"""
    return value == math.floor(value)


def xldate_to_python_date(value):
    """
    convert xl date to python date
    """
    date_tuple = xlrd.xldate_as_tuple(value, 0)
    ret = None
    if date_tuple == (0, 0, 0, 0, 0, 0):
        ret = datetime.datetime(1900, 1, 1, 0, 0, 0)
    elif date_tuple[0:3] == (0, 0, 0):
        ret = datetime.time(date_tuple[3],
                            date_tuple[4],
                            date_tuple[5])
    elif date_tuple[3:6] == (0, 0, 0):
        ret = datetime.date(date_tuple[0],
                            date_tuple[1],
                            date_tuple[2])
    else:
        ret = datetime.datetime(
            date_tuple[0],
            date_tuple[1],
            date_tuple[2],
            date_tuple[3],
            date_tuple[4],
            date_tuple[5]
        )
    return ret


_xls_reader_registry = {
    "file_type": "xls",
    "reader": XLSBook,
    "writer": XLSWriter,
    "stream_type": "binary",
    "mime_type": "application/vnd.ms-excel",
    "library": "pyexcel-xls"
}

_XLSM_MIME = (
    "application/" +
    "vnd.openxmlformats-officedocument.spreadsheetml.sheet")

_xlsm_registry = {
    "file_type": "xlsm",
    "reader": XLSBook,
    "stream_type": "binary",
    "mime_type": _XLSM_MIME,
    "library": "pyexcel-xls"
}

_xlsx_registry = {
    "file_type": "xlsx",
    "reader": XLSBook,
    "stream_type": "binary",
    "mime_type": "application/vnd.ms-excel.sheet.macroenabled.12",
    "library": "pyexcel-xls"
}

exports = (_xls_reader_registry,
           _xlsm_registry,
           _xlsx_registry)
