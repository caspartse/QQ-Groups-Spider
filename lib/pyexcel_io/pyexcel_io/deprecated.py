from functools import partial
from .io import load_data_new, get_writer_new

from .constants import (
    MESSAGE_ERROR_02,
    MESSAGE_CANNOT_WRITE_STREAM_FORMATTER,
    MESSAGE_CANNOT_READ_STREAM_FORMATTER,
    MESSAGE_CANNOT_WRITE_FILE_TYPE_FORMATTER,
    MESSAGE_CANNOT_READ_FILE_TYPE_FORMATTER,
)
from ._compact import is_string, isstream


def deprecated(func, message="Deprecated!"):
    def inner(*arg, **keywords):
        print(message)
        return func(*arg, **keywords)
    return inner


DEPRECATED_DATA_LOADER = partial(
    deprecated,
    message="Deprecated since 0.2.0! Please use get_data instead.")

DEPRECATED_GET_WRITER = partial(
    deprecated,
    message="Deprecated since 0.2.0! Please use save_data.")


@DEPRECATED_DATA_LOADER
def load_data(filename,
              file_type=None,
              sheet_name=None,
              sheet_index=None,
              **keywords):
    file_name = None
    file_stream = None
    file_content = None
    extension = None
    from_memory = False
    if filename is None:
        raise IOError(MESSAGE_ERROR_02)
    elif not is_string(type(filename)) and not isstream(filename):
        raise IOError(MESSAGE_ERROR_02)
    if file_type is not None:
        from_memory = True
        extension = file_type
    else:
        extension = filename.split(".")[-1]
    if from_memory:
        if isstream(filename):
            file_stream = filename
        else:
            file_content = filename
    else:
        file_name = filename
    try:
        return load_data_new(
            file_name=file_name,
            file_content=file_content,
            file_stream=file_stream,
            file_type=extension,
            sheet_name=sheet_name,
            sheet_index=sheet_index,
            **keywords
        )
    except NotImplementedError:
        if from_memory:
            raise NotImplementedError(
                MESSAGE_CANNOT_READ_STREAM_FORMATTER % extension)
        else:
            raise NotImplementedError(
                MESSAGE_CANNOT_READ_FILE_TYPE_FORMATTER % (
                    extension, filename))


@DEPRECATED_GET_WRITER
def get_writer(filename, file_type=None, **keywords):
    """Create a writer from any supported excel formats

    :param filename: actual file name or a file stream
    :param file_type: used only when filename is not a physial file name
    :param keywords: any other parameters
    """
    extension = None
    to_memory = False
    file_name = None
    file_stream = None
    if filename is None:
        raise IOError(MESSAGE_ERROR_02)
    elif not is_string(type(filename)) and not isstream(filename):
        raise IOError(MESSAGE_ERROR_02)
    if isstream(filename):
        to_memory = True
        file_stream = filename
    else:
        file_name = filename
    try:
        return get_writer_new(file_name=file_name, file_stream=file_stream,
                              file_type=file_type, **keywords)
    except NotImplementedError:
        if to_memory:
            raise NotImplementedError(
                MESSAGE_CANNOT_WRITE_STREAM_FORMATTER % extension)
        else:
            raise NotImplementedError(
                MESSAGE_CANNOT_WRITE_FILE_TYPE_FORMATTER % (
                    extension, filename))
