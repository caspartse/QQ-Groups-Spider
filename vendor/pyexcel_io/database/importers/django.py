"""
    pyexcel_io.database.django
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The lower level handler for django import and export

    :copyright: (c) 2014-2017 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
import logging

from pyexcel_io.book import BookWriter
from pyexcel_io.sheet import SheetWriter
from pyexcel_io.utils import is_empty_array, swap_empty_string_for_none
import pyexcel_io.constants as constants

log = logging.getLogger(__name__)


class DjangoModelWriter(SheetWriter):
    """ import data into a django model """
    def __init__(self, importer, adapter, batch_size=None,
                 bulk_save=True):
        SheetWriter.__init__(self, importer, adapter, adapter.name)
        self.__batch_size = batch_size
        self.__model = adapter.model
        self.__column_names = adapter.column_names
        self.__mapdict = adapter.column_name_mapping_dict
        self.__initializer = adapter.row_initializer
        self.__objs = []
        self.__bulk_save = bulk_save

    def write_row(self, array):
        if is_empty_array(array):
            print(constants.MESSAGE_EMPTY_ARRAY)
        else:
            new_array = swap_empty_string_for_none(array)
            model_to_be_created = new_array
            if self.__initializer is not None:
                model_to_be_created = self.__initializer(new_array)
            if model_to_be_created:
                self.__objs.append(self.__model(**dict(
                    zip(self.__column_names, model_to_be_created)
                )))
            # else
                # skip the row

    def close(self):
        if self.__bulk_save:
            try:
                self.__model.objects.bulk_create(
                    self.__objs, batch_size=self.__batch_size)
            except Exception as bulk_create_exception:
                log.info(constants.MESSAGE_DB_EXCEPTION)
                log.exception(bulk_create_exception)
                raise

        else:
            for an_object in self.__objs:
                try:
                    an_object.save()
                except Exception as single_save_exception:
                    log.info(constants.MESSAGE_IGNORE_ROW)
                    log.exception(single_save_exception)
                    raise


class DjangoBookWriter(BookWriter):
    """ write data into django models """
    def __init__(self):
        BookWriter.__init__(self)
        self.__importer = None

    def open_content(self, file_content, **keywords):
        self.__importer = file_content
        self._keywords = keywords

    def create_sheet(self, sheet_name):
        sheet_writer = None
        model = self.__importer.get(sheet_name)
        if model:
            sheet_writer = DjangoModelWriter(
                self.__importer, model,
                batch_size=self._keywords.get('batch_size', None))
        return sheet_writer
