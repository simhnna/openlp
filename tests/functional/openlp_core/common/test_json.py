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
"""
Package to test the openlp.core.common.json package.
"""
import json
from unittest import TestCase
from unittest.mock import patch

from openlp.core.common.path import Path
from openlp.core.common.json import OpenLPJsonDecoder, OpenLPJsonEncoder


class TestOpenLPJsonDecoder(TestCase):
    """
    Test the OpenLPJsonDecoder class
    """
    def test_object_hook_path_object(self):
        """
        Test the object_hook method when called with a decoded Path JSON object
        """
        # GIVEN: An instance of OpenLPJsonDecoder
        instance = OpenLPJsonDecoder()

        # WHEN: Calling the object_hook method with a decoded JSON object which contains a Path
        result = instance.object_hook({'__Path__': ['test', 'path']})

        # THEN: A Path object should be returned
        self.assertEqual(result, Path('test', 'path'))

    def test_object_hook_non_path_object(self):
        """
        Test the object_hook method when called with a decoded JSON object
        """
        # GIVEN: An instance of OpenLPJsonDecoder
        instance = OpenLPJsonDecoder()

        # WHEN: Calling the object_hook method with a decoded JSON object which contains a Path
        with patch('openlp.core.common.json.Path') as mocked_path:
            result = instance.object_hook({'key': 'value'})

            # THEN: The object should be returned unchanged and a Path object should not have been initiated
            self.assertEqual(result, {'key': 'value'})
            self.assertFalse(mocked_path.called)

    def test_json_decode(self):
        """
        Test the OpenLPJsonDecoder when decoding a JSON string
        """
        # GIVEN: A JSON encoded string
        json_string = '[{"__Path__": ["test", "path1"]}, {"__Path__": ["test", "path2"]}]'

        # WHEN: Decoding the string using the OpenLPJsonDecoder class
        obj = json.loads(json_string, cls=OpenLPJsonDecoder)

        # THEN: The object returned should be a python version of the JSON string
        self.assertEqual(obj, [Path('test', 'path1'), Path('test', 'path2')])


class TestOpenLPJsonEncoder(TestCase):
    """
    Test the OpenLPJsonEncoder class
    """
    def test_default_path_object(self):
        """
        Test the default method when called with a Path object
        """
        # GIVEN: An instance of OpenLPJsonEncoder
        instance = OpenLPJsonEncoder()

        # WHEN: Calling the default method with a Path object
        result = instance.default(Path('test', 'path'))

        # THEN: A dictionary object that can be JSON encoded should be returned
        self.assertEqual(result, {'__Path__': ('test', 'path')})

    def test_default_non_path_object(self):
        """
        Test the default method when called with a object other than a Path object
        """
        with patch('openlp.core.common.json.JSONEncoder.default') as mocked_super_default:

            # GIVEN: An instance of OpenLPJsonEncoder
            instance = OpenLPJsonEncoder()

            # WHEN: Calling the default method with a object other than a Path object
            instance.default('invalid object')

            # THEN: default method of the super class should have been called
            mocked_super_default.assert_called_once_with('invalid object')

    def test_json_encode(self):
        """
        Test the OpenLPJsonDEncoder when encoding an object conatining Path objects
        """
        # GIVEN: A list of Path objects
        obj = [Path('test', 'path1'), Path('test', 'path2')]

        # WHEN: Encoding the object using the OpenLPJsonEncoder class
        json_string = json.dumps(obj, cls=OpenLPJsonEncoder)

        # THEN: The JSON string return should be a representation of the object encoded
        self.assertEqual(json_string, '[{"__Path__": ["test", "path1"]}, {"__Path__": ["test", "path2"]}]')
