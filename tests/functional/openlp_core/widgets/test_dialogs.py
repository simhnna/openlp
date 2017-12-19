import os
from unittest import TestCase
from unittest.mock import patch

from PyQt5 import QtWidgets

from openlp.core.common.path import Path
from openlp.core.widgets.dialogs import FileDialog


class TestFileDialogPatches(TestCase):
    """
    Tests for the :mod:`openlp.core.widgets.dialogs` module
    """

    def test_file_dialog(self):
        """
        Test that the :class:`FileDialog` instantiates correctly
        """
        # GIVEN: The FileDialog class
        # WHEN: Creating an instance
        instance = FileDialog()

        # THEN: The instance should be an instance of QFileDialog
        assert isinstance(instance, QtWidgets.QFileDialog)

    def test_get_existing_directory_user_abort(self):
        """
        Test that `getExistingDirectory` handles the case when the user cancels the dialog
        """
        # GIVEN: FileDialog with a mocked QDialog.getExistingDirectory method
        # WHEN: Calling FileDialog.getExistingDirectory and the user cancels the dialog returns a empty string
        with patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory', return_value=''):
            result = FileDialog.getExistingDirectory()

            # THEN: The result should be None
            assert result is None

    def test_get_existing_directory_user_accepts(self):
        """
        Test that `getExistingDirectory` handles the case when the user accepts the dialog
        """
        # GIVEN: FileDialog with a mocked QDialog.getExistingDirectory method
        # WHEN: Calling FileDialog.getExistingDirectory, the user chooses a file and accepts the dialog (it returns a
        #       string pointing to the directory)
        with patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory', return_value=os.path.join('test', 'dir')):
            result = FileDialog.getExistingDirectory()

            # THEN: getExistingDirectory() should return a Path object pointing to the chosen file
            assert result == Path('test', 'dir')

    def test_get_existing_directory_param_order(self):
        """
        Test that `getExistingDirectory` passes the parameters to `QFileDialog.getExistingDirectory` in the correct
        order
        """
        # GIVEN: FileDialog
        with patch('openlp.core.widgets.dialogs.QtWidgets.QFileDialog.getExistingDirectory', return_value='') \
                as mocked_get_existing_directory:

            # WHEN: Calling the getExistingDirectory method with all parameters set
            FileDialog.getExistingDirectory('Parent', 'Caption', Path('test', 'dir'), 'Options')

            # THEN: The `QFileDialog.getExistingDirectory` should have been called with the parameters in the correct
            #       order
            mocked_get_existing_directory.assert_called_once_with('Parent', 'Caption', os.path.join('test', 'dir'),
                                                                  'Options')

    def test_get_open_file_name_user_abort(self):
        """
        Test that `getOpenFileName` handles the case when the user cancels the dialog
        """
        # GIVEN: FileDialog with a mocked QDialog.getOpenFileName method
        # WHEN: Calling FileDialog.getOpenFileName and the user cancels the dialog (it returns a tuple with the first
        #       value set as an empty string)
        with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName', return_value=('', '')):
            result = FileDialog.getOpenFileName()

            # THEN: First value should be None
            assert result[0] is None

    def test_get_open_file_name_user_accepts(self):
        """
        Test that `getOpenFileName` handles the case when the user accepts the dialog
        """
        # GIVEN: FileDialog with a mocked QDialog.getOpenFileName method
        # WHEN: Calling FileDialog.getOpenFileName, the user chooses a file and accepts the dialog (it returns a
        #       tuple with the first value set as an string pointing to the file)
        with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName',
                   return_value=(os.path.join('test', 'chosen.file'), '')):
            result = FileDialog.getOpenFileName()

            # THEN: getOpenFileName() should return a tuple with the first value set to a Path object pointing to the
            #       chosen file
            assert result[0] == Path('test', 'chosen.file')

    def test_get_open_file_name_selected_filter(self):
        """
        Test that `getOpenFileName` does not modify the selectedFilter as returned by `QFileDialog.getOpenFileName`
        """
        # GIVEN: FileDialog with a mocked QDialog.get_save_file_name method
        # WHEN: Calling FileDialog.getOpenFileName, and `QFileDialog.getOpenFileName` returns a known `selectedFilter`
        with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName', return_value=('', 'selected filter')):
            result = FileDialog.getOpenFileName()

            # THEN: getOpenFileName() should return a tuple with the second value set to a the selected filter
            assert result[1] == 'selected filter' 

    def test_get_open_file_names_user_abort(self):
        """
        Test that `getOpenFileNames` handles the case when the user cancels the dialog
        """
        # GIVEN: FileDialog with a mocked QDialog.getOpenFileNames method
        # WHEN: Calling FileDialog.getOpenFileNames and the user cancels the dialog (it returns a tuple with the first
        #       value set as an empty list)
        with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileNames', return_value=([], '')):
            result = FileDialog.getOpenFileNames()

            # THEN: First value should be an empty list
            assert result[0] == []

    def test_get_open_file_names_user_accepts(self):
        """
        Test that `getOpenFileNames` handles the case when the user accepts the dialog
        """
        # GIVEN: FileDialog with a mocked QDialog.getOpenFileNames method
        # WHEN: Calling FileDialog.getOpenFileNames, the user chooses some files and accepts the dialog (it returns a
        #       tuple with the first value set as a list of strings pointing to the file)
        with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileNames',
                   return_value=([os.path.join('test', 'chosen.file1'), os.path.join('test', 'chosen.file2')], '')):
            result = FileDialog.getOpenFileNames()

            # THEN: getOpenFileNames() should return a tuple with the first value set to a list of Path objects pointing
            #       to the chosen file
            assert result[0] == [Path('test', 'chosen.file1'), Path('test', 'chosen.file2')]

    def test_get_open_file_names_selected_filter(self):
        """
        Test that `getOpenFileNames` does not modify the selectedFilter as returned by `QFileDialog.getOpenFileNames`
        """
        # GIVEN: FileDialog with a mocked QDialog.getOpenFileNames method
        # WHEN: Calling FileDialog.getOpenFileNames, and `QFileDialog.getOpenFileNames` returns a known
        #       `selectedFilter`
        with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileNames', return_value=([], 'selected filter')):
            result = FileDialog.getOpenFileNames()

            # THEN: getOpenFileNames() should return a tuple with the second value set to a the selected filter
            assert result[1] == 'selected filter'

    def test_get_save_file_name_user_abort(self):
        """
        Test that `getSaveFileName` handles the case when the user cancels the dialog
        """
        # GIVEN: FileDialog with a mocked QDialog.get_save_file_name method
        # WHEN: Calling FileDialog.getSaveFileName and the user cancels the dialog (it returns a tuple with the first
        #       value set as an empty string)
        with patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName', return_value=('', '')):
            result = FileDialog.getSaveFileName()

            # THEN: First value should be None
            assert result[0] is None

    def test_get_save_file_name_user_accepts(self):
        """
        Test that `getSaveFileName` handles the case when the user accepts the dialog
        """
        # GIVEN: FileDialog with a mocked QDialog.getSaveFileName method
        # WHEN: Calling FileDialog.getSaveFileName, the user chooses a file and accepts the dialog (it returns a
        #       tuple with the first value set as an string pointing to the file)
        with patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName',
                   return_value=(os.path.join('test', 'chosen.file'), '')):
            result = FileDialog.getSaveFileName()

            # THEN: getSaveFileName() should return a tuple with the first value set to a Path object pointing to the
            #       chosen file
            assert result[0] == Path('test', 'chosen.file')

    def test_get_save_file_name_selected_filter(self):
        """
        Test that `getSaveFileName` does not modify the selectedFilter as returned by `QFileDialog.getSaveFileName`
        """
        # GIVEN: FileDialog with a mocked QDialog.get_save_file_name method
        # WHEN: Calling FileDialog.getSaveFileName, and `QFileDialog.getSaveFileName` returns a known `selectedFilter`
        with patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName', return_value=('', 'selected filter')):
            result = FileDialog.getSaveFileName()

            # THEN: getSaveFileName() should return a tuple with the second value set to a the selected filter
            assert result[1] == 'selected filter'
