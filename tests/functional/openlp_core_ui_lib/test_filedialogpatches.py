import os
import sys
from unittest import TestCase
from unittest.mock import patch
from pathlib import Path

from PyQt5 import QtWidgets

from openlp.core.ui.lib.filedialogpatches import PQFileDialog


class TestFileDialogPatches(TestCase):
    """
    Tests for the :mod:`openlp.core.ui.lib.filedialogpatches` module
    """

    def test_pq_file_dialog(self):
        """
        Test that the :class:`PQFileDialog` instantiates correctly
        """
        # GIVEN: The PQFileDialog class
        # WHEN: Creating an instance
        instance = PQFileDialog()

        # THEN: The instance should be an instance of QFileDialog
        self.assertIsInstance(instance, QtWidgets.QFileDialog)

    def test_get_existing_directory_user_abort(self):
        """
        Test that `getExistingDirectory` handles the case when the user cancels the dialog
        """
        # GIVEN: PQFileDialog with a mocked QDialog.getExistingDirectory method
        # WHEN: Calling PQFileDialog.getExistingDirectory and the user cancels the dialog returns a empty string
        with patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory', return_value=''):
            result = PQFileDialog.getExistingDirectory()

            # THEN: The result should be None
            self.assertEqual(result, None)

    def test_get_existing_directory_user_accepts(self):
        """
        Test that `getExistingDirectory` handles the case when the user accepts the dialog
        """
        # GIVEN: PQFileDialog with a mocked QDialog.getExistingDirectory method
        # WHEN: Calling PQFileDialog.getExistingDirectory, the user chooses a file and accepts the dialog (it returns a
        #       string pointing to the directory)
        with patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory', return_value=os.path.join('test', 'dir')):
            result = PQFileDialog.getExistingDirectory()

            # THEN: getExistingDirectory() should return a Path object pointing to the chosen file
            self.assertEqual(result, Path('test', 'dir'))

    def test_get_existing_directory_param_order(self):
        """
        Test that `getExistingDirectory` passes the parameters to `QFileDialog.getExistingDirectory` in the correct
        order
        """
        # GIVEN: PQFileDialog
        with patch('openlp.core.ui.lib.filedialogpatches.QtWidgets.QFileDialog.getExistingDirectory', return_value='') \
                as mocked_get_existing_directory:

            # WHEN: Calling the getExistingDirectory method with all parameters set
            PQFileDialog.getExistingDirectory('Parent', 'Caption', Path('test', 'dir'), 'Options')

            # THEN: The `QFileDialog.getExistingDirectory` should have been called with the parameters in the correct
            #       order
            mocked_get_existing_directory.assert_called_once_with('Parent', 'Caption', os.path.join('test', 'dir'),
                                                                  'Options')

    def test_get_open_file_name_user_abort(self):
        """
        Test that `getOpenFileName` handles the case when the user cancels the dialog
        """
        # GIVEN: PQFileDialog with a mocked QDialog.getOpenFileName method
        # WHEN: Calling PQFileDialog.getOpenFileName and the user cancels the dialog (it returns a tuple with the first
        #       value set as an empty string)
        with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName', return_value=('', '')):
            result = PQFileDialog.getOpenFileName()

            # THEN: First value should be None
            self.assertEqual(result[0], None)

    def test_get_open_file_name_user_accepts(self):
        """
        Test that `getOpenFileName` handles the case when the user accepts the dialog
        """
        # GIVEN: PQFileDialog with a mocked QDialog.getOpenFileName method
        # WHEN: Calling PQFileDialog.getOpenFileName, the user chooses a file and accepts the dialog (it returns a
        #       tuple with the first value set as an string pointing to the file)
        with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName',
                   return_value=(os.path.join('test', 'chosen.file'), '')):
            result = PQFileDialog.getOpenFileName()

            # THEN: getOpenFileName() should return a tuple with the first value set to a Path object pointing to the
            #       chosen file
            self.assertEqual(result[0], Path('test', 'chosen.file'))

    def test_get_open_file_name_selected_filter(self):
        """
        Test that `getOpenFileName` does not modify the selectedFilter as returned by `QFileDialog.getOpenFileName`
        """
        # GIVEN: PQFileDialog with a mocked QDialog.get_save_file_name method
        # WHEN: Calling PQFileDialog.getOpenFileName, and `QFileDialog.getOpenFileName` returns a known `selectedFilter`
        with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName', return_value=('', 'selected filter')):
            result = PQFileDialog.getOpenFileName()

            # THEN: getOpenFileName() should return a tuple with the second value set to a the selected filter
            self.assertEqual(result[1], 'selected filter')

    def test_get_open_file_names_user_abort(self):
        """
        Test that `getOpenFileNames` handles the case when the user cancels the dialog
        """
        # GIVEN: PQFileDialog with a mocked QDialog.getOpenFileNames method
        # WHEN: Calling PQFileDialog.getOpenFileNames and the user cancels the dialog (it returns a tuple with the first
        #       value set as an empty list)
        with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileNames', return_value=([], '')):
            result = PQFileDialog.getOpenFileNames()

            # THEN: First value should be an empty list
            self.assertEqual(result[0], [])

    def test_get_open_file_names_user_accepts(self):
        """
        Test that `getOpenFileNames` handles the case when the user accepts the dialog
        """
        # GIVEN: PQFileDialog with a mocked QDialog.getOpenFileNames method
        # WHEN: Calling PQFileDialog.getOpenFileNames, the user chooses some files and accepts the dialog (it returns a
        #       tuple with the first value set as a list of strings pointing to the file)
        with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileNames',
                   return_value=([os.path.join('test', 'chosen.file1'), os.path.join('test', 'chosen.file2')], '')):
            result = PQFileDialog.getOpenFileNames()

            # THEN: getOpenFileNames() should return a tuple with the first value set to a list of Path objects pointing
            #       to the chosen file
            self.assertEqual(result[0], [Path('test', 'chosen.file1'), Path('test', 'chosen.file2')])

    def test_get_open_file_names_selected_filter(self):
        """
        Test that `getOpenFileNames` does not modify the selectedFilter as returned by `QFileDialog.getOpenFileNames`
        """
        # GIVEN: PQFileDialog with a mocked QDialog.getOpenFileNames method
        # WHEN: Calling PQFileDialog.getOpenFileNames, and `QFileDialog.getOpenFileNames` returns a known
        #       `selectedFilter`
        with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileNames', return_value=([], 'selected filter')):
            result = PQFileDialog.getOpenFileNames()

            # THEN: getOpenFileNames() should return a tuple with the second value set to a the selected filter
            self.assertEqual(result[1], 'selected filter')

    def test_get_save_file_name_user_abort(self):
        """
        Test that `getSaveFileName` handles the case when the user cancels the dialog
        """
        # GIVEN: PQFileDialog with a mocked QDialog.get_save_file_name method
        # WHEN: Calling PQFileDialog.getSaveFileName and the user cancels the dialog (it returns a tuple with the first
        #       value set as an empty string)
        with patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName', return_value=('', '')):
            result = PQFileDialog.getSaveFileName()

            # THEN: First value should be None
            self.assertEqual(result[0], None)

    def test_get_save_file_name_user_accepts(self):
        """
        Test that `getSaveFileName` handles the case when the user accepts the dialog
        """
        # GIVEN: PQFileDialog with a mocked QDialog.getSaveFileName method
        # WHEN: Calling PQFileDialog.getSaveFileName, the user chooses a file and accepts the dialog (it returns a
        #       tuple with the first value set as an string pointing to the file)
        with patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName',
                   return_value=(os.path.join('test', 'chosen.file'), '')):
            result = PQFileDialog.getSaveFileName()

            # THEN: getSaveFileName() should return a tuple with the first value set to a Path object pointing to the
            #       chosen file
            self.assertEqual(result[0], Path('test', 'chosen.file'))

    def test_get_save_file_name_selected_filter(self):
        """
        Test that `getSaveFileName` does not modify the selectedFilter as returned by `QFileDialog.getSaveFileName`
        """
        # GIVEN: PQFileDialog with a mocked QDialog.get_save_file_name method
        # WHEN: Calling PQFileDialog.getSaveFileName, and `QFileDialog.getSaveFileName` returns a known `selectedFilter`
        with patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName', return_value=('', 'selected filter')):
            result = PQFileDialog.getSaveFileName()

            # THEN: getSaveFileName() should return a tuple with the second value set to a the selected filter
            self.assertEqual(result[1], 'selected filter')
