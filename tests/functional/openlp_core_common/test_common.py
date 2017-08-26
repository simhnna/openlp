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
Functional tests to test the AppLocation class and related methods.
"""
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from openlp.core import common
from openlp.core.common import check_directory_exists, clean_button_text, de_hump, extension_loader, is_macosx, \
    is_linux, is_win, path_to_module, trace_error_handler, translate


class TestCommonFunctions(TestCase):
    """
    A test suite to test out various functions in the openlp.core.common module.
    """
    def test_check_directory_exists_dir_exists(self):
        """
        Test the check_directory_exists() function when the path already exists
        """
        # GIVEN: A `Path` to check with patched out mkdir and exists methods
        with patch.object(Path, 'exists') as mocked_exists, \
                patch.object(Path, 'mkdir') as mocked_mkdir, \
                patch('openlp.core.common.log'):

            # WHEN: `check_directory_exists` is called and the path exists
            mocked_exists.return_value = True
            check_directory_exists(Path('existing', 'directory'))

            # THEN: The function should not attempt to create the directory
            mocked_exists.assert_called_with()
            self.assertFalse(mocked_mkdir.called)

    def test_check_directory_exists_dir_doesnt_exists(self):
        """
        Test the check_directory_exists() function when the path does not already exist
        """
        # GIVEN: A `Path` to check with patched out mkdir and exists methods
        with patch.object(Path, 'exists') as mocked_exists, \
                patch.object(Path, 'mkdir') as mocked_mkdir, \
                patch('openlp.core.common.log'):

            # WHEN: `check_directory_exists` is called and the path does not exist
            mocked_exists.return_value = False
            check_directory_exists(Path('existing', 'directory'))

            # THEN: The directory should have been created
            mocked_exists.assert_called_with()
            mocked_mkdir.assert_called_with(parents=True)

    def test_check_directory_exists_dir_io_error(self):
        """
        Test the check_directory_exists() when an IOError is raised
        """
        # GIVEN: A `Path` to check with patched out mkdir and exists methods
        with patch.object(Path, 'exists') as mocked_exists, \
                patch.object(Path, 'mkdir'), \
                patch('openlp.core.common.log') as mocked_logger:

            # WHEN: An IOError is raised when checking the if the path exists.
            mocked_exists.side_effect = IOError()
            check_directory_exists(Path('existing', 'directory'))

            # THEN: The Error should have been logged
            mocked_logger.exception.assert_called_once_with('failed to check if directory exists or create directory')

    def test_check_directory_exists_dir_value_error(self):
        """
        Test the check_directory_exists() when an error other than IOError is raised
        """
        # GIVEN: A `Path` to check with patched out mkdir and exists methods
        with patch.object(Path, 'exists') as mocked_exists, \
                patch.object(Path, 'mkdir'), \
                patch('openlp.core.common.log'):

            # WHEN: Some other exception is raised
            mocked_exists.side_effect = ValueError()

            # THEN: `check_directory_exists` raises an exception
            self.assertRaises(ValueError, check_directory_exists, Path('existing', 'directory'))

    def test_extension_loader_no_files_found(self):
        """
        Test the `extension_loader` function when no files are found
        """
        # GIVEN: A mocked `Path.glob` method which does not match any files
        with patch('openlp.core.common.AppLocation.get_directory', return_value=Path('/', 'app', 'dir', 'openlp')), \
                patch.object(Path, 'glob', return_value=[]), \
                patch('openlp.core.common.importlib.import_module') as mocked_import_module:

            # WHEN: Calling `extension_loader`
            extension_loader('glob', ['file2.py', 'file3.py'])

            # THEN: `extension_loader` should not try to import any files
            self.assertFalse(mocked_import_module.called)

    def test_extension_loader_files_found(self):
        """
        Test the `extension_loader` function when it successfully finds and loads some files
        """
        # GIVEN: A mocked `Path.glob` method which returns a list of files
        with patch('openlp.core.common.AppLocation.get_directory', return_value=Path('/', 'app', 'dir', 'openlp')), \
                patch.object(Path, 'glob', return_value=[
                    Path('/', 'app', 'dir', 'openlp', 'import_dir', 'file1.py'),
                    Path('/', 'app', 'dir', 'openlp', 'import_dir', 'file2.py'),
                    Path('/', 'app', 'dir', 'openlp', 'import_dir', 'file3.py'),
                    Path('/', 'app', 'dir', 'openlp', 'import_dir', 'file4.py')]), \
                patch('openlp.core.common.importlib.import_module') as mocked_import_module:

            # WHEN: Calling `extension_loader` with a list of files to exclude
            extension_loader('glob', ['file2.py', 'file3.py'])

            # THEN: `extension_loader` should only try to import the files that are matched by the blob, excluding the
            #       files listed in the `excluded_files` argument
            mocked_import_module.assert_has_calls([call('openlp.import_dir.file1'), call('openlp.import_dir.file4')])

    def test_extension_loader_import_error(self):
        """
        Test the `extension_loader` function when `SourceFileLoader` raises a `ImportError`
        """
        # GIVEN: A mocked `import_module` which raises an `ImportError`
        with patch('openlp.core.common.AppLocation.get_directory', return_value=Path('/', 'app', 'dir', 'openlp')), \
                patch.object(Path, 'glob', return_value=[
                    Path('/', 'app', 'dir', 'openlp', 'import_dir', 'file1.py')]), \
                patch('openlp.core.common.importlib.import_module', side_effect=ImportError()), \
                patch('openlp.core.common.log') as mocked_logger:

            # WHEN: Calling `extension_loader`
            extension_loader('glob')

            # THEN: The `ImportError` should be caught and logged
            self.assertTrue(mocked_logger.warning.called)

    def test_extension_loader_os_error(self):
        """
        Test the `extension_loader` function when `import_module` raises a `ImportError`
        """
        # GIVEN: A mocked `SourceFileLoader` which raises an `OSError`
        with patch('openlp.core.common.AppLocation.get_directory', return_value=Path('/', 'app', 'dir', 'openlp')), \
                patch.object(Path, 'glob', return_value=[
                    Path('/', 'app', 'dir', 'openlp', 'import_dir', 'file1.py')]), \
                patch('openlp.core.common.importlib.import_module', side_effect=OSError()), \
                patch('openlp.core.common.log') as mocked_logger:

            # WHEN: Calling `extension_loader`
            extension_loader('glob')

            # THEN: The `OSError` should be caught and logged
            self.assertTrue(mocked_logger.warning.called)

    def test_de_hump_conversion(self):
        """
        Test the de_hump function with a class name
        """
        # GIVEN: a Class name in Camel Case
        string = "MyClass"

        # WHEN: we call de_hump
        new_string = de_hump(string)

        # THEN: the new string should be converted to python format
        self.assertEqual(new_string, "my_class", 'The class name should have been converted')

    def test_de_hump_static(self):
        """
        Test the de_hump function with a python string
        """
        # GIVEN: a Class name in Camel Case
        string = "my_class"

        # WHEN: we call de_hump
        new_string = de_hump(string)

        # THEN: the new string should be converted to python format
        self.assertEqual(new_string, "my_class", 'The class name should have been preserved')

    def test_path_to_module(self):
        """
        Test `path_to_module` when supplied with a `Path` object
        """
        # GIVEN: A `Path` object
        path = Path('core', 'ui', 'media', 'webkitplayer.py')

        # WHEN: Calling path_to_module with the `Path` object
        result = path_to_module(path)

        # THEN: path_to_module should return the module name
        self.assertEqual(result, 'openlp.core.ui.media.webkitplayer')

    def test_trace_error_handler(self):
        """
        Test the trace_error_handler() method
        """
        # GIVEN: Mocked out objects
        with patch('openlp.core.common.traceback') as mocked_traceback:
            mocked_traceback.extract_stack.return_value = [('openlp.fake', 56, None, 'trace_error_handler_test')]
            mocked_logger = MagicMock()

            # WHEN: trace_error_handler() is called
            trace_error_handler(mocked_logger)

            # THEN: The mocked_logger.error() method should have been called with the correct parameters
            mocked_logger.error.assert_called_with(
                'OpenLP Error trace\n   File openlp.fake at line 56 \n\t called trace_error_handler_test')

    def test_translate(self):
        """
        Test the translate() function
        """
        # GIVEN: A string to translate and a mocked Qt translate function
        context = 'OpenLP.Tests'
        text = 'Untranslated string'
        comment = 'A comment'
        mocked_translate = MagicMock(return_value='Translated string')

        # WHEN: we call the translate function
        result = translate(context, text, comment, mocked_translate)

        # THEN: the translated string should be returned, and the mocked function should have been called
        mocked_translate.assert_called_with(context, text, comment)
        self.assertEqual('Translated string', result, 'The translated string should have been returned')

    def test_is_win(self):
        """
        Test the is_win() function
        """
        # GIVEN: Mocked out objects
        with patch('openlp.core.common.os') as mocked_os, patch('openlp.core.common.sys') as mocked_sys:

            # WHEN: The mocked os.name and sys.platform are set to 'nt' and 'win32' repectivly
            mocked_os.name = 'nt'
            mocked_sys.platform = 'win32'

            # THEN: The three platform functions should perform properly
            self.assertTrue(is_win(), 'is_win() should return True')
            self.assertFalse(is_macosx(), 'is_macosx() should return False')
            self.assertFalse(is_linux(), 'is_linux() should return False')

    def test_is_macosx(self):
        """
        Test the is_macosx() function
        """
        # GIVEN: Mocked out objects
        with patch('openlp.core.common.os') as mocked_os, patch('openlp.core.common.sys') as mocked_sys:

            # WHEN: The mocked os.name and sys.platform are set to 'posix' and 'darwin' repectivly
            mocked_os.name = 'posix'
            mocked_sys.platform = 'darwin'

            # THEN: The three platform functions should perform properly
            self.assertTrue(is_macosx(), 'is_macosx() should return True')
            self.assertFalse(is_win(), 'is_win() should return False')
            self.assertFalse(is_linux(), 'is_linux() should return False')

    def test_is_linux(self):
        """
        Test the is_linux() function
        """
        # GIVEN: Mocked out objects
        with patch('openlp.core.common.os') as mocked_os, patch('openlp.core.common.sys') as mocked_sys:

            # WHEN: The mocked os.name and sys.platform are set to 'posix' and 'linux3' repectivly
            mocked_os.name = 'posix'
            mocked_sys.platform = 'linux3'

            # THEN: The three platform functions should perform properly
            self.assertTrue(is_linux(), 'is_linux() should return True')
            self.assertFalse(is_win(), 'is_win() should return False')
            self.assertFalse(is_macosx(), 'is_macosx() should return False')

    def test_clean_button_text(self):
        """
        Test the clean_button_text() function.
        """
        # GIVEN: Button text
        input_text = '&Next >'
        expected_text = 'Next'

        # WHEN: The button caption is sent through the clean_button_text function
        actual_text = clean_button_text(input_text)

        # THEN: The text should have been cleaned
        self.assertEqual(expected_text, actual_text, 'The text should be clean')
