"""
    pyexcel_xlsr
    ~~~~~~~~~~~~~~~~~~~

    The lower level xls/xlsm file format handler using xlrd

    :copyright: (c) 2016-2017 by Onni Software Ltd
    :license: New BSD License
"""
import math
import datetime
import xlrd

from pyexcel_io.book import BookReader
from pyexcel_io.sheet import SheetReader
from pyexcel_io._compact import OrderedDict


XLS_KEYWORDS = [
    'filename', 'logfile', 'verbosity', 'use_mmap',
    'file_contents', 'encoding_override', 'formatting_info',
    'on_demand', 'ragged_rows'
]


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

    def open(self, file_name, skip_hidden_sheets=True, **keywords):
        BookReader.open(self, file_name, **keywords)
        self.__skip_hidden_sheets = skip_hidden_sheets

    def open_stream(self, file_stream, skip_hidden_sheets=True, **keywords):
        BookReader.open_stream(self, file_stream, **keywords)
        self.__skip_hidden_sheets = skip_hidden_sheets

    def open_content(self, file_content, skip_hidden_sheets=True, **keywords):
        self._keywords = keywords
        self._file_content = file_content
        self.__skip_hidden_sheets = skip_hidden_sheets

    def close(self):
        if self._native_book:
            self._native_book.release_resources()
            self._native_book = None

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
            if self.__skip_hidden_sheets and sheet.visibility != 0:
                continue
            data_dict = self.read_sheet(sheet)
            result.update(data_dict)
        return result

    def read_sheet(self, native_sheet):
        sheet = XLSheet(native_sheet, **self._keywords)
        return {sheet.name: sheet.to_array()}

    def _get_book(self, on_demand=False):
        xlrd_params = self._extract_xlrd_params()
        xlrd_params['on_demand'] = on_demand

        if self._file_name:
            xlrd_params['filename'] = self._file_name
        elif self._file_stream:
            self._file_stream.seek(0)
            file_content = self._file_stream.read()
            xlrd_params['file_contents'] = file_content
        elif self._file_content is not None:
            xlrd_params['file_contents'] = self._file_content
        else:
            raise IOError("No valid file name or file content found.")
        xls_book = xlrd.open_workbook(**xlrd_params)
        return xls_book

    def _extract_xlrd_params(self):
        params = {}
        if self._keywords is not None:
            for key in list(self._keywords.keys()):
                if key in XLS_KEYWORDS:
                    params[key] = self._keywords.pop(key)
        return params


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
