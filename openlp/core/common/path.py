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
import logging
import shutil
from contextlib import suppress

from openlp.core.common import is_win

if is_win():
    from pathlib import WindowsPath as PathVariant
else:
    from pathlib import PosixPath as PathVariant

log = logging.getLogger(__name__)


class Path(PathVariant):
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

    def rmtree(self, *args, **kwargs):
        shutil.rmtree(str(self), *args, **kwargs)


def replace_params(args, kwargs, params):
    """
    Apply a transformation function to the specified args or kwargs

    :param tuple args: Positional arguments
    :param dict kwargs: Key Word arguments
    :param params: A tuple of tuples with the position and the key word to replace.
    :return: The modified positional and keyword arguments
    :rtype: tuple[tuple, dict]


    Usage:
        Take a method with the following signature, and assume we which to apply the str function to arg2:
            def method(arg1=None, arg2=None, arg3=None)

        As arg2 can be specified postitionally as the second argument (1 with a zero index) or as a keyword, the we
        would call this function as follows:

        replace_params(args, kwargs, ((1, 'arg2', str),))
    """
    args = list(args)
    for position, key_word, transform in params:
        if len(args) > position:
            args[position] = transform(args[position])
        elif key_word in kwargs:
            kwargs[key_word] = transform(kwargs[key_word])
    return tuple(args), kwargs


def copy(*args, **kwargs):
    """
    Wraps :func:`shutil.copy` so that we can accept Path objects.

    :param src openlp.core.common.path.Path: Takes a Path object which is then converted to a str object
    :param dst openlp.core.common.path.Path: Takes a Path object which is then converted to a str object
    :return: Converts the str object received from :func:`shutil.copy` to a Path or NoneType object
    :rtype: openlp.core.common.path.Path | None

    See the following link for more information on the other parameters:
        https://docs.python.org/3/library/shutil.html#shutil.copy
    """

    args, kwargs = replace_params(args, kwargs, ((0, 'src', path_to_str), (1, 'dst', path_to_str)))

    return str_to_path(shutil.copy(*args, **kwargs))


def copyfile(*args, **kwargs):
    """
    Wraps :func:`shutil.copyfile` so that we can accept Path objects.

    :param openlp.core.common.path.Path src: Takes a Path object which is then converted to a str object
    :param openlp.core.common.path.Path dst: Takes a Path object which is then converted to a str object
    :return: Converts the str object received from :func:`shutil.copyfile` to a Path or NoneType object
    :rtype: openlp.core.common.path.Path | None

    See the following link for more information on the other parameters:
        https://docs.python.org/3/library/shutil.html#shutil.copyfile
    """

    args, kwargs = replace_params(args, kwargs, ((0, 'src', path_to_str), (1, 'dst', path_to_str)))

    return str_to_path(shutil.copyfile(*args, **kwargs))


def copytree(*args, **kwargs):
    """
    Wraps :func:shutil.copytree` so that we can accept Path objects.

    :param openlp.core.common.path.Path src : Takes a Path object which is then converted to a str object
    :param openlp.core.common.path.Path dst: Takes a Path object which is then converted to a str object
    :return: Converts the str object received from :func:`shutil.copytree` to a Path or NoneType object
    :rtype: openlp.core.common.path.Path | None

    See the following link for more information on the other parameters:
        https://docs.python.org/3/library/shutil.html#shutil.copytree
    """

    args, kwargs = replace_params(args, kwargs, ((0, 'src', path_to_str), (1, 'dst', path_to_str)))

    return str_to_path(shutil.copytree(*args, **kwargs))


def rmtree(*args, **kwargs):
    """
    Wraps :func:shutil.rmtree` so that we can accept Path objects.

    :param openlp.core.common.path.Path path: Takes a Path object which is then converted to a str object
    :return: Passes the return from :func:`shutil.rmtree` back
    :rtype: None

    See the following link for more information on the other parameters:
        https://docs.python.org/3/library/shutil.html#shutil.rmtree
    """

    args, kwargs = replace_params(args, kwargs, ((0, 'path', path_to_str),))

    return shutil.rmtree(*args, **kwargs)


def which(*args, **kwargs):
    """
    Wraps :func:shutil.which` so that it return a Path objects.

    :rtype: openlp.core.common.Path

    See the following link for more information on the other parameters:
        https://docs.python.org/3/library/shutil.html#shutil.which
    """
    file_name = shutil.which(*args, **kwargs)
    if file_name:
        return str_to_path(file_name)
    return None


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


def create_paths(*paths, **kwargs):
    """
    Create one or more paths

    :param openlp.core.common.path.Path paths: The paths to create
    :param bool do_not_log: To not log anything. This is need for the start up, when the log isn't ready.
    :rtype: None
    """
    for path in paths:
        if not kwargs.get('do_not_log', False):
            log.debug('create_path {path}'.format(path=path))
        try:
            if not path.exists():
                path.mkdir(parents=True)
        except OSError:
            if not kwargs.get('do_not_log', False):
                log.exception('failed to check if directory exists or create directory')


def files_to_paths(file_names):
    """
    Convert a list of file names in to a list of file paths.

    :param list[str] file_names: The list of file names to convert.
    :return: The list converted to file paths
    :rtype: openlp.core.common.path.Path
    """
    if file_names:
        return [str_to_path(file_name) for file_name in file_names]
