"""
    pyexcel_io.exceptions
    ~~~~~~~~~~~~~~~~~~~~~~

    all possible exceptions

    :copyright: (c) 2014-2017 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""


class NoSupportingPluginFound(Exception):
    """raised when an known file extension is seen"""
    pass


class SupportingPluginAvailableButNotInstalled(Exception):
    """raised when a known plugin is not installed"""
    pass


class UpgradePlugin(Exception):
    """raised when a known plugin is not compatible"""
    pass
