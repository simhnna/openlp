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
Package to test openlp.core.ui.mainwindow package.
"""
import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from PyQt5 import QtCore, QtWidgets

from openlp.core.common.i18n import UiStrings
from openlp.core.common.registry import Registry
from openlp.core.display.screens import ScreenList
from openlp.core.ui.mainwindow import MainWindow
from tests.helpers.testmixin import TestMixin
from tests.utils.constants import TEST_RESOURCES_PATH


class TestMainWindow(TestCase, TestMixin):
    """
    Test the main window
    """
    def _create_mock_action(self, parent, name, **kwargs):
        """
        Create a fake action with some "real" attributes
        """
        action = QtWidgets.QAction(parent)
        action.setObjectName(name)
        if kwargs.get('triggers'):
            action.triggered.connect(kwargs.pop('triggers'))
        return action

    def setUp(self):
        """
        Set up the objects we need for all of the tests
        """
        Registry.create()
        self.registry = Registry()
        self.setup_application()
        # Mock cursor busy/normal methods.
        self.app.set_busy_cursor = MagicMock()
        self.app.set_normal_cursor = MagicMock()
        self.app.process_events = MagicMock()
        self.app.args = []
        Registry().register('application', self.app)
        Registry().set_flag('no_web_server', True)
        self.add_toolbar_action_patcher = patch('openlp.core.ui.mainwindow.create_action')
        self.mocked_add_toolbar_action = self.add_toolbar_action_patcher.start()
        self.mocked_add_toolbar_action.side_effect = self._create_mock_action
        with patch('openlp.core.display.screens.ScreenList.__instance__', spec=ScreenList) as mocked_screen_list:
            mocked_screen_list.current = {'number': 0, 'size': QtCore.QSize(600, 800), 'primary': True}
            self.main_window = MainWindow()

    def tearDown(self):
        """
        Delete all the C++ objects and stop all the patchers
        """
        del self.main_window
        self.add_toolbar_action_patcher.stop()

    def test_cmd_line_file(self):
        """
        Test that passing a service file from the command line loads the service.
        """
        # GIVEN a service as an argument to openlp
        service = os.path.join(TEST_RESOURCES_PATH, 'service', 'test.osz')

        # WHEN the argument is processed
        with patch.object(self.main_window.service_manager, 'load_file') as mocked_load_file:
            self.main_window.open_cmd_line_files(service)

        # THEN the service from the arguments is loaded
        mocked_load_file.assert_called_with(Path(service))

    @patch('openlp.core.ui.servicemanager.ServiceManager.load_file')
    def test_cmd_line_arg(self, mocked_load_file):
        """
        Test that passing a non service file does nothing.
        """
        # GIVEN a non service file as an argument to openlp
        service = os.path.join('openlp.py')
        self.main_window.arguments = [service]

        # WHEN the argument is processed
        self.main_window.open_cmd_line_files(service)

        # THEN the file should not be opened
        assert mocked_load_file.called is False, 'load_file should not have been called'

    def test_main_window_title(self):
        """
        Test that running a new instance of OpenLP set the window title correctly
        """
        # GIVEN a newly opened OpenLP instance

        # WHEN no changes are made to the service

        # THEN the main window's title shoud be the same as the OpenLP string in the UiStrings class
        assert self.main_window.windowTitle() == UiStrings().OpenLP, \
            'The main window\'s title should be the same as the OpenLP string in UiStrings class'

    def test_set_service_modifed(self):
        """
        Test that when setting the service's title the main window's title is set correctly
        """
        # GIVEN a newly opened OpenLP instance

        # WHEN set_service_modified is called with with the modified flag set true and a file name
        self.main_window.set_service_modified(True, 'test.osz')

        # THEN the main window's title should be set to the
        assert self.main_window.windowTitle(), '%s - %s*' % (UiStrings().OpenLP, 'test.osz') == \
            'The main window\'s title should be set to "<the contents of UiStrings().OpenLP> - test.osz*"'

    def test_set_service_unmodified(self):
        """
        Test that when setting the service's title the main window's title is set correctly
        """
        # GIVEN a newly opened OpenLP instance

        # WHEN set_service_modified is called with with the modified flag set False and a file name
        self.main_window.set_service_modified(False, 'test.osz')

        # THEN the main window's title should be set to the
        assert self.main_window.windowTitle(), '%s - %s' % (UiStrings().OpenLP, 'test.osz') == \
            'The main window\'s title should be set to "<the contents of UiStrings().OpenLP> - test.osz"'

    def test_mainwindow_configuration(self):
        """
        Check that the Main Window initialises the Registry Correctly
        """
        # GIVEN: A built main window

        # WHEN: you check the started functions

        # THEN: the following registry functions should have been registered
        assert len(self.registry.service_list) == 13, \
            'The registry should have 12 services, got {}'.format(self.registry.service_list.keys())
        assert len(self.registry.functions_list) == 19, \
            'The registry should have 19 functions, got {}'.format(self.registry.functions_list.keys())
        assert 'application' in self.registry.service_list, 'The application should have been registered.'
        assert 'main_window' in self.registry.service_list, 'The main_window should have been registered.'
        assert 'media_controller' in self.registry.service_list, 'The media_controller should have been registered.'
        assert 'plugin_manager' in self.registry.service_list, 'The plugin_manager should have been registered.'

    def test_projector_manager_hidden_on_startup(self):
        """
        Test that the projector manager is hidden on startup
        """
        # GIVEN: A built main window
        # WHEN: OpenLP is started
        # THEN: The projector manager should be hidden
        assert self.main_window.projector_manager_dock.isVisible() is False

    def test_on_search_shortcut_triggered_shows_media_manager(self):
        """
        Test that the media manager is made visible when the search shortcut is triggered
        """
        # GIVEN: A build main window set up for testing
        with patch.object(self.main_window, 'media_manager_dock') as mocked_media_manager_dock, \
                patch.object(self.main_window, 'media_tool_box') as mocked_media_tool_box:
            mocked_media_manager_dock.isVisible.return_value = False
            mocked_media_tool_box.currentWidget.return_value = None

            # WHEN: The search shortcut is triggered
            self.main_window.on_search_shortcut_triggered()

            # THEN: The media manager dock is made visible
            mocked_media_manager_dock.setVisible.assert_called_with(True)

    def test_on_search_shortcut_triggered_focuses_widget(self):
        """
        Test that the focus is set on the widget when the search shortcut is triggered
        """
        # GIVEN: A build main window set up for testing
        with patch.object(self.main_window, 'media_manager_dock') as mocked_media_manager_dock, \
                patch.object(self.main_window, 'media_tool_box') as mocked_media_tool_box:
            mocked_media_manager_dock.isVisible.return_value = True
            mocked_widget = MagicMock()
            mocked_media_tool_box.currentWidget.return_value = mocked_widget

            # WHEN: The search shortcut is triggered
            self.main_window.on_search_shortcut_triggered()

            # THEN: The media manager dock is made visible
            assert 0 == mocked_media_manager_dock.setVisible.call_count
            mocked_widget.on_focus.assert_called_with()

    @patch('openlp.core.ui.mainwindow.FirstTimeForm')
    @patch('openlp.core.ui.mainwindow.QtWidgets.QMessageBox.warning')
    @patch('openlp.core.ui.mainwindow.Settings')
    def test_on_first_time_wizard_clicked_show_projectors_after(self, MockSettings, mocked_warning, MockWizard):
        """Test that the projector manager is shown after the FTW is run"""
        # GIVEN: Main_window, patched things, patched "Yes" as confirmation to re-run wizard, settings to True.
        MockSettings.return_value.value.return_value = True
        mocked_warning.return_value = QtWidgets.QMessageBox.Yes
        MockWizard.return_value.was_cancelled = False

        with patch.object(self.main_window, 'projector_manager_dock') as mocked_dock, \
                patch.object(self.registry, 'execute'), patch.object(self.main_window, 'theme_manager_contents'):
            # WHEN: on_first_time_wizard_clicked is called
            self.main_window.on_first_time_wizard_clicked()

        # THEN: projector_manager_dock.setVisible should had been called once
        mocked_dock.setVisible.assert_called_once_with(True)

    @patch('openlp.core.ui.mainwindow.FirstTimeForm')
    @patch('openlp.core.ui.mainwindow.QtWidgets.QMessageBox.warning')
    @patch('openlp.core.ui.mainwindow.Settings')
    def test_on_first_time_wizard_clicked_hide_projectors_after(self, MockSettings, mocked_warning, MockWizard):
        """Test that the projector manager is hidden after the FTW is run"""
        # GIVEN: Main_window, patched things, patched "Yes" as confirmation to re-run wizard, settings to False.
        MockSettings.return_value.value.return_value = False
        mocked_warning.return_value = QtWidgets.QMessageBox.Yes
        MockWizard.return_value.was_cancelled = False

        # WHEN: on_first_time_wizard_clicked is called
        with patch.object(self.main_window, 'projector_manager_dock') as mocked_dock, \
                patch.object(self.registry, 'execute'), patch.object(self.main_window, 'theme_manager_contents'):
            self.main_window.on_first_time_wizard_clicked()

        # THEN: projector_manager_dock.setVisible should had been called once
        mocked_dock.setVisible.assert_called_once_with(False)
