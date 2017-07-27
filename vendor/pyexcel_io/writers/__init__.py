"""
    pyexcel_io.writers
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    file writers

    :copyright: (c) 2014-2017 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
from pyexcel_io.plugins import IOPluginInfoChain


IOPluginInfoChain(__name__).add_a_writer(
    relative_plugin_class_path='csvw.CSVBookWriter',
    file_types=['csv'],
    stream_type='text'
).add_a_writer(
    relative_plugin_class_path='tsv.TSVBookWriter',
    file_types=['tsv'],
    stream_type='text'
).add_a_writer(
    relative_plugin_class_path='csvz.CSVZipBookWriter',
    file_types=['csvz'],
    stream_type='binary'
).add_a_writer(
    relative_plugin_class_path='tsvz.TSVZipBookWriter',
    file_types=['tsvz'],
    stream_type='binary'
)
