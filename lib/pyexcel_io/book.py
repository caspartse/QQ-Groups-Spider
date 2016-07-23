"""
    pyexcel_io.base
    ~~~~~~~~~~~~~~~~~~~

    The io interface to file extensions

    :copyright: (c) 2014-2016 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
from .manager import RWManager
from ._compact import PY2, OrderedDict, isstream, StringIO
from .constants import (
    MESSAGE_ERROR_03,
    MESSAGE_WRONG_IO_INSTANCE
)


class RWInterface(object):
    """
    The common methods for book reader and writer
    """
    def __init__(self):
        self.file_type = None

    def open(self, file_name, **keywords):
        """open a file for read or write"""
        raise NotImplementedError("Please implement this method")

    def open_stream(self, file_stream, **keywords):
        """open a file stream for read or write"""
        raise NotImplementedError("Please implement this method")

    def open_content(self, file_stream, **keywords):
        """open a file content for read or write"""
        raise NotImplementedError("Please implement this method")

    def set_type(self, file_type):
        """
        set the file type for the instance

        file type is needed when a third party library could
        handle more than one file type"""
        self.file_type = file_type

    def close(self):
        """
        close the file handle if necessary
        """
        pass


class BookReader(RWInterface):
    """
    Standard book reader
    """
    def __init__(self):
        self.reader = None
        self.file_name = None
        self.file_stream = None
        self.keywords = None
        self.native_book = None

    def open(self, file_name, **keywords):
        """
        open a file with unlimited keywords

        keywords are passed on to individual readers
        """
        self.file_name = file_name
        self.keywords = keywords

    def open_stream(self, file_stream, **keywords):
        """
        open a file with unlimited keywords for reading

        keywords are passed on to individual readers
        """
        if isstream(file_stream):
            self.file_stream = file_stream
            self.keywords = keywords
        else:
            raise IOError(MESSAGE_WRONG_IO_INSTANCE)

    def open_content(self, file_content, **keywords):
        """
        read file content as if it is a file stream with
        unlimited keywords for reading

        keywords are passed on to individual readers
        """
        file_stream = _convert_content_to_stream(file_content, self.file_type)
        self.open_stream(file_stream, **keywords)

    def read_sheet_by_name(self, sheet_name):
        """
        read a named sheet from a excel data book
        """
        named_contents = [content for content in self.native_book
                          if content.name == sheet_name]
        if len(named_contents) == 1:
            return {named_contents[0].name: self.read_sheet(named_contents[0])}
        else:
            self.close()
            raise ValueError("Cannot find sheet %s" % sheet_name)

    def read_sheet_by_index(self, sheet_index):
        """
        read an indexed sheet from a excel data book
        """
        try:
            sheet = self.native_book[sheet_index]
            return {sheet.name: self.read_sheet(sheet)}
        except IndexError:
            self.close()
            raise

    def read_all(self):
        """
        read everything from a excel data book
        """
        result = OrderedDict()
        for sheet in self.native_book:
            result[sheet.name] = self.read_sheet(sheet)
        return result

    def read_sheet(self, native_sheet):
        """
        Return a context specific sheet from a native sheet
        """
        raise NotImplementedError("Please implement this method")


def _convert_content_to_stream(file_content, file_type):
    io = RWManager.get_io(file_type)
    if PY2:
        io.write(file_content)
    else:
        if (isinstance(io, StringIO) and isinstance(file_content, bytes)):
            content = file_content.decode('utf-8')
        else:
            content = file_content
        io.write(content)
    io.seek(0)
    return io


class BookWriter(RWInterface):
    """
    Standard book writer
    """
    def __init__(self):
        self.file_alike_object = None

    def open(self, file_name, **keywords):
        """
        open a file with unlimited keywords for writing

        keywords are passed on to individual writers
        """
        self.file_alike_object = file_name
        self.keywords = keywords

    def open_stream(self, file_stream, **keywords):
        """
        open a file stream with unlimited keywords for writing

        keywords are passed on to individual writers
        """
        if not isstream(file_stream):
            raise IOError(MESSAGE_ERROR_03)
        self.open(file_stream, **keywords)

    def write(self, incoming_dict):
        for sheet_name in incoming_dict:
            sheet_writer = self.create_sheet(sheet_name)
            if sheet_writer:
                sheet_writer.write_array(incoming_dict[sheet_name])
                sheet_writer.close()

    def create_sheet(self, sheet_name):
        pass
