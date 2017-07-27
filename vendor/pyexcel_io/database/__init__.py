"""
    pyexcel_io.database
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    database data importer and exporter

    :copyright: (c) 2014-2017 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
from pyexcel_io.plugins import IOPluginInfoChain
from pyexcel_io.constants import DB_DJANGO, DB_SQL


IOPluginInfoChain(__name__).add_a_reader(
    relative_plugin_class_path='exporters.django.DjangoBookReader',
    file_types=[DB_DJANGO]
).add_a_reader(
    relative_plugin_class_path='exporters.sqlalchemy.SQLBookReader',
    file_types=[DB_SQL],
).add_a_writer(
    relative_plugin_class_path='importers.django.DjangoBookWriter',
    file_types=[DB_DJANGO],
).add_a_writer(
    relative_plugin_class_path='importers.sqlalchemy.SQLBookWriter',
    file_types=[DB_SQL]
)
