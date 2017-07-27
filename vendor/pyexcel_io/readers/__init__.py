"""
    pyexcel_io.readers
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    file readers

    :copyright: (c) 2014-2017 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
from pyexcel_io.plugins import IOPluginInfoChain


IOPluginInfoChain(__name__).add_a_reader(
    relative_plugin_class_path='csvr.CSVBookReader',
    file_types=['csv'],
    stream_type='text'
).add_a_reader(
    relative_plugin_class_path='tsv.TSVBookReader',
    file_types=['tsv'],
    stream_type='text'
).add_a_reader(
    relative_plugin_class_path='csvz.CSVZipBookReader',
    file_types=['csvz'],
    stream_type='binary'
).add_a_reader(
    relative_plugin_class_path='tsvz.TSVZipBookReader',
    file_types=['tsvz'],
    stream_type='binary'
)
