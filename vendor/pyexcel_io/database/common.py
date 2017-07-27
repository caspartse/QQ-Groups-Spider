"""
    pyexcel_io.database.common
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Common classes shared among database importers and exporters

    :copyright: (c) 2014-2017 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
from pyexcel_io.book import BookReader


class DbExporter(BookReader):
    """ Transcode the book reader interface to db interface """
    def open(self, file_name, **keywords):
        self.export_tables(self, file_name, **keywords)

    def open_stream(self, file_stream, **keywords):
        self.export_tables(self, file_stream, **keywords)

    def open_content(self, file_content, **keywords):
        self.export_tables(file_content, **keywords)

    def export_tables(self, exporter, **keywords):
        """ read database tables """
        raise NotImplementedError("Please implement this method")


class DjangoModelExportAdapter(object):
    """ django export parameter holder """
    def __init__(self, model, export_columns=None):
        self.model = model
        self.export_columns = export_columns

    @property
    def name(self):
        """ get database table name """
        return self.get_name()

    def get_name(self):
        """ get database table name """
        return self.model._meta.model_name


class DjangoModelImportAdapter(DjangoModelExportAdapter):
    """ parameter holder for django data import """
    class InOutParameter(object):
        """ local class to manipulate variable io """
        def __init__(self):
            self.output = None
            self.input = None

    def __init__(self, model):
        DjangoModelExportAdapter.__init__(self, model)
        self.__column_names = self.InOutParameter()
        self.__column_name_mapping_dict = self.InOutParameter()
        self.__row_initializer = self.InOutParameter()
        self._process_parameters()

    @property
    def row_initializer(self):
        """ contructor for a database table entry """
        return self.__row_initializer.output

    @property
    def column_names(self):
        """ the desginated database column names """
        return self.__column_names.output

    @property
    def column_name_mapping_dict(self):
        """ if not the same, a mapping dictionary is looked up"""
        return self.__column_name_mapping_dict.output

    @row_initializer.setter
    def row_initializer(self, a_function):
        """ set the contructor """
        self.__row_initializer.input = a_function
        self._process_parameters()

    @column_names.setter
    def column_names(self, column_names):
        """ set the column names """
        self.__column_names.input = column_names
        self._process_parameters()

    @column_name_mapping_dict.setter
    def column_name_mapping_dict(self, mapping_dict):
        """ set the mapping dict """
        self.__column_name_mapping_dict.input = mapping_dict
        self._process_parameters()

    def _process_parameters(self):
        if self.__row_initializer.input is None:
            self.__row_initializer.output = None
        else:
            self.__row_initializer.output = self.__row_initializer.input
        if isinstance(self.__column_name_mapping_dict.input, list):
            self.__column_names.output = self.__column_name_mapping_dict.input
            self.__column_name_mapping_dict.output = None
        elif isinstance(self.__column_name_mapping_dict.input, dict):
            if self.__column_names.input:
                self.__column_names.output = [
                    self.__column_name_mapping_dict.input[name]
                    for name in self.__column_names.input]
                self.__column_name_mapping_dict.output = None
        if self.__column_names.output is None:
            self.__column_names.output = self.__column_names.input


class DjangoModelExporter(object):
    """ public interface for django model export """
    def __init__(self):
        self.adapters = []

    def append(self, import_adapter):
        """ store model parameter for more than one model """
        self.adapters.append(import_adapter)


class DjangoModelImporter(object):
    """ public interface for django model import """
    def __init__(self):
        self.__adapters = {}

    def append(self, import_adapter):
        """ store model parameter for more than one model """
        self.__adapters[import_adapter.get_name()] = import_adapter

    def get(self, name):
        """ get a parameter out """
        return self.__adapters.get(name, None)


class SQLTableExportAdapter(DjangoModelExportAdapter):
    """ parameter holder for sql table data export """
    def __init__(self, model, export_columns=None):
        DjangoModelExportAdapter.__init__(self, model, export_columns)
        self.table = model

    def get_name(self):
        return getattr(self.table, '__tablename__', None)


class SQLTableImportAdapter(DjangoModelImportAdapter):
    """ parameter holder for sqlalchemy table import """
    def __init__(self, model):
        DjangoModelImportAdapter.__init__(self, model)
        self.table = model

    def get_name(self):
        return getattr(self.table, '__tablename__', None)


class SQLTableExporter(DjangoModelExporter):
    """ public interface for sql table export """
    def __init__(self, session):
        DjangoModelExporter.__init__(self)
        self.session = session


class SQLTableImporter(DjangoModelImporter):
    """ public interface to do data import via sqlalchemy """
    def __init__(self, session):
        DjangoModelImporter.__init__(self)
        self.session = session
