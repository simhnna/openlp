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
import pathlib
from contextlib import suppress

from openlp.core.common import is_win


if is_win():
    path_variant = pathlib.WindowsPath
else:
    path_variant = pathlib.PosixPath


def path_to_str(path=None):
    """
    A utility function to convert a Path object or NoneType to a string equivalent.

    :param openlp.core.common.path.Path | None path: The value to convert to a string
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

    :param str string: The string to convert
    :return: None if :param:`string` is empty, or a Path object representation of :param:`string`
    :rtype: openlp.core.common.path.Path | None
    """
    if not isinstance(string, str):
        raise TypeError('parameter \'string\' must be of type str')
    if string == '':
        return None
    return Path(string)


class Path(path_variant):
    """
    Subclass pathlib.Path, so we can add json conversion methods
    """
    @staticmethod
    def encode_json(obj, base_path=None, **kwargs):
        """
        Create a Path object from a dictionary representation. The dictionary has been constructed by JSON encoding of
        a JSON reprensation of a Path object.

        :param dict[str] obj: The dictionary representation
        :param openlp.core.common.path.Path base_path: If specified, an absolute path to base the relative path off of.
        :param kwargs: Contains any extra parameters. Not used!
        :return: The reconstructed Path object
        :rtype: openlp.core.common.path.Path
        """
        path = Path(*obj['__Path__'])
        if base_path and not path.is_absolute():
            return base_path / path
        return path

    def json_object(self, base_path=None, **kwargs):
        """
        Create a dictionary that can be JSON decoded.

        :param openlp.core.common.path.Path base_path: If specified, an absolute path to make a relative path from.
        :param kwargs: Contains any extra parameters. Not used!
        :return: The dictionary representation of this Path object.
        :rtype: dict[tuple]
        """
        path = self
        if base_path:
            with suppress(ValueError):
                path = path.relative_to(base_path)
        return {'__Path__': path.parts}
