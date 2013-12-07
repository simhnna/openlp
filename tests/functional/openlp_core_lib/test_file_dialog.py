"""
Package to test the openlp.core.lib.filedialog package.
"""
from unittest import TestCase

from openlp.core.common import UiStrings
from openlp.core.lib.filedialog import FileDialog
from tests.functional import MagicMock, patch

class TestFileDialog(TestCase):
    """
    Test the functions in the :mod:`filedialog` module.
    """
    def setUp(self):
        self.os_patcher = patch('openlp.core.lib.filedialog.os')
        self.qt_gui_patcher = patch('openlp.core.lib.filedialog.QtGui')
        self.ui_strings_patcher = patch('openlp.core.lib.filedialog.UiStrings')
        self.mocked_os = self.os_patcher.start()
        self.mocked_qt_gui = self.qt_gui_patcher.start()
        self.mocked_ui_strings = self.ui_strings_patcher.start()
        self.mocked_parent = MagicMock()

    def tearDown(self):
        self.os_patcher.stop()
        self.qt_gui_patcher.stop()
        self.ui_strings_patcher.stop()

    def get_open_file_names_canceled_test(self):
        """
            Test that FileDialog.getOpenFileNames() returns and empty QStringList when QFileDialog is canceled
            (returns an empty QStringList)
        """
        self.mocked_os.reset()

        # GIVEN: An empty QStringList as a return value from QFileDialog.getOpenFileNames
        self.mocked_qt_gui.QFileDialog.getOpenFileNames.return_value = []

        # WHEN: FileDialog.getOpenFileNames is called
        result = FileDialog.getOpenFileNames(self.mocked_parent)

        # THEN: The returned value should be an empty QStringList and os.path.exists should not have been called
        assert not self.mocked_os.path.exists.called
        self.assertEqual(result, [],
            'FileDialog.getOpenFileNames should return and empty list when QFileDialog.getOpenFileNames is canceled')

    def returned_file_list_test(self):
        """
            Test that FileDialog.getOpenFileNames handles a list of files properly when QFileList.getOpenFileNames
            returns a good file name, a urlencoded file name and a non-existing file
        """
        self.mocked_os.rest()
        self.mocked_qt_gui.reset()

        # GIVEN: A List of known values as a return value from QFileDialog.getOpenFileNames and a list of valid
        #		file names.
        self.mocked_qt_gui.QFileDialog.getOpenFileNames.return_value = [
            '/Valid File', '/url%20encoded%20file%20%231', '/non-existing']
        self.mocked_os.path.exists.side_effect = lambda file_name: file_name in [
            '/Valid File', '/url encoded file #1']

        # WHEN: FileDialog.getOpenFileNames is called
        result = FileDialog.getOpenFileNames(self.mocked_parent)

        # THEN: os.path.exists should have been called with known args. QmessageBox.information should have been
        #       called. The returned result should corrilate with the input.
        self.mocked_os.path.exists.assert_callde_with('/Valid File')
        self.mocked_os.path.exists.assert_callde_with('/url%20encoded%20file%20%231')
        self.mocked_os.path.exists.assert_callde_with('/url encoded file #1')
        self.mocked_os.path.exists.assert_callde_with('/non-existing')
        self.mocked_os.path.exists.assert_callde_with('/non-existing')
        self.mocked_qt_gui.QmessageBox.information.called_with(self.mocked_parent, UiStrings().FileNotFound,
            UiStrings().FileNotFoundMessage % '/non-existing')
        self.assertEqual(result, ['/Valid File', '/url encoded file #1'], 'The returned file list is incorrect')