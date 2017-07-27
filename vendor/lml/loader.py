"""
    lml.loader
    ~~~~~~~~~~~~~~~~~~~

    Plugin discovery module. It supports plugins installed via pip tools
    and pyinstaller. :func:`~lml.loader.scan_plugins` is expected to be
    called in the main package of yours at an earliest time of convenience.

    :copyright: (c) 2017 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
import pkgutil
import logging
from itertools import chain
from lml.utils import do_import


log = logging.getLogger(__name__)


def scan_plugins(prefix, path, black_list=None, white_list=None):
    """
    Implicitly discover plugins via pkgutil and pyinstaller path

    Parameters
    -----------------

    prefix:string
      module prefix. This prefix should become the prefix of the module name
      of all plugins.

      In the tutorial, robotchef-britishcuisine is a plugin package
      of robotchef and its module name is 'robotchef_britishcuisine'. When
      robotchef call scan_plugins to load its cuisine plugins, it specifies
      its prefix as "robotchef_". All modules that starts with 'robotchef_'
      will be auto-loaded: robotchef_britishcuisine, robotchef_chinesecuisine,
      etc.

    path:string
       used in pyinstaller only. When your end developer would package
       your main library and its plugins using pyinstaller, this path
       helps pyinstaller to find the plugins.

    black_list:list
       a list of module names that should be skipped.

    white_list:list
       a list of modules that comes with your main module. If you have a
       built-in module, the module name should be inserted into the list.

       For example, robot_cuisine is a built-in module inside robotchef. It
       is listed in white_list.
    """
    log.debug("scanning for plugins...")
    if black_list is None:
        black_list = []

    if white_list is None:
        white_list = []

    # scan pkgutil.iter_modules
    module_names = (module_info[1] for module_info in pkgutil.iter_modules()
                    if module_info[2] and module_info[1].startswith(prefix))

    # scan pyinstaller
    module_names_from_pyinstaller = scan_from_pyinstaller(prefix, path)

    all_modules = chain(module_names,
                        module_names_from_pyinstaller,
                        white_list)
    # loop through modules and find our plug ins
    for module_name in all_modules:

        if module_name in black_list:
            log.debug("ignored " + module_name)
            continue

        try:
            do_import(module_name)
        except ImportError as e:
            log.debug(module_name)
            log.debug(e)
            continue
    log.debug("scanning done")


# load modules to work based with and without pyinstaller
# from: https://github.com/webcomics/dosage/blob/master/dosagelib/loader.py
# see: https://github.com/pyinstaller/pyinstaller/issues/1905
# load modules using iter_modules()
# (should find all plug ins in normal build, but not pyinstaller)
def scan_from_pyinstaller(prefix, path):
    """
    Discover plugins from pyinstaller
    """
    table_of_content = set()
    for a_toc in (importer.toc for importer in map(pkgutil.get_importer, path)
                  if hasattr(importer, 'toc')):
        table_of_content |= a_toc

    for module_name in table_of_content:
        if module_name.startswith(prefix) and '.' not in module_name:
            yield module_name
