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
from json import JSONDecoder, JSONEncoder

from openlp.core.common.path import Path


class OpenLPJsonDecoder(JSONDecoder):
    """
    Implement a custom JSONDecoder to handle Path objects

    Example Usage:
        object = json.loads(json_string, cls=OpenLPJsonDecoder)
    """
    def __init__(self, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, strict=True,
                 object_pairs_hook=None, **kwargs):
        """
        Re-implement __init__ so that we can pass in our object_hook method. Any additional kwargs, are stored in the
        instance and are passed to custom objects upon encoding or decoding.
        """
        self.kwargs = kwargs
        if object_hook is None:
            object_hook = self.custom_object_hook
        super().__init__(object_hook=object_hook, parse_float=parse_float, parse_int=parse_int,
                         parse_constant=parse_constant, strict=strict, object_pairs_hook=object_pairs_hook)

    def custom_object_hook(self, obj):
        """
        Implement a custom Path object decoder.

        :param dict obj: A decoded JSON object
        :return: The original object literal, or a Path object if the object literal contains a key '__Path__'
        :rtype: dict | openlp.core.common.path.Path
        """
        if '__Path__' in obj:
            obj = Path.encode_json(obj, **self.kwargs)
        return obj


class OpenLPJsonEncoder(JSONEncoder):
    """
    Implement a custom JSONEncoder to handle Path objects

    Example Usage:
        json_string = json.dumps(object, cls=OpenLPJsonEncoder)
    """
    def __init__(self, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, sort_keys=False,
                 indent=None, separators=None, default=None, **kwargs):
        """
        Re-implement __init__ so that we can pass in additional kwargs, which are stored in the instance and are passed
        to custom objects upon encoding or decoding.
        """
        self.kwargs = kwargs
        if default is None:
            default = self.custom_default
        super().__init__(skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
                         allow_nan=allow_nan, sort_keys=sort_keys, indent=indent, separators=separators,
                         default=default)

    def custom_default(self, obj):
        """
        Convert any Path objects into a dictionary object which can be serialized.

        :param object obj: The object to convert
        :return: The serializable object
        :rtype: dict
        """
        if isinstance(obj, Path):
            return obj.json_object(**self.kwargs)
        return super().default(obj)
