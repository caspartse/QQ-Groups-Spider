"""
    pyexcel_io.database.sql
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    The lower level handler for database import and export

    :copyright: (c) 2014-2017 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
from pyexcel_io.book import BookWriter
from pyexcel_io.sheet import SheetWriter
from pyexcel_io.utils import is_empty_array, swap_empty_string_for_none
import pyexcel_io.constants as constants


class PyexcelSQLSkipRowException(Exception):
    """
    Raised this exception to skipping a row
    while data import
    """
    pass


class SQLTableWriter(SheetWriter):
    """Write to a table
    """
    def __init__(self, importer, adapter, auto_commit=True, **keywords):
        SheetWriter.__init__(self, importer, adapter,
                             adapter.get_name(), **keywords)
        self.__auto_commit = auto_commit

    def write_row(self, array):
        if is_empty_array(array):
            print(constants.MESSAGE_EMPTY_ARRAY)
        else:
            new_array = swap_empty_string_for_none(array)
            try:
                self._write_row(new_array)
            except PyexcelSQLSkipRowException:
                print(constants.MESSAGE_IGNORE_ROW)
                print(new_array)

    def _write_row(self, array):
        row = dict(zip(self._native_sheet.column_names, array))
        obj = None
        if self._native_sheet.row_initializer:
            # allow initinalizer to return None
            # if skipping is needed
            obj = self._native_sheet.row_initializer(row)
        if obj is None:
            obj = self._native_sheet.table()
            for name in self._native_sheet.column_names:
                if self._native_sheet.column_name_mapping_dict is not None:
                    key = self._native_sheet.column_name_mapping_dict[name]
                else:
                    key = name
                setattr(obj, key, row[name])
        self._native_book.session.add(obj)

    def close(self):
        if self.__auto_commit:
            self._native_book.session.commit()


class SQLBookWriter(BookWriter):
    """ write data into database tables via sqlalchemy """
    def __init__(self):
        BookWriter.__init__(self)
        self.__importer = None
        self.__auto_commit = True

    def open_content(self, file_content, auto_commit=True, **keywords):
        self.__importer = file_content
        self.__auto_commit = auto_commit

    def create_sheet(self, sheet_name):
        sheet_writer = None
        adapter = self.__importer.get(sheet_name)
        if adapter:
            sheet_writer = SQLTableWriter(
                self.__importer, adapter,
                auto_commit=self.__auto_commit
            )
        return sheet_writer
