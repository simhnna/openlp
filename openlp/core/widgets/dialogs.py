# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2017 OpenLP Developers                                   #
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
""" Patch the QFileDialog so it accepts and returns Path objects"""
from PyQt5 import QtWidgets

from openlp.core.common.path import path_to_str, replace_params, str_to_path


class FileDialog(QtWidgets.QFileDialog):
    @classmethod
    def getExistingDirectory(cls, *args, **kwargs):
        """
        Wraps `getExistingDirectory` so that it can be called with, and return Path objects

        :type parent: QtWidgets.QWidget | None
        :type caption: str
        :type directory: openlp.core.common.path.Path
        :type options: QtWidgets.QFileDialog.Options
        :rtype: tuple[openlp.core.common.path.Path, str]
        """
        args, kwargs = replace_params(args, kwargs, ((2, 'directory', path_to_str),))

        return_value = super().getExistingDirectory(*args, **kwargs)

        # getExistingDirectory returns a str that represents the path. The string is empty if the user cancels the
        # dialog.
        return str_to_path(return_value)

    @classmethod
    def getOpenFileName(cls, *args, **kwargs):
        """
        Wraps `getOpenFileName` so that it can be called with, and return Path objects

        :type parent: QtWidgets.QWidget | None
        :type caption: str
        :type directory: openlp.core.common.path.Path
        :type filter: str
        :type initialFilter: str
        :type options: QtWidgets.QFileDialog.Options
        :rtype: tuple[openlp.core.common.path.Path, str]
        """
        args, kwargs = replace_params(args, kwargs, ((2, 'directory', path_to_str),))

        file_name, selected_filter = super().getOpenFileName(*args, **kwargs)

        # getOpenFileName returns a tuple. The first item is a str that represents the path. The string is empty if
        # the user cancels the dialog.
        return str_to_path(file_name), selected_filter

    @classmethod
    def getOpenFileNames(cls, *args, **kwargs):
        """
        Wraps `getOpenFileNames` so that it can be called with, and return Path objects

        :type parent: QtWidgets.QWidget | None
        :type caption: str
        :type directory: openlp.core.common.path.Path
        :type filter: str
        :type initialFilter: str
        :type options: QtWidgets.QFileDialog.Options
        :rtype: tuple[list[openlp.core.common.path.Path], str]
        """
        args, kwargs = replace_params(args, kwargs, ((2, 'directory', path_to_str),))

        file_names, selected_filter = super().getOpenFileNames(*args, **kwargs)

        # getSaveFileName returns a tuple. The first item is a list of str's that represents the path. The list is
        # empty if the user cancels the dialog.
        paths = [str_to_path(path) for path in file_names]
        return paths, selected_filter

    @classmethod
    def getSaveFileName(cls, *args, **kwargs):
        """
        Wraps `getSaveFileName` so that it can be called with, and return Path objects

        :type parent: QtWidgets.QWidget | None
        :type caption: str
        :type directory: openlp.core.common.path.Path
        :type filter: str
        :type initialFilter: str
        :type options: QtWidgets.QFileDialog.Options
        :rtype: tuple[openlp.core.common.path.Path | None, str]
        """
        args, kwargs = replace_params(args, kwargs, ((2, 'directory', path_to_str),))

        file_name, selected_filter = super().getSaveFileName(*args, **kwargs)

        # getSaveFileName returns a tuple. The first item represents the path as a str. The string is empty if the user
        # cancels the dialog.
        return str_to_path(file_name), selected_filter
