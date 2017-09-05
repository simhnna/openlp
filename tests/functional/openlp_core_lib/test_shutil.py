import os
from unittest import TestCase
from unittest.mock import ANY, MagicMock, patch

from openlp.core.common.path import Path
from openlp.core.lib import shutilpatches


class TestShutilPatches(TestCase):
    """
    Tests for the :mod:`openlp.core.lib.shutil` module
    """

    def test_pcopy(self):
        """
        Test :func:`copy`        
        """
        # GIVEN: A mocked `shutil.copy` which returns a test path as a string
        with patch('openlp.core.lib.shutil.shutil.copy', return_value=os.path.join('destination', 'test', 'path')) \
                as mocked_shutil_copy:

            # WHEN: Calling shutilpatches.copy with the src and dst parameters as Path object types
            result = shutilpatches.copy(Path('source', 'test', 'path'), Path('destination', 'test', 'path'))

            # THEN: `shutil.copy` should have been called with the str equivalents of the Path objects.
            #       `shutilpatches.copy` should return the str type result of calling `shutil.copy` as a Path
            #       object.
            mocked_shutil_copy.assert_called_once_with(os.path.join('source', 'test', 'path'),
                                                       os.path.join('destination', 'test', 'path'))
            self.assertEqual(result, Path('destination', 'test', 'path'))

    def test_pcopy_follow_optional_params(self):
        """
        Test :func:`copy` when follow_symlinks is set to false
        """
        # GIVEN: A mocked `shutil.copy`
        with patch('openlp.core.lib.shutil.shutil.copy', return_value='') as mocked_shutil_copy:

            # WHEN: Calling shutilpatches.copy with `follow_symlinks` set to False
            shutilpatches.copy(Path('source', 'test', 'path'),
                               Path('destination', 'test', 'path'),
                               follow_symlinks=False)

            # THEN: `shutil.copy` should have been called with follow_symlinks is set to false
            mocked_shutil_copy.assert_called_once_with(ANY, ANY, follow_symlinks=False)

    def test_pcopyfile(self):
        """
        Test :func:`copyfile`        
        """
        # GIVEN: A mocked `shutil.copyfile` which returns a test path as a string
        with patch('openlp.core.lib.shutil.shutil.copyfile', return_value=os.path.join('destination', 'test', 'path')) \
                as mocked_shutil_copyfile:

            # WHEN: Calling shutilpatches.copyfile with the src and dst parameters as Path object types
            result = shutilpatches.copyfile(Path('source', 'test', 'path'), Path('destination', 'test', 'path'))

            # THEN: `shutil.copyfile` should have been called with the str equivalents of the Path objects.
            #       `shutilpatches.copyfile` should return the str type result of calling `shutil.copyfile` as a Path
            #       object.
            mocked_shutil_copyfile.assert_called_once_with(os.path.join('source', 'test', 'path'),
                                                           os.path.join('destination', 'test', 'path'))
            self.assertEqual(result, Path('destination', 'test', 'path'))

    def test_pcopyfile_optional_params(self):
        """
        Test :func:`copyfile` when follow_symlinks is set to false
        """
        # GIVEN: A mocked `shutil.copyfile`
        with patch('openlp.core.lib.shutil.shutil.copyfile', return_value='') as mocked_shutil_copyfile:

            # WHEN: Calling shutilpatches.copyfile with `follow_symlinks` set to False
            shutilpatches.copyfile(Path('source', 'test', 'path'),
                                   Path('destination', 'test', 'path'),
                                   follow_symlinks=False)

            # THEN: `shutil.copyfile` should have been called with the optional parameters, with out any of the values
            #       being modified
            mocked_shutil_copyfile.assert_called_once_with(ANY, ANY, follow_symlinks=False)

    def test_pcopytree(self):
        """
        Test :func:`copytree`        
        """
        # GIVEN: A mocked `shutil.copytree` which returns a test path as a string
        with patch('openlp.core.lib.shutil.shutil.copytree', return_value=os.path.join('destination', 'test', 'path')) \
                as mocked_shutil_copytree:

            # WHEN: Calling shutilpatches.copytree with the src and dst parameters as Path object types
            result = shutilpatches.copytree(Path('source', 'test', 'path'), Path('destination', 'test', 'path'))

            # THEN: `shutil.copytree` should have been called with the str equivalents of the Path objects.
            #       `shutilpatches.copytree` should return the str type result of calling `shutil.copytree` as a Path
            #       object.
            mocked_shutil_copytree.assert_called_once_with(os.path.join('source', 'test', 'path'),
                                                           os.path.join('destination', 'test', 'path'))
            self.assertEqual(result, Path('destination', 'test', 'path'))

    def test_pcopytree_optional_params(self):
        """
        Test :func:`copytree` when optional parameters are passed
        """
        # GIVEN: A mocked `shutil.copytree`
        with patch('openlp.core.lib.shutil.shutil.copytree', return_value='') as mocked_shutil_copytree:
            mocked_ignore = MagicMock()
            mocked_copy_function = MagicMock()

            # WHEN: Calling shutilpatches.copytree with the optional parameters set
            shutilpatches.copytree(Path('source', 'test', 'path'),
                                   Path('destination', 'test', 'path'),
                                   symlinks=True,
                                   ignore=mocked_ignore,
                                   copy_function=mocked_copy_function,
                                   ignore_dangling_symlinks=True)

            # THEN: `shutil.copytree` should have been called with the optional parameters, with out any of the values
            #       being modified
            mocked_shutil_copytree.assert_called_once_with(ANY, ANY,
                                                           symlinks=True,
                                                           ignore=mocked_ignore,
                                                           copy_function=mocked_copy_function,
                                                           ignore_dangling_symlinks=True)

    def test_prmtree(self):
        """
        Test :func:`rmtree`        
        """
        # GIVEN: A mocked `shutil.rmtree`
        with patch('openlp.core.lib.shutil.shutil.rmtree', return_value=None) as mocked_rmtree:

            # WHEN: Calling shutilpatches.rmtree with the path parameter as Path object type
            result = shutilpatches.rmtree(Path('test', 'path'))

            # THEN: `shutil.rmtree` should have been called with the str equivalents of the Path object.
            mocked_rmtree.assert_called_once_with(os.path.join('test', 'path'))
            self.assertIsNone(result)

    def test_prmtree_optional_params(self):
        """
        Test :func:`rmtree`  when optional parameters are passed
        """
        # GIVEN: A mocked `shutil.rmtree`
        with patch('openlp.core.lib.shutil.shutil.rmtree', return_value='') as mocked_shutil_rmtree:
            mocked_on_error = MagicMock()

            # WHEN: Calling shutilpatches.rmtree with `ignore_errors` set to True and `onerror` set to a mocked object
            shutilpatches.rmtree(Path('test', 'path'), ignore_errors=True, onerror=mocked_on_error)

            # THEN: `shutil.rmtree` should have been called with the optional parameters, with out any of the values
            #       being modified
            mocked_shutil_rmtree.assert_called_once_with(ANY, ignore_errors=True, onerror=mocked_on_error)
