"""
    pyexcel_io.database.django
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The lower level handler for django import and export

    :copyright: (c) 2014-2017 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
from pyexcel_io.database.common import DbExporter
from pyexcel_io.database.querysets import QuerysetsReader


class DjangoModelReader(QuerysetsReader):
    """Read from django model
    """
    def __init__(self, model, export_columns=None, **keywords):
        self.__model = model
        if export_columns:
            column_names = export_columns
        else:
            column_names = sorted(
                [field.attname
                 for field in self.__model._meta.concrete_fields])
        QuerysetsReader.__init__(self, self.__model.objects.all(),
                                 column_names,
                                 **keywords)


class DjangoBookReader(DbExporter):
    """ read django models """
    def __init__(self):
        DbExporter.__init__(self)
        self.exporter = None

    def export_tables(self, file_content, **keywords):
        self.exporter = file_content
        self._load_from_django_models()

    def read_sheet(self, native_sheet):
        reader = DjangoModelReader(native_sheet.model,
                                   native_sheet.export_columns)
        return reader.to_array()

    def _load_from_django_models(self):
        self._native_book = self.exporter.adapters
