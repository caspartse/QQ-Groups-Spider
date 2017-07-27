"""
    pyexcel_io.database.sql
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    The lower level handler for database import and export

    :copyright: (c) 2014-2017 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
from pyexcel_io.database.common import DbExporter
from pyexcel_io.database.querysets import QuerysetsReader


class SQLTableReader(QuerysetsReader):
    """Read a table
    """
    def __init__(self, session, table, export_columns=None, **keywords):
        everything = session.query(table).all()
        column_names = None
        if export_columns:
            column_names = export_columns
        else:
            if len(everything) > 0:
                column_names = sorted([
                    column for column in everything[0].__dict__
                    if column != '_sa_instance_state'])
        QuerysetsReader.__init__(self, everything, column_names, **keywords)


class SQLBookReader(DbExporter):
    """ read a table via sqlalchemy """
    def __init__(self):
        DbExporter.__init__(self)
        self.__exporter = None

    def export_tables(self, file_content, **keywords):
        self.__exporter = file_content
        self._load_from_tables()

    def read_sheet(self, native_sheet):
        reader = SQLTableReader(
            self.__exporter.session,
            native_sheet.table,
            native_sheet.export_columns)
        return reader.to_array()

    def _load_from_tables(self):
        self._native_book = self.__exporter.adapters
