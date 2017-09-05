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
Package to test the openlp.core.common.path package.
"""
import os
from unittest import TestCase

from openlp.core.common.path import Path, path_to_str, str_to_path


class TestPath(TestCase):
    """
    Tests for the :mod:`openlp.core.common.path` module
    """

    def test_path_to_str_type_error(self):
        """
        Test that `path_to_str` raises a type error when called with an invalid type
        """
        # GIVEN: The `path_to_str` function
        # WHEN: Calling `path_to_str` with an invalid Type
        # THEN: A TypeError should have been raised
        with self.assertRaises(TypeError):
            path_to_str(str())

    def test_path_to_str_none(self):
        """
        Test that `path_to_str` correctly converts the path parameter when passed with None
        """
        # GIVEN: The `path_to_str` function
        # WHEN: Calling the `path_to_str` function with None
        result = path_to_str(None)

        # THEN: `path_to_str` should return an empty string
        self.assertEqual(result, '')

    def test_path_to_str_path_object(self):
        """
        Test that `path_to_str` correctly converts the path parameter when passed a Path object
        """
        # GIVEN: The `path_to_str` function
        # WHEN: Calling the `path_to_str` function with a Path object
        result = path_to_str(Path('test/path'))

        # THEN: `path_to_str` should return a string representation of the Path object
        self.assertEqual(result, os.path.join('test', 'path'))

    def test_str_to_path_type_error(self):
        """
        Test that `str_to_path` raises a type error when called with an invalid type
        """
        # GIVEN: The `str_to_path` function
        # WHEN: Calling `str_to_path` with an invalid Type
        # THEN: A TypeError should have been raised
        with self.assertRaises(TypeError):
            str_to_path(Path())

    def test_str_to_path_empty_str(self):
        """
        Test that `str_to_path` correctly converts the string parameter when passed with and empty string
        """
        # GIVEN: The `str_to_path` function
        # WHEN: Calling the `str_to_path` function with None
        result = str_to_path('')

        # THEN: `path_to_str` should return None
        self.assertEqual(result, None)

    def test_path_encode_json(self):
        """
        Test that `Path.encode_json` returns a Path object from a dictionary representation of a Path object decoded
        from JSON
        """
        # GIVEN: A Path object from openlp.core.common.path
        # WHEN: Calling encode_json, with a dictionary representation
        path = Path.encode_json({'__Path__': ['path', 'to', 'fi.le']}, extra=1, args=2)

        # THEN: A Path object should have been returned
        self.assertEqual(path, Path('path', 'to', 'fi.le'))

    def test_path_encode_json_base_path(self):
        """
        Test that `Path.encode_json` returns a Path object from a dictionary representation of a Path object decoded
        from JSON when the base_path arg is supplied.
        """
        # GIVEN: A Path object from openlp.core.common.path
        # WHEN: Calling encode_json, with a dictionary representation
        path = Path.encode_json({'__Path__': ['path', 'to', 'fi.le']}, base_path=Path('/base'))

        # THEN: A Path object should have been returned with an absolute path
        self.assertEqual(path, Path('/', 'base', 'path', 'to', 'fi.le'))

    def test_path_json_object(self):
        """
        Test that `Path.json_object` creates a JSON decode-able object from a Path object
        """
        # GIVEN: A Path object from openlp.core.common.path
        path = Path('/base', 'path', 'to', 'fi.le')

        # WHEN: Calling json_object
        obj = path.json_object(extra=1, args=2)

        # THEN: A JSON decodable object should have been returned.
        self.assertEqual(obj, {'__Path__': ('/', 'base', 'path', 'to', 'fi.le')})

    def test_path_json_object_base_path(self):
        """
        Test that `Path.json_object` creates a JSON decode-able object from a Path object, that is relative to the
        base_path
        """
        # GIVEN: A Path object from openlp.core.common.path
        path = Path('/base', 'path', 'to', 'fi.le')

        # WHEN: Calling json_object with a base_path
        obj = path.json_object(base_path=Path('/', 'base'))

        # THEN: A JSON decodable object should have been returned.
        self.assertEqual(obj, {'__Path__': ('path', 'to', 'fi.le')})
