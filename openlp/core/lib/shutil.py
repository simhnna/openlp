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
""" Patch the shutil methods we use so they accept and return Path objects"""
import shutil

from openlp.core.common.path import path_to_str, str_to_path
from openlp.core.lib import replace_params


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
