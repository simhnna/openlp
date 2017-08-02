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

from pathlib import Path


def path_to_str(path):
    """
    A utility function to convert a Path object or NoneType to a string equivalent.

    :param path: The value to convert to a string
    :type: pathlib.Path or None

    :return: An empty string if :param:`path` is None, else a string representation of the :param:`path`
    :rtype: str
    """
    if not isinstance(path, Path) and path is not None:
        raise TypeError('parameter \'path\' must be of type Path or NoneType')
    if path is None:
        return ''
    else:
        return str(path)


def str_to_path(string):
    """
    A utility function to convert a str object to a Path or NoneType.

    This function is of particular use because initating a Path object with an empty string causes the Path object to
    point to the current working directory.

    :param string: The string to convert
    :type string: str

    :return: None if :param:`string` is empty, or a Path object representation of :param:`string`
    :rtype: pathlib.Path or None
    """
    if not isinstance(string, str):
        raise TypeError('parameter \'string\' must be of type str')
    if string == '':
        return None
    return Path(string)
