"""
    pyexcel_io.readers.csvr
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    csv file reader

    :copyright: (c) 2014-2017 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
import re
import os
import csv
import glob
import codecs
import datetime

from pyexcel_io.book import BookReader
from pyexcel_io.sheet import SheetReader, NamedContent
import pyexcel_io._compact as compact
import pyexcel_io.constants as constants


DEFAULT_SEPARATOR = '__'
DEFAULT_SHEET_SEPARATOR_FORMATTER = '---%s---' % constants.DEFAULT_NAME + "%s"
SEPARATOR_MATCHER = "---%s:(.*)---" % constants.DEFAULT_NAME
DEFAULT_CSV_STREAM_FILE_FORMATTER = (
    "---%s:" % constants.DEFAULT_NAME + "%s---%s")
DEFAULT_NEWLINE = '\r\n'
BOM_LITTLE_ENDIAN = b'\xff\xfe'
BOM_BIG_ENDIAN = b'\xfe\ff'
LITTLE_ENDIAN = 0
BIG_ENDIAN = 1


class CSVMemoryMapIterator(compact.Iterator):
    """
    Wrapper class for mmap object

    mmap object does not handle encoding at all. This class
    provide the necessary transcoding for utf-8, utf-16 and utf-32
    """
    def __init__(self, mmap_obj, encoding):
        self.__mmap_obj = mmap_obj
        self.__encoding = encoding
        self.__count = 0
        self.__endian = LITTLE_ENDIAN
        if encoding == 'utf-8':
            # ..\r\x00\n
            # \x00\x..
            self.__zeros_left_in_2_row = 0
        elif encoding == 'utf-16':
            # ..\r\x00\n
            # \x00\x..
            self.__zeros_left_in_2_row = 1
        elif encoding == 'utf-32':
            # \r\x00\x00\x00\n
            # \x00\x00\x00\x..
            self.__zeros_left_in_2_row = 3
        elif encoding == 'utf-32-be' or encoding == 'utf-16-be':
            self.__zeros_left_in_2_row = 0
            self.__endian = BIG_ENDIAN
        elif encoding == 'utf-32-le':
            self.__zeros_left_in_2_row = 3
            self.__endian = LITTLE_ENDIAN
        elif encoding == 'utf-16-le':
            self.__zeros_left_in_2_row = 1
            self.__endian = LITTLE_ENDIAN
        else:
            raise Exception("Encoding %s is not supported" % encoding)

    def __iter__(self):
        return self

    def __next__(self):
        line = self.__mmap_obj.readline()
        if self.__count == 0:
            utf_16_32 = (self.__encoding == 'utf-16' or
                         self.__encoding == 'utf-32')
            if utf_16_32:
                bom_header = line[:2]
                if bom_header == BOM_BIG_ENDIAN:
                    self.__endian = BIG_ENDIAN
        elif self.__endian == LITTLE_ENDIAN:
            line = line[self.__zeros_left_in_2_row:]
        if self.__endian == LITTLE_ENDIAN:
            line = line.rstrip()
        line = line.decode(self.__encoding)
        self.__count += 1
        if line == '':
            raise StopIteration
        if compact.PY2:
            # python 2 requires utf-8 encoded string for reading
            line = line.encode('utf-8')
        return line


class UTF8Recorder(compact.Iterator):
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8.
    """
    def __init__(self, file_handle, encoding):
        self.__file_handle = file_handle
        self.reader = codecs.getreader(encoding)(file_handle)

    def close(self):
        self.__file_handle.close()

    def __iter__(self):
        return self

    def __next__(self):
        # python 2 requires utf-8 encoded string for reading
        line = next(self.reader).encode('utf-8')
        return line


class CSVSheetReader(SheetReader):
    """ generic csv file reader"""
    def __init__(self, sheet, encoding="utf-8",
                 auto_detect_float=True, ignore_infinity=True,
                 auto_detect_int=True, auto_detect_datetime=True,
                 **keywords):
        SheetReader.__init__(self, sheet, **keywords)
        self._encoding = encoding
        self.__auto_detect_int = auto_detect_int
        self.__auto_detect_float = auto_detect_float
        self.__ignore_infinity = ignore_infinity
        self.__auto_detect_datetime = auto_detect_datetime
        self.__file_handle = None

    def get_file_handle(self):
        """ return me unicde reader for csv """
        raise NotImplementedError("Please implement get_file_handle()")

    def row_iterator(self):
        self.__file_handle = self.get_file_handle()
        return csv.reader(self.__file_handle, **self._keywords)

    def column_iterator(self, row):
        for element in row:
            if compact.PY2:
                element = element.decode('utf-8')
            if element is not None and element != '':
                element = self.__convert_cell(element)
            yield element

    def __convert_cell(self, csv_cell_text):
        ret = None
        if self.__auto_detect_int:
            ret = _detect_int_value(csv_cell_text)
        if ret is None and self.__auto_detect_float:
            ret = _detect_float_value(csv_cell_text)
            shall_we_ignore_the_conversion = (
                (ret in [float('inf'), float('-inf')]) and
                self.__ignore_infinity
            )
            if shall_we_ignore_the_conversion:
                ret = None
        if ret is None and self.__auto_detect_datetime:
            ret = _detect_date_value(csv_cell_text)
        if ret is None:
            ret = csv_cell_text
        return ret

    def close(self):
        if self.__file_handle:
            self.__file_handle.close()
        # else: means the generator has been run
        # yes, no run, no file open.


class CSVFileReader(CSVSheetReader):
    """ read csv from phyical file """
    def get_file_handle(self):
        unicode_reader = None
        if compact.PY2:
            file_handle = open(self._native_sheet.payload, 'rb')
            unicode_reader = UTF8Recorder(file_handle, self._encoding)
        else:
            unicode_reader = open(self._native_sheet.payload, 'r',
                                  encoding=self._encoding)
        return unicode_reader


class CSVinMemoryReader(CSVSheetReader):
    """ read csv file from memory """
    def get_file_handle(self):
        unicode_reader = None
        if compact.PY2:
            if hasattr(self._native_sheet.payload, 'read'):
                unicode_reader = UTF8Recorder(self._native_sheet.payload,
                                              self._encoding)
            else:
                unicode_reader = self._native_sheet.payload
        else:
            if isinstance(self._native_sheet.payload, compact.BytesIO):
                # please note that
                # if the end developer feed us bytesio in python3
                # we will do the conversion to StriongIO but that
                # comes at a cost.
                content = self._native_sheet.payload.read()
                unicode_reader = compact.StringIO(
                    content.decode(self._encoding))
            else:
                unicode_reader = self._native_sheet.payload

        return unicode_reader


class CSVBookReader(BookReader):
    """ read csv file """
    def __init__(self):
        BookReader.__init__(self)
        self._file_type = constants.FILE_FORMAT_CSV
        self._file_content = None
        self.__load_from_memory_flag = False
        self.__line_terminator = constants.DEFAULT_CSV_NEWLINE
        self.__sheet_name = None
        self.__sheet_index = None
        self.__multiple_sheets = False
        self.__readers = []

    def open(self, file_name, **keywords):
        BookReader.open(self, file_name, **keywords)
        self._native_book = self._load_from_file()

    def open_stream(self, file_stream, multiple_sheets=False, **keywords):
        BookReader.open_stream(self, file_stream, **keywords)
        self.__multiple_sheets = multiple_sheets
        self._native_book = self._load_from_stream()

    def open_content(self, file_content, **keywords):
        if compact.PY27_ABOVE:
            import mmap
            encoding = keywords.get('encoding', 'utf-8')
            if isinstance(file_content, mmap.mmap):
                # load from mmap
                self.__multiple_sheets = keywords.get('multiple_sheets', False)
                self._file_stream = CSVMemoryMapIterator(
                    file_content, encoding)
                self._keywords = keywords
                self._native_book = self._load_from_stream()
            else:
                if compact.PY3_ABOVE:
                    if isinstance(file_content, bytes):
                        file_content = file_content.decode(encoding)
                # else python 2.7 does not care about bytes nor str
                BookReader.open_content(
                    self, file_content, **keywords)
        else:
            BookReader.open_content(
                self, file_content, **keywords)

    def read_sheet(self, native_sheet):
        if self.__load_from_memory_flag:
            reader = CSVinMemoryReader(native_sheet, **self._keywords)
        else:
            reader = CSVFileReader(native_sheet, **self._keywords)
            self.__readers.append(reader)
        return reader.to_array()

    def close(self):
        for reader in self.__readers:
            reader.close()

    def _load_from_stream(self):
        """Load content from memory

        :params stream file_content: the actual file content in memory
        :returns: a book
        """
        self.__load_from_memory_flag = True
        self.__line_terminator = self._keywords.get(
            constants.KEYWORD_LINE_TERMINATOR,
            self.__line_terminator)
        separator = DEFAULT_SHEET_SEPARATOR_FORMATTER % self.__line_terminator
        if self.__multiple_sheets:
            # will be slow for large files
            self._file_stream.seek(0)
            content = self._file_stream.read()
            sheets = content.split(separator)
            named_contents = []
            for sheet in sheets:
                if sheet == '':  # skip empty named sheet
                    continue
                lines = sheet.split(self.__line_terminator)
                result = re.match(constants.SEPARATOR_MATCHER, lines[0])
                new_content = '\n'.join(lines[1:])
                new_sheet = NamedContent(result.group(1),
                                         compact.StringIO(new_content))
                named_contents.append(new_sheet)
            return named_contents
        else:
            if hasattr(self._file_stream, 'seek'):
                self._file_stream.seek(0)
            return [NamedContent(self._file_type, self._file_stream)]

    def _load_from_file(self):
        """Load content from a file

        :params str filename: an accessible file path
        :returns: a book
        """
        self.__line_terminator = self._keywords.get(
            constants.KEYWORD_LINE_TERMINATOR,
            self.__line_terminator)
        names = self._file_name.split('.')
        filepattern = "%s%s*%s*.%s" % (
            names[0],
            constants.DEFAULT_MULTI_CSV_SEPARATOR,
            constants.DEFAULT_MULTI_CSV_SEPARATOR,
            names[1])
        filelist = glob.glob(filepattern)
        if len(filelist) == 0:
            file_parts = os.path.split(self._file_name)
            return [NamedContent(file_parts[-1], self._file_name)]
        else:
            matcher = "%s%s(.*)%s(.*).%s" % (
                names[0],
                constants.DEFAULT_MULTI_CSV_SEPARATOR,
                constants.DEFAULT_MULTI_CSV_SEPARATOR,
                names[1])
            tmp_file_list = []
            for filen in filelist:
                result = re.match(matcher, filen)
                tmp_file_list.append((result.group(1), result.group(2), filen))
            ret = []
            for lsheetname, index, filen in sorted(tmp_file_list,
                                                   key=lambda row: row[1]):
                ret.append(NamedContent(lsheetname, filen))
            return ret


def _detect_date_value(csv_cell_text):
    """
    Read the date formats that were written by csv.writer
    """
    ret = None
    try:
        if len(csv_cell_text) == 10:
            ret = datetime.datetime.strptime(
                csv_cell_text,
                "%Y-%m-%d")
            ret = ret.date()
        elif len(csv_cell_text) == 19:
            ret = datetime.datetime.strptime(
                csv_cell_text,
                "%Y-%m-%d %H:%M:%S")
        elif len(csv_cell_text) > 19:
            ret = datetime.datetime.strptime(
                csv_cell_text[0:26],
                "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        pass
    return ret


def _detect_float_value(csv_cell_text):
    try:
        if csv_cell_text.startswith('0'):
            # do not convert if a number starts with 0
            # e.g. 014325
            return None
        else:
            return float(csv_cell_text)
    except ValueError:
        return None


def _detect_int_value(csv_cell_text):
    if csv_cell_text.startswith('0') and len(csv_cell_text) > 1:
        return None
    try:
        return int(csv_cell_text)
    except ValueError:
        return None
