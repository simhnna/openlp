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
This module contains tests for the openlp.core.widgets.edits module
"""
import os
from unittest import TestCase
from unittest.mock import MagicMock, PropertyMock, patch

from openlp.core.common.path import Path
from openlp.core.widgets.enums import PathEditType
from openlp.core.widgets.dialogs import FileDialog
from openlp.core.widgets.edits import PathEdit


class TestPathEdit(TestCase):
    """
    Test the :class:`~openlp.core.widgets.edits.PathEdit` class
    """
    def setUp(self):
        with patch('openlp.core.widgets.edits.PathEdit._setup'):
            self.widget = PathEdit()

    def test_path_getter(self):
        """
        Test the `path` property getter.
        """
        # GIVEN: An instance of PathEdit with the `_path` instance variable set
        self.widget._path = Path('getter', 'test', 'pat.h')

        # WHEN: Reading the `path` property
        # THEN: The value that we set should be returned
        assert self.widget.path == Path('getter', 'test', 'pat.h')

    def test_path_setter(self):
        """
        Test the `path` property setter.
        """
        # GIVEN: An instance of the PathEdit object and a mocked `line_edit`
        self.widget.line_edit = MagicMock()

        # WHEN: Writing to the `path` property
        self.widget.path = Path('setter', 'test', 'pat.h')

        # THEN: The `_path` instance variable should be set with the test data. The `line_edit` text and tooltip
        #       should have also been set.
        assert self.widget._path == Path('setter', 'test', 'pat.h')
        self.widget.line_edit.setToolTip.assert_called_once_with(os.path.join('setter', 'test', 'pat.h'))
        self.widget.line_edit.setText.assert_called_once_with(os.path.join('setter', 'test', 'pat.h'))

    def test_path_type_getter(self):
        """
        Test the `path_type` property getter.
        """
        # GIVEN: An instance of PathEdit
        # WHEN: Reading the `path` property
        # THEN: The default value should be returned
        assert self.widget.path_type == PathEditType.Files

    def test_path_type_setter(self):
        """
        Test the `path_type` property setter.
        """
        # GIVEN: An instance of the PathEdit object and a mocked `update_button_tool_tips` method.
        with patch.object(self.widget, 'update_button_tool_tips') as mocked_update_button_tool_tips:

            # WHEN: Writing to a different value than default to the `path_type` property
            self.widget.path_type = PathEditType.Directories

            # THEN: The `_path_type` instance variable should be set with the test data and not the default. The
            #       update_button_tool_tips should have been called.
            assert self.widget._path_type == PathEditType.Directories
            mocked_update_button_tool_tips.assert_called_once_with()

    def test_update_button_tool_tips_directories(self):
        """
        Test the `update_button_tool_tips` method.
        """
        # GIVEN: An instance of PathEdit with the `path_type` set to `Directories`
        self.widget.browse_button = MagicMock()
        self.widget.revert_button = MagicMock()
        self.widget._path_type = PathEditType.Directories

        # WHEN: Calling update_button_tool_tips
        self.widget.update_button_tool_tips()

        self.widget.browse_button.setToolTip.assert_called_once_with('Browse for directory.')
        self.widget.revert_button.setToolTip.assert_called_once_with('Revert to default directory.')

    def test_update_button_tool_tips_files(self):
        """
        Test the `update_button_tool_tips` method.
        """
        # GIVEN: An instance of PathEdit with the `path_type` set to `Files`
        self.widget.browse_button = MagicMock()
        self.widget.revert_button = MagicMock()
        self.widget._path_type = PathEditType.Files

        # WHEN: Calling update_button_tool_tips
        self.widget.update_button_tool_tips()

        self.widget.browse_button.setToolTip.assert_called_once_with('Browse for file.')
        self.widget.revert_button.setToolTip.assert_called_once_with('Revert to default file.')

    @patch('openlp.core.widgets.edits.FileDialog.getExistingDirectory', return_value=None)
    @patch('openlp.core.widgets.edits.FileDialog.getOpenFileName')
    def test_on_browse_button_clicked_directory(self, mocked_get_open_file_name, mocked_get_existing_directory):
        """
        Test the `browse_button` `clicked` handler on_browse_button_clicked when the `path_type` is set to Directories.
        """
        # GIVEN: An instance of PathEdit with the `path_type` set to `Directories` and a mocked
        #        QFileDialog.getExistingDirectory
        self.widget._path_type = PathEditType.Directories
        self.widget._path = Path('test', 'path')

        # WHEN: Calling on_browse_button_clicked
        self.widget.on_browse_button_clicked()

        # THEN: The FileDialog.getExistingDirectory should have been called with the default caption
        mocked_get_existing_directory.assert_called_once_with(self.widget, 'Select Directory',
                                                              Path('test', 'path'),
                                                              FileDialog.ShowDirsOnly)
        assert mocked_get_open_file_name.called is False

    def test_on_browse_button_clicked_directory_custom_caption(self):
        """
        Test the `browse_button` `clicked` handler on_browse_button_clicked when the `path_type` is set to Directories,
        and `dialog_caption` is set.
        """
        # GIVEN: An instance of PathEdit with the `path_type` set to `Directories` and a mocked
        #        QFileDialog.getExistingDirectory with `default_caption` set.
        with patch('openlp.core.widgets.edits.FileDialog.getExistingDirectory', return_value=None) as \
                mocked_get_existing_directory, \
                patch('openlp.core.widgets.edits.FileDialog.getOpenFileName') as mocked_get_open_file_name:
            self.widget._path_type = PathEditType.Directories
            self.widget._path = Path('test', 'path')
            self.widget.dialog_caption = 'Directory Caption'

            # WHEN: Calling on_browse_button_clicked
            self.widget.on_browse_button_clicked()

            # THEN: The FileDialog.getExistingDirectory should have been called with the custom caption
            mocked_get_existing_directory.assert_called_once_with(self.widget, 'Directory Caption',
                                                                  Path('test', 'path'),
                                                                  FileDialog.ShowDirsOnly)
            assert mocked_get_open_file_name.called is False

    def test_on_browse_button_clicked_file(self):
        """
        Test the `browse_button` `clicked` handler on_browse_button_clicked when the `path_type` is set to Files.
        """
        # GIVEN: An instance of PathEdit with the `path_type` set to `Files` and a mocked QFileDialog.getOpenFileName
        with patch('openlp.core.widgets.edits.FileDialog.getExistingDirectory') as mocked_get_existing_directory, \
                patch('openlp.core.widgets.edits.FileDialog.getOpenFileName', return_value=(None, '')) as \
                mocked_get_open_file_name:
            self.widget._path_type = PathEditType.Files
            self.widget._path = Path('test', 'pat.h')

            # WHEN: Calling on_browse_button_clicked
            self.widget.on_browse_button_clicked()

            # THEN: The FileDialog.getOpenFileName should have been called with the default caption
            mocked_get_open_file_name.assert_called_once_with(self.widget, 'Select File', Path('test', 'pat.h'),
                                                              self.widget.filters)
            assert mocked_get_existing_directory.called is False

    def test_on_browse_button_clicked_file_custom_caption(self):
        """
        Test the `browse_button` `clicked` handler on_browse_button_clicked when the `path_type` is set to Files and
        `dialog_caption` is set.
        """
        # GIVEN: An instance of PathEdit with the `path_type` set to `Files` and a mocked QFileDialog.getOpenFileName
        #        with `default_caption` set.
        with patch('openlp.core.widgets.edits.FileDialog.getExistingDirectory') as mocked_get_existing_directory, \
                patch('openlp.core.widgets.edits.FileDialog.getOpenFileName', return_value=(None, '')) as \
                mocked_get_open_file_name:
            self.widget._path_type = PathEditType.Files
            self.widget._path = Path('test', 'pat.h')
            self.widget.dialog_caption = 'File Caption'

            # WHEN: Calling on_browse_button_clicked
            self.widget.on_browse_button_clicked()

            # THEN: The FileDialog.getOpenFileName should have been called with the custom caption
            mocked_get_open_file_name.assert_called_once_with(self.widget, 'File Caption', Path('test', 'pat.h'),
                                                              self.widget.filters)
            assert mocked_get_existing_directory.called is False

    def test_on_browse_button_clicked_user_cancels(self):
        """
        Test the `browse_button` `clicked` handler on_browse_button_clicked when the user cancels the FileDialog (an
        empty str is returned)
        """
        # GIVEN: An instance of PathEdit with a mocked QFileDialog.getOpenFileName which returns an empty str for the
        #        file path.
        with patch('openlp.core.widgets.edits.FileDialog.getOpenFileName', return_value=(None, '')) as \
                mocked_get_open_file_name:

            # WHEN: Calling on_browse_button_clicked
            self.widget.on_browse_button_clicked()

            # THEN: normpath should not have been called
            assert mocked_get_open_file_name.called is True

    def test_on_browse_button_clicked_user_accepts(self):
        """
        Test the `browse_button` `clicked` handler on_browse_button_clicked when the user accepts the FileDialog (a path
        is returned)
        """
        # GIVEN: An instance of PathEdit with a mocked QFileDialog.getOpenFileName which returns a str for the file
        #        path.
        with patch('openlp.core.widgets.edits.FileDialog.getOpenFileName',
                   return_value=(Path('test', 'pat.h'), '')) as mocked_get_open_file_name, \
                patch.object(self.widget, 'on_new_path'):

            # WHEN: Calling on_browse_button_clicked
            self.widget.on_browse_button_clicked()

            # THEN: normpath and `on_new_path` should have been called
            assert mocked_get_open_file_name.called is True
            assert self.widget.on_new_path.called is True

    def test_on_revert_button_clicked(self):
        """
        Test that the default path is set as the path when the `revert_button.clicked` handler is called.
        """
        # GIVEN: An instance of PathEdit with a mocked `on_new_path`, and the `default_path` set.
        with patch.object(self.widget, 'on_new_path') as mocked_on_new_path:
            self.widget.default_path = Path('default', 'pat.h')

            # WHEN: Calling `on_revert_button_clicked`
            self.widget.on_revert_button_clicked()

            # THEN: on_new_path should have been called with the default path
            mocked_on_new_path.assert_called_once_with(Path('default', 'pat.h'))

    def test_on_line_edit_editing_finished(self):
        """
        Test that the new path is set as the path when the `line_edit.editingFinished` handler is called.
        """
        # GIVEN: An instance of PathEdit with a mocked `line_edit` and `on_new_path`.
        with patch.object(self.widget, 'on_new_path') as mocked_on_new_path:
            self.widget.line_edit = MagicMock(**{'text.return_value': 'test/pat.h'})

            # WHEN: Calling `on_line_edit_editing_finished`
            self.widget.on_line_edit_editing_finished()

            # THEN: on_new_path should have been called with the path enetered in `line_edit`
            mocked_on_new_path.assert_called_once_with(Path('test', 'pat.h'))

    def test_on_new_path_no_change(self):
        """
        Test `on_new_path` when called with a path that is the same as the existing path.
        """
        # GIVEN: An instance of PathEdit with a test path and mocked `pathChanged` signal
        with patch('openlp.core.widgets.edits.PathEdit.path', new_callable=PropertyMock):
            self.widget._path = Path('/old', 'test', 'pat.h')
            self.widget.pathChanged = MagicMock()

            # WHEN: Calling `on_new_path` with the same path as the existing path
            self.widget.on_new_path(Path('/old', 'test', 'pat.h'))

            # THEN: The `pathChanged` signal should not be emitted
            assert self.widget.pathChanged.emit.called is False

    def test_on_new_path_change(self):
        """
        Test `on_new_path` when called with a path that is the different to the existing path.
        """
        # GIVEN: An instance of PathEdit with a test path and mocked `pathChanged` signal
        with patch('openlp.core.widgets.edits.PathEdit.path', new_callable=PropertyMock):
            self.widget._path = Path('/old', 'test', 'pat.h')
            self.widget.pathChanged = MagicMock()

            # WHEN: Calling `on_new_path` with the a new path
            self.widget.on_new_path(Path('/new', 'test', 'pat.h'))

            # THEN: The `pathChanged` signal should be emitted
            self.widget.pathChanged.emit.assert_called_once_with(Path('/new', 'test', 'pat.h'))
