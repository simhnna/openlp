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
Package to test the openlp.core.common.path package.
"""
import os
from unittest import TestCase
from unittest.mock import ANY, MagicMock, patch

from openlp.core.common.path import Path, copy, copyfile, copytree, create_paths, path_to_str, replace_params, \
    str_to_path, which, files_to_paths


class TestShutil(TestCase):
    """
    Tests for the :mod:`openlp.core.common.path` module
    """
    def test_replace_params_no_params(self):
        """
        Test replace_params when called with and empty tuple instead of parameters to replace
        """
        # GIVEN: Some test data
        test_args = (1, 2)
        test_kwargs = {'arg3': 3, 'arg4': 4}
        test_params = tuple()

        # WHEN: Calling replace_params
        result_args, result_kwargs = replace_params(test_args, test_kwargs, test_params)

        # THEN: The positional and keyword args should not have changed
        assert test_args == result_args
        assert test_kwargs == result_kwargs

    def test_replace_params_params(self):
        """
        Test replace_params when given a positional and a keyword argument to change
        """
        # GIVEN: Some test data
        test_args = (1, 2)
        test_kwargs = {'arg3': 3, 'arg4': 4}
        test_params = ((1, 'arg2', str), (2, 'arg3', str))

        # WHEN: Calling replace_params
        result_args, result_kwargs = replace_params(test_args, test_kwargs, test_params)

        # THEN: The positional and keyword args should have have changed
        assert result_args == (1, '2')
        assert result_kwargs == {'arg3': '3', 'arg4': 4}

    def test_copy(self):
        """
        Test :func:`openlp.core.common.path.copy`
        """
        # GIVEN: A mocked `shutil.copy` which returns a test path as a string
        with patch('openlp.core.common.path.shutil.copy', return_value=os.path.join('destination', 'test', 'path')) \
                as mocked_shutil_copy:

            # WHEN: Calling :func:`openlp.core.common.path.copy` with the src and dst parameters as Path object types
            result = copy(Path('source', 'test', 'path'), Path('destination', 'test', 'path'))

            # THEN: :func:`shutil.copy` should have been called with the str equivalents of the Path objects.
            #       :func:`openlp.core.common.path.copy` should return the str type result of calling
            #       :func:`shutil.copy` as a Path object.
            mocked_shutil_copy.assert_called_once_with(os.path.join('source', 'test', 'path'),
                                                       os.path.join('destination', 'test', 'path'))
            assert result == Path('destination', 'test', 'path')

    def test_copy_follow_optional_params(self):
        """
        Test :func:`openlp.core.common.path.copy` when follow_symlinks is set to false
        """
        # GIVEN: A mocked `shutil.copy`
        with patch('openlp.core.common.path.shutil.copy', return_value='') as mocked_shutil_copy:

            # WHEN: Calling :func:`openlp.core.common.path.copy` with :param:`follow_symlinks` set to False
            copy(Path('source', 'test', 'path'), Path('destination', 'test', 'path'), follow_symlinks=False)

            # THEN: :func:`shutil.copy` should have been called with :param:`follow_symlinks` set to false
            mocked_shutil_copy.assert_called_once_with(ANY, ANY, follow_symlinks=False)

    def test_copyfile(self):
        """
        Test :func:`openlp.core.common.path.copyfile`
        """
        # GIVEN: A mocked :func:`shutil.copyfile` which returns a test path as a string
        with patch('openlp.core.common.path.shutil.copyfile',
                   return_value=os.path.join('destination', 'test', 'path')) as mocked_shutil_copyfile:

            # WHEN: Calling :func:`openlp.core.common.path.copyfile` with the src and dst parameters as Path object
            #       types
            result = copyfile(Path('source', 'test', 'path'), Path('destination', 'test', 'path'))

            # THEN: :func:`shutil.copyfile` should have been called with the str equivalents of the Path objects.
            #       :func:`openlp.core.common.path.copyfile` should return the str type result of calling
            #       :func:`shutil.copyfile` as a Path object.
            mocked_shutil_copyfile.assert_called_once_with(os.path.join('source', 'test', 'path'),
                                                           os.path.join('destination', 'test', 'path'))
            assert result == Path('destination', 'test', 'path')

    def test_copyfile_optional_params(self):
        """
        Test :func:`openlp.core.common.path.copyfile` when follow_symlinks is set to false
        """
        # GIVEN: A mocked :func:`shutil.copyfile`
        with patch('openlp.core.common.path.shutil.copyfile', return_value='') as mocked_shutil_copyfile:

            # WHEN: Calling :func:`openlp.core.common.path.copyfile` with :param:`follow_symlinks` set to False
            copyfile(Path('source', 'test', 'path'), Path('destination', 'test', 'path'), follow_symlinks=False)

            # THEN: :func:`shutil.copyfile` should have been called with the optional parameters, with out any of the
            #       values being modified
            mocked_shutil_copyfile.assert_called_once_with(ANY, ANY, follow_symlinks=False)

    def test_copytree(self):
        """
        Test :func:`openlp.core.common.path.copytree`
        """
        # GIVEN: A mocked :func:`shutil.copytree` which returns a test path as a string
        with patch('openlp.core.common.path.shutil.copytree',
                   return_value=os.path.join('destination', 'test', 'path')) as mocked_shutil_copytree:

            # WHEN: Calling :func:`openlp.core.common.path.copytree` with the src and dst parameters as Path object
            #       types
            result = copytree(Path('source', 'test', 'path'), Path('destination', 'test', 'path'))

            # THEN: :func:`shutil.copytree` should have been called with the str equivalents of the Path objects.
            #       :func:`openlp.core.common.path.copytree` should return the str type result of calling
            #       :func:`shutil.copytree` as a Path object.
            mocked_shutil_copytree.assert_called_once_with(os.path.join('source', 'test', 'path'),
                                                           os.path.join('destination', 'test', 'path'))
            assert result == Path('destination', 'test', 'path')

    def test_copytree_optional_params(self):
        """
        Test :func:`openlp.core.common.path.copytree` when optional parameters are passed
        """
        # GIVEN: A mocked :func:`shutil.copytree`
        with patch('openlp.core.common.path.shutil.copytree', return_value='') as mocked_shutil_copytree:
            mocked_ignore = MagicMock()
            mocked_copy_function = MagicMock()

            # WHEN: Calling :func:`openlp.core.common.path.copytree` with the optional parameters set
            copytree(Path('source', 'test', 'path'), Path('destination', 'test', 'path'), symlinks=True,
                     ignore=mocked_ignore, copy_function=mocked_copy_function, ignore_dangling_symlinks=True)

            # THEN: :func:`shutil.copytree` should have been called with the optional parameters, with out any of the
            #       values being modified
            mocked_shutil_copytree.assert_called_once_with(ANY, ANY, symlinks=True, ignore=mocked_ignore,
                                                           copy_function=mocked_copy_function,
                                                           ignore_dangling_symlinks=True)

    def test_rmtree(self):
        """
        Test :func:`rmtree`
        """
        # GIVEN: A mocked :func:`shutil.rmtree` and a test Path object
        with patch('openlp.core.common.path.shutil.rmtree', return_value=None) as mocked_shutil_rmtree:
            path = Path('test', 'path')

            # WHEN: Calling :func:`openlp.core.common.path.rmtree` with the path parameter as Path object type
            path.rmtree()

            # THEN: :func:`shutil.rmtree` should have been called with the str equivalents of the Path object.
            mocked_shutil_rmtree.assert_called_once_with(
                os.path.join('test', 'path'), False, None)

    def test_rmtree_optional_params(self):
        """
        Test :func:`openlp.core.common.path.rmtree` when optional parameters are passed
        """
        # GIVEN: A mocked :func:`shutil.rmtree` and a test Path object.
        with patch('openlp.core.common.path.shutil.rmtree', return_value=None) as mocked_shutil_rmtree:
            path = Path('test', 'path')
            mocked_on_error = MagicMock()

            # WHEN: Calling :func:`openlp.core.common.path.rmtree` with :param:`ignore_errors` set to True and
            #       :param:`onerror` set to a mocked object
            path.rmtree(ignore_errors=True, onerror=mocked_on_error)

            # THEN: :func:`shutil.rmtree` should have been called with the optional parameters, with out any of the
            #       values being modified
            mocked_shutil_rmtree.assert_called_once_with(
                os.path.join('test', 'path'), True, mocked_on_error)

    def test_which_no_command(self):
        """
        Test :func:`openlp.core.common.path.which` when the command is not found.
        """
        # GIVEN: A mocked :func:`shutil.which` when the command is not found.
        with patch('openlp.core.common.path.shutil.which', return_value=None) as mocked_shutil_which:

            # WHEN: Calling :func:`openlp.core.common.path.which` with a command that does not exist.
            result = which('no_command')

            # THEN: :func:`shutil.which` should have been called with the command, and :func:`which` should return None.
            mocked_shutil_which.assert_called_once_with('no_command')
        assert result is None

    def test_which_command(self):
        """
        Test :func:`openlp.core.common.path.which` when a command has been found.
        """
        # GIVEN: A mocked :func:`shutil.which` when the command is found.
        with patch('openlp.core.common.path.shutil.which',
                   return_value=os.path.join('path', 'to', 'command')) as mocked_shutil_which:

            # WHEN: Calling :func:`openlp.core.common.path.which` with a command that exists.
            result = which('command')

            # THEN: :func:`shutil.which` should have been called with the command, and :func:`which` should return a
            #       Path object equivalent of the command path.
            mocked_shutil_which.assert_called_once_with('command')
            assert result == Path('path', 'to', 'command')


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
        assert result == ''

    def test_path_to_str_path_object(self):
        """
        Test that `path_to_str` correctly converts the path parameter when passed a Path object
        """
        # GIVEN: The `path_to_str` function
        # WHEN: Calling the `path_to_str` function with a Path object
        result = path_to_str(Path('test/path'))

        # THEN: `path_to_str` should return a string representation of the Path object
        assert result == os.path.join('test', 'path')

    def test_str_to_path_type_error(self):
        """
        Test that `str_to_path` returns None if called with invalid information
        """
        # GIVEN: The `str_to_path` function
        # WHEN: Calling `str_to_path` with an invalid Type
        # THEN: None is returned
        assert str_to_path(Path()) is None

    def test_str_to_path_empty_str(self):
        """
        Test that `str_to_path` correctly converts the string parameter when passed with and empty string
        """
        # GIVEN: The `str_to_path` function
        # WHEN: Calling the `str_to_path` function with None
        result = str_to_path('')

        # THEN: `path_to_str` should return None
        assert result is None

    def test_path_encode_json(self):
        """
        Test that `Path.encode_json` returns a Path object from a dictionary representation of a Path object decoded
        from JSON
        """
        # GIVEN: A Path object from openlp.core.common.path
        # WHEN: Calling encode_json, with a dictionary representation
        path = Path.encode_json({'__Path__': ['path', 'to', 'fi.le']}, extra=1, args=2)

        # THEN: A Path object should have been returned
        assert path == Path('path', 'to', 'fi.le')

    def test_path_encode_json_base_path(self):
        """
        Test that `Path.encode_json` returns a Path object from a dictionary representation of a Path object decoded
        from JSON when the base_path arg is supplied.
        """
        # GIVEN: A Path object from openlp.core.common.path
        # WHEN: Calling encode_json, with a dictionary representation
        path = Path.encode_json({'__Path__': ['path', 'to', 'fi.le']}, base_path=Path('/base'))

        # THEN: A Path object should have been returned with an absolute path
        assert path == Path('/', 'base', 'path', 'to', 'fi.le')

    def test_path_json_object(self):
        """
        Test that `Path.json_object` creates a JSON decode-able object from a Path object
        """
        # GIVEN: A Path object from openlp.core.common.path
        path = Path('/base', 'path', 'to', 'fi.le')

        # WHEN: Calling json_object
        obj = path.json_object(extra=1, args=2)

        # THEN: A JSON decodable object should have been returned.
        assert obj == {'__Path__': ('/', 'base', 'path', 'to', 'fi.le')}

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
        assert obj == {'__Path__': ('path', 'to', 'fi.le')}

    def test_create_paths_dir_exists(self):
        """
        Test the create_paths() function when the path already exists
        """
        # GIVEN: A `Path` to check with patched out mkdir and exists methods
        mocked_path = MagicMock()
        mocked_path.exists.return_value = True

        # WHEN: `create_paths` is called and the path exists
        create_paths(mocked_path)

        # THEN: The function should not attempt to create the directory
        mocked_path.exists.assert_called_once_with()
        assert mocked_path.mkdir.call_count == 0, 'mkdir should not have been called'

    def test_create_paths_dir_doesnt_exists(self):
        """
        Test the create_paths() function when the path does not already exist
        """
        # GIVEN: A `Path` to check with patched out mkdir and exists methods
        mocked_path = MagicMock()
        mocked_path.exists.return_value = False

        # WHEN: `create_paths` is called and the path does not exist
        create_paths(mocked_path)

        # THEN: The directory should have been created
        mocked_path.exists.assert_called_once_with()
        mocked_path.mkdir.assert_called_once_with(parents=True)

    @patch('openlp.core.common.path.log')
    def test_create_paths_dir_io_error(self, mocked_logger):
        """
        Test the create_paths() when an OSError is raised
        """
        # GIVEN: A `Path` to check with patched out mkdir and exists methods
        mocked_path = MagicMock()
        mocked_path.exists.side_effect = OSError('Cannot make directory')

        # WHEN: An OSError is raised when checking the if the path exists.
        create_paths(mocked_path)

        # THEN: The Error should have been logged
        mocked_logger.exception.assert_called_once_with('failed to check if directory exists or create directory')

    def test_create_paths_dir_value_error(self):
        """
        Test the create_paths() when an error other than OSError is raised
        """
        # GIVEN: A `Path` to check with patched out mkdir and exists methods
        mocked_path = MagicMock()
        mocked_path.exists.side_effect = ValueError('Some other error')

        # WHEN: Some other exception is raised
        try:
            create_paths(mocked_path)
            assert False, 'create_paths should have thrown an exception'
        except:
            # THEN: `create_paths` raises an exception
            pass

    def test_files_to_paths(self):
        """
        Test the files_to_paths() method
        """
        # GIVEN: A list of string filenames
        test_files = ['/tmp/openlp/file1.txt', '/tmp/openlp/file2.txt']

        # WHEN: files_to_paths is called
        result = files_to_paths(test_files)

        # THEN: The result should be a list of Paths
        assert result == [Path('/tmp/openlp/file1.txt'), Path('/tmp/openlp/file2.txt')]
