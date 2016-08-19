"""
    pyexcel_io
    ~~~~~~~~~~~~~~~~~~~

    Uniform interface for reading/writing different excel file formats

    :copyright: (c) 2014-2016 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
# flake8: noqa
from .io import get_data, save_data
from .manager import RWManager
from . import fileformat, database

exports = fileformat.exports + database.exports

from pkgutil import iter_modules

black_list = [__name__, 'pyexcel_webio', 'pyexcel_text']

for _, module_name, ispkg in iter_modules():
    if module_name in black_list:
        continue

    if ispkg and module_name.startswith('pyexcel_'):
        try:
            plugin = __import__(module_name)
            if hasattr(plugin, '__pyexcel_io_plugins__'):
                for p in plugin.__pyexcel_io_plugins__:
                    plugin = __import__("%s.%s" % (module_name, p))
                    submodule = getattr(plugin, p)
                    exports += submodule.exports
        except ImportError:
            continue

RWManager.register_readers_and_writers(exports)
