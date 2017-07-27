"""
    pyexcel_xls
    ~~~~~~~~~~~~~~~~~~~

    The lower level xls/xlsx/xlsm file format handler using xlrd/xlwt

    :copyright: (c) 2016-2017 by Onni Software Ltd
    :license: New BSD License
"""
# flake8: noqa
# this line has to be place above all else
# because of dynamic import
from pyexcel_io.plugins import IOPluginInfoChain
from pyexcel_io.io import get_data as read_data, isstream, store_data as write_data

__FILE_TYPE__ = 'xls'
IOPluginInfoChain(__name__).add_a_reader(
    relative_plugin_class_path='xlsr.XLSBook',
    file_types=[__FILE_TYPE__, 'xlsx', 'xlsm'],
    stream_type='binary'
).add_a_writer(
    relative_plugin_class_path='xlsw.XLSWriter',
    file_types=[__FILE_TYPE__],
    stream_type='binary'
)


def get_data(afile, file_type=None, **keywords):
    """standalone module function for reading module supported file type"""
    if isstream(afile) and file_type is None:
        file_type = __FILE_TYPE__
    return read_data(afile, file_type=file_type, **keywords)


def save_data(afile, data, file_type=None, **keywords):
    """standalone module function for writing module supported file type"""
    if isstream(afile) and file_type is None:
        file_type = __FILE_TYPE__
    write_data(afile, data, file_type=file_type, **keywords)
