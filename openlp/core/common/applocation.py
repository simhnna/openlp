# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2018 OpenLP Developers                                   #
# --------------------------------------------------------------------------- #
# This program is free software; you can redistribute it and/or modify it     #
# under the terms of the GNU General Public License as published by the Free  #
# Software Foundation; version 2 of the License.                              #
#                                                                             #
# This program is distributed in the hope that it will be useful, but WITHOUT #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for    #
# more details.                                                               #
#                                                                             #
# You should have received a copy of the GNU General Public License along     #
# with this program; if not, write to the Free Software Foundation, Inc., 59  #
# Temple Place, Suite 330, Boston, MA 02111-1307 USA                          #
###############################################################################
"""
The :mod:`openlp.core.common.applocation` module provides an utility for OpenLP receiving the data path etc.
"""
import logging
import os
import sys

import openlp
from openlp.core.common import get_frozen_path, is_win, is_macosx
from openlp.core.common.path import Path, create_paths
from openlp.core.common.settings import Settings

if not is_win() and not is_macosx():
    try:
        from xdg import BaseDirectory
        XDG_BASE_AVAILABLE = True
    except ImportError:
        XDG_BASE_AVAILABLE = False

log = logging.getLogger(__name__)

FROZEN_APP_PATH = Path(sys.argv[0]).parent
APP_PATH = Path(openlp.__file__).parent


class AppLocation(object):
    """
    The :class:`AppLocation` class is a static class which retrieves a directory based on the directory type.
    """
    AppDir = 1
    DataDir = 2
    PluginsDir = 3
    VersionDir = 4
    CacheDir = 5
    LanguageDir = 6

    @staticmethod
    def get_directory(dir_type=AppDir):
        """
        Return the appropriate directory according to the directory type.

        :param dir_type: The directory type you want, for instance the data directory. Default *AppLocation.AppDir*
        :return: The requested path
        :rtype: openlp.core.common.path.Path
        """
        if dir_type == AppLocation.AppDir or dir_type == AppLocation.VersionDir:
            return get_frozen_path(FROZEN_APP_PATH, APP_PATH)
        elif dir_type == AppLocation.PluginsDir:
            return get_frozen_path(FROZEN_APP_PATH, APP_PATH) / 'plugins'
        elif dir_type == AppLocation.LanguageDir:
            return get_frozen_path(FROZEN_APP_PATH, _get_os_dir_path(dir_type)) / 'i18n'
        else:
            return _get_os_dir_path(dir_type)

    @staticmethod
    def get_data_path():
        """
        Return the path OpenLP stores all its data under.

        :return: The data path to use.
        :rtype: openlp.core.common.path.Path
        """
        # Check if we have a different data location.
        if Settings().contains('advanced/data path'):
            path = Path(Settings().value('advanced/data path'))
        else:
            path = AppLocation.get_directory(AppLocation.DataDir)
            create_paths(path)
        return path

    @staticmethod
    def get_files(section=None, extension=''):
        """
        Get a list of files from the data files path.

        :param None | str section: Defaults to *None*. The section of code getting the files - used to load from a
        section's data subdirectory.
        :param str extension: Defaults to ''. The extension to search for. For example::
            '.png'
        :return: List of files found.
        :rtype: list[openlp.core.common.path.Path]
        """
        path = AppLocation.get_data_path()
        if section:
            path = path / section
        try:
            file_paths = path.glob('*' + extension)
            return [file_path.relative_to(path) for file_path in file_paths]
        except OSError:
            return []

    @staticmethod
    def get_section_data_path(section):
        """
        Return the path a particular module stores its data under.

        :param str section:
        :rtype: openlp.core.common.path.Path
        """
        path = AppLocation.get_data_path() / section
        create_paths(path)
        return path


def _get_os_dir_path(dir_type):
    """
    Return a path based on which OS and environment we are running in.

    :param dir_type: AppLocation Enum of the requested path type
    :return: The requested path
    :rtype: openlp.core.common.path.Path
    """
    # If running from source, return the language directory from the source directory
    if dir_type == AppLocation.LanguageDir:
        directory = Path(openlp.__file__, '..', '..').resolve() / 'resources'
        if directory.exists():
            return directory
    if is_win():
        openlp_folder_path = Path(os.getenv('APPDATA'), 'openlp')
        if dir_type == AppLocation.DataDir:
            return openlp_folder_path / 'data'
        elif dir_type == AppLocation.LanguageDir:
            return Path(openlp.__file__).parent
        return openlp_folder_path
    elif is_macosx():
        openlp_folder_path = Path(os.getenv('HOME'), 'Library', 'Application Support', 'openlp')
        if dir_type == AppLocation.DataDir:
            return openlp_folder_path / 'Data'
        elif dir_type == AppLocation.LanguageDir:
            return Path(openlp.__file__).parent
        return openlp_folder_path
    else:
        if dir_type == AppLocation.LanguageDir:
            directory = Path('/usr', 'local', 'share', 'openlp')
            if directory.exists():
                return directory
            return Path('/usr', 'share', 'openlp')
        if XDG_BASE_AVAILABLE:
            if dir_type == AppLocation.DataDir:
                return Path(BaseDirectory.xdg_data_home, 'openlp')
            elif dir_type == AppLocation.CacheDir:
                return Path(BaseDirectory.xdg_cache_home, 'openlp')
        if dir_type == AppLocation.DataDir:
            return Path(os.getenv('HOME'), '.openlp', 'data')
        return Path(os.getenv('HOME'), '.openlp')
