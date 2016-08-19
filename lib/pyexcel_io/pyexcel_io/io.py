from ._compact import isstream, is_generator, PY2
from .manager import RWManager
from .constants import (
    FILE_FORMAT_CSV,
    DEFAULT_SHEET_NAME,
    MESSAGE_ERROR_02
)


def get_data(afile, file_type=None, streaming=False, **keywords):
    """Get data from an excel file source

    :param filename: actual file name, a file stream or actual content
    :param sheet_name: the name of the sheet to be loaded
    :param sheet_index: the index of the sheet to be loaded
    :param file_type: used only when filename is not a physial file name
    :param keywords: any other parameters
    :returns: an array if it is a single sheet, an ordered dictionary otherwise
    """
    if isstream(afile) and file_type is None:
        file_type = FILE_FORMAT_CSV
    if isstream(afile):
        data = load_data_new(file_stream=afile,
                             file_type=file_type, **keywords)
    else:
        if afile is not None and file_type is not None:
            data = load_data_new(file_content=afile,
                                 file_type=file_type, **keywords)
        else:
            data = load_data_new(file_name=afile,
                                 file_type=file_type, **keywords)
    if streaming is False:
        for key in data.keys():
            data[key] = list(data[key])
    return data


def save_data(afile, data, file_type=None, **keywords):
    """Save data to an excel file source

    Your data can be an array or an ordered dictionary

    :param filename: actual file name, a file stream or actual content
    :param data: the data to be saved
    :param file_type: used only when filename is not a physial file name
    :param keywords: any other parameters that python csv module's
                     `fmtparams <https://docs.python.org/release/3.1.5/
                      library/csv.html#dialects-and-formatting-parameters>`_
    """
    to_store = data
    if isinstance(data, list) or is_generator(data):
        single_sheet_in_book = True
        to_store = {DEFAULT_SHEET_NAME: data}
    else:
        if PY2:
            keys = data.keys()
        else:
            keys = list(data.keys())
        if len(keys) == 1:
            single_sheet_in_book = True
        else:
            single_sheet_in_book = False

    if isstream(afile) and file_type is None:
        file_type = FILE_FORMAT_CSV

    store_data(afile, to_store,
               file_type=file_type,
               single_sheet_in_book=single_sheet_in_book,
               **keywords)


def store_data(afile, data, file_type=None, **keywords):
    """Non public function to store data to afile

    :param filename: actual file name, a file stream or actual content
    :param data: the data to be written
    :param file_type: used only when filename is not a physial file name
    :param keywords: any other parameters
    """
    if isstream(afile):
        writer = get_writer_new(
            file_stream=afile,
            file_type=file_type,
            **keywords)
    else:
        writer = get_writer_new(
            file_name=afile,
            file_type=file_type,
            **keywords)
    writer.write(data)
    writer.close()


def load_data_new(file_name=None,
                  file_content=None,
                  file_stream=None,
                  file_type=None,
                  sheet_name=None,
                  sheet_index=None,
                  library=None,
                  **keywords):
    """Load data from any supported excel formats

    :param filename: actual file name, a file stream or actual content
    :param file_type: used only when filename is not a physial file name
    :param sheet_name: the name of the sheet to be loaded
    :param sheet_index: the index of the sheet to be loaded
    :param keywords: any other parameters
    """
    result = {}
    inputs = [file_name, file_content, file_stream]
    number_of_none_inputs = [x for x in inputs if x is not None]
    if len(number_of_none_inputs) != 1:
        raise IOError(MESSAGE_ERROR_02)
    if file_type is None:
        file_type = file_name.split(".")[-1]
    reader = RWManager.create_reader(file_type, library)
    if file_name:
        reader.open(file_name, **keywords)
    elif file_content:
        reader.open_content(file_content, **keywords)
    elif file_stream:
        reader.open_stream(file_stream, **keywords)
    if sheet_name:
        result = reader.read_sheet_by_name(sheet_name)
    elif sheet_index is not None:
        result = reader.read_sheet_by_index(sheet_index)
    else:
        result = reader.read_all()
    reader.close()
    return result


def get_writer_new(file_name=None, file_stream=None,
                   file_type=None, library=None, **keywords):
    number_of_none_inputs = list(filter(lambda x: x is not None,
                                        [file_name, file_stream]))

    if len(number_of_none_inputs) != 1:
        raise IOError(MESSAGE_ERROR_02)
    file_type_given = True
    if file_type is None and file_name:
        file_type = file_name.split(".")[-1]
        file_type_given = False

    writer = RWManager.create_writer(file_type, library)
    if file_name:
        if file_type_given:
            writer.open_content(file_name, **keywords)
        else:
            writer.open(file_name, **keywords)
    elif file_stream:
        writer.open_stream(file_stream, **keywords)
    # else: is resolved by earlier raise statement
    return writer
