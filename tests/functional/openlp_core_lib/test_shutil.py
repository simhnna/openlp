import os
from unittest import TestCase
from unittest.mock import ANY, MagicMock, patch

from openlp.core.common.path import Path
from openlp.core.lib.shutil import copy, copyfile, copytree, rmtree, which


class TestShutil(TestCase):
    """
    Tests for the :mod:`openlp.core.lib.shutil` module
    """

    def test_copy(self):
        """
        Test :func:`copy`
        """
        # GIVEN: A mocked `shutil.copy` which returns a test path as a string
        with patch('openlp.core.lib.shutil.shutil.copy', return_value=os.path.join('destination', 'test', 'path')) \
                as mocked_shutil_copy:

            # WHEN: Calling :func:`copy` with the src and dst parameters as Path object types
            result = copy(Path('source', 'test', 'path'), Path('destination', 'test', 'path'))

            # THEN: :func:`shutil.copy` should have been called with the str equivalents of the Path objects.
            #       :func:`copy` should return the str type result of calling :func:`shutil.copy` as a Path object.
            mocked_shutil_copy.assert_called_once_with(os.path.join('source', 'test', 'path'),
                                                       os.path.join('destination', 'test', 'path'))
            self.assertEqual(result, Path('destination', 'test', 'path'))

    def test_copy_follow_optional_params(self):
        """
        Test :func:`copy` when follow_symlinks is set to false
        """
        # GIVEN: A mocked `shutil.copy`
        with patch('openlp.core.lib.shutil.shutil.copy', return_value='') as mocked_shutil_copy:

            # WHEN: Calling :func:`copy` with :param:`follow_symlinks` set to False
            copy(Path('source', 'test', 'path'), Path('destination', 'test', 'path'), follow_symlinks=False)

            # THEN: :func:`shutil.copy` should have been called with :param:`follow_symlinks` set to false
            mocked_shutil_copy.assert_called_once_with(ANY, ANY, follow_symlinks=False)

    def test_copyfile(self):
        """
        Test :func:`copyfile`
        """
        # GIVEN: A mocked :func:`shutil.copyfile` which returns a test path as a string
        with patch('openlp.core.lib.shutil.shutil.copyfile',
                   return_value=os.path.join('destination', 'test', 'path')) as mocked_shutil_copyfile:

            # WHEN: Calling :func:`copyfile` with the src and dst parameters as Path object types
            result = copyfile(Path('source', 'test', 'path'), Path('destination', 'test', 'path'))

            # THEN: :func:`shutil.copyfile` should have been called with the str equivalents of the Path objects.
            #       :func:`copyfile` should return the str type result of calling :func:`shutil.copyfile` as a Path
            #       object.
            mocked_shutil_copyfile.assert_called_once_with(os.path.join('source', 'test', 'path'),
                                                           os.path.join('destination', 'test', 'path'))
            self.assertEqual(result, Path('destination', 'test', 'path'))

    def test_copyfile_optional_params(self):
        """
        Test :func:`copyfile` when follow_symlinks is set to false
        """
        # GIVEN: A mocked :func:`shutil.copyfile`
        with patch('openlp.core.lib.shutil.shutil.copyfile', return_value='') as mocked_shutil_copyfile:

            # WHEN: Calling :func:`copyfile` with :param:`follow_symlinks` set to False
            copyfile(Path('source', 'test', 'path'), Path('destination', 'test', 'path'), follow_symlinks=False)

            # THEN: :func:`shutil.copyfile` should have been called with the optional parameters, with out any of the
            #       values being modified
            mocked_shutil_copyfile.assert_called_once_with(ANY, ANY, follow_symlinks=False)

    def test_copytree(self):
        """
        Test :func:`copytree`
        """
        # GIVEN: A mocked :func:`shutil.copytree` which returns a test path as a string
        with patch('openlp.core.lib.shutil.shutil.copytree',
                   return_value=os.path.join('destination', 'test', 'path')) as mocked_shutil_copytree:

            # WHEN: Calling :func:`copytree` with the src and dst parameters as Path object types
            result = copytree(Path('source', 'test', 'path'), Path('destination', 'test', 'path'))

            # THEN: :func:`shutil.copytree` should have been called with the str equivalents of the Path objects.
            #       :func:`patches.copytree` should return the str type result of calling :func:`shutil.copytree` as a
            #       Path object.
            mocked_shutil_copytree.assert_called_once_with(os.path.join('source', 'test', 'path'),
                                                           os.path.join('destination', 'test', 'path'))
            self.assertEqual(result, Path('destination', 'test', 'path'))

    def test_copytree_optional_params(self):
        """
        Test :func:`copytree` when optional parameters are passed
        """
        # GIVEN: A mocked :func:`shutil.copytree`
        with patch('openlp.core.lib.shutil.shutil.copytree', return_value='') as mocked_shutil_copytree:
            mocked_ignore = MagicMock()
            mocked_copy_function = MagicMock()

            # WHEN: Calling :func:`copytree` with the optional parameters set
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
        # GIVEN: A mocked :func:`shutil.rmtree`
        with patch('openlp.core.lib.shutil.shutil.rmtree', return_value=None) as mocked_shutil_rmtree:

            # WHEN: Calling :func:`rmtree` with the path parameter as Path object type
            result = rmtree(Path('test', 'path'))

            # THEN: :func:`shutil.rmtree` should have been called with the str equivalents of the Path object.
            mocked_shutil_rmtree.assert_called_once_with(os.path.join('test', 'path'))
            self.assertIsNone(result)

    def test_rmtree_optional_params(self):
        """
        Test :func:`rmtree` when optional parameters are passed
        """
        # GIVEN: A mocked :func:`shutil.rmtree`
        with patch('openlp.core.lib.shutil.shutil.rmtree', return_value='') as mocked_shutil_rmtree:
            mocked_on_error = MagicMock()

            # WHEN: Calling :func:`rmtree` with :param:`ignore_errors` set to True and `onerror` set to a mocked object
            rmtree(Path('test', 'path'), ignore_errors=True, onerror=mocked_on_error)

            # THEN: :func:`shutil.rmtree` should have been called with the optional parameters, with out any of the
            #       values being modified
            mocked_shutil_rmtree.assert_called_once_with(ANY, ignore_errors=True, onerror=mocked_on_error)

    def test_which_no_command(self):
        """
        Test :func:`which` when the command is not found.
        """
        # GIVEN: A mocked :func:``shutil.which` when the command is not found.
        with patch('openlp.core.lib.shutil.shutil.which', return_value=None) as mocked_shutil_which:

            # WHEN: Calling :func:`which` with a command that does not exist.
            result = which('no_command')

            # THEN: :func:`shutil.which` should have been called with the command, and :func:`which` should return None.
            mocked_shutil_which.assert_called_once_with('no_command')
            self.assertIsNone(result)

    def test_which_command(self):
        """
        Test :func:`which` when a command has been found.
        """
        # GIVEN: A mocked :func:`shutil.which` when the command is found.
        with patch('openlp.core.lib.shutil.shutil.which',
                   return_value=os.path.join('path', 'to', 'command')) as mocked_shutil_which:

            # WHEN: Calling :func:`which` with a command that exists.
            result = which('command')

            # THEN: :func:`shutil.which` should have been called with the command, and :func:`which` should return a
            #       Path object equivalent of the command path.
            mocked_shutil_which.assert_called_once_with('command')
            self.assertEqual(result, Path('path', 'to', 'command'))
