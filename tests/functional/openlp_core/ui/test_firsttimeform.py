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
Package to test the openlp.core.ui.firsttimeform package.
"""
import os
import tempfile
from unittest import TestCase
from unittest.mock import MagicMock, patch

from openlp.core.common.path import Path
from openlp.core.common.registry import Registry
from openlp.core.ui.firsttimeform import FirstTimeForm
from tests.helpers.testmixin import TestMixin

FAKE_CONFIG = """
[general]
base url = http://example.com/frw/
[songs]
directory = songs
[bibles]
directory = bibles
[themes]
directory = themes
"""

FAKE_BROKEN_CONFIG = """
[general]
base url = http://example.com/frw/
[songs]
directory = songs
[bibles]
directory = bibles
"""

FAKE_INVALID_CONFIG = """
<html>
<head><title>This is not a config file</title></head>
<body>Some text</body>
</html>
"""


class TestFirstTimeForm(TestCase, TestMixin):

    def setUp(self):
        self.setup_application()
        self.app.setApplicationVersion('0.0')
        # Set up a fake "set_normal_cursor" method since we're not dealing with an actual OpenLP application object
        self.app.set_normal_cursor = lambda: None
        self.app.process_events = lambda: None
        Registry.create()
        Registry().register('application', self.app)
        self.tempfile = os.path.join(tempfile.gettempdir(), 'testfile')

    def tearDown(self):
        if os.path.isfile(self.tempfile):
            os.remove(self.tempfile)

    def test_initialise(self):
        """
        Test if we can intialise the FirstTimeForm
        """
        # GIVEN: A First Time Wizard and an expected screen object
        frw = FirstTimeForm(None)
        expected_screens = MagicMock()

        # WHEN: The First Time Wizard is initialised
        frw.initialize(expected_screens)

        # THEN: The screens should be set up, and the default values initialised
        assert expected_screens == frw.screens, 'The screens should be correct'
        assert frw.web_access is True, 'The default value of self.web_access should be True'
        assert frw.was_cancelled is False, 'The default value of self.was_cancelled should be False'
        assert [] == frw.theme_screenshot_threads, 'The list of threads should be empty'
        assert frw.has_run_wizard is False, 'has_run_wizard should be False'

    def test_set_defaults(self):
        """
        Test that the default values are set when set_defaults() is run
        """
        # GIVEN: An initialised FRW and a whole lot of stuff mocked out
        frw = FirstTimeForm(None)
        frw.initialize(MagicMock())
        with patch.object(frw, 'restart') as mocked_restart, \
                patch.object(frw, 'cancel_button') as mocked_cancel_button, \
                patch.object(frw, 'no_internet_finish_button') as mocked_no_internet_finish_btn, \
                patch.object(frw, 'currentIdChanged') as mocked_currentIdChanged, \
                patch.object(Registry, 'register_function') as mocked_register_function, \
                patch('openlp.core.ui.firsttimeform.Settings') as MockedSettings, \
                patch('openlp.core.ui.firsttimeform.gettempdir') as mocked_gettempdir, \
                patch('openlp.core.ui.firsttimeform.create_paths') as mocked_create_paths, \
                patch.object(frw.application, 'set_normal_cursor'):
            mocked_settings = MagicMock()
            mocked_settings.value.return_value = True
            MockedSettings.return_value = mocked_settings
            mocked_gettempdir.return_value = 'temp'
            expected_temp_path = Path('temp', 'openlp')

            # WHEN: The set_defaults() method is run
            frw.set_defaults()

            # THEN: The default values should have been set
            mocked_restart.assert_called_with()
            assert 'http://openlp.org/files/frw/' == frw.web, 'The default URL should be set'
            mocked_cancel_button.clicked.connect.assert_called_with(frw.on_cancel_button_clicked)
            mocked_no_internet_finish_btn.clicked.connect.assert_called_with(frw.on_no_internet_finish_button_clicked)
            mocked_currentIdChanged.connect.assert_called_with(frw.on_current_id_changed)
            mocked_register_function.assert_called_with('config_screen_changed', frw.update_screen_list_combo)
            mocked_no_internet_finish_btn.setVisible.assert_called_with(False)
            mocked_settings.value.assert_called_with('core/has run wizard')
            mocked_gettempdir.assert_called_with()
            mocked_create_paths.assert_called_with(expected_temp_path)

    def test_update_screen_list_combo(self):
        """
        Test that the update_screen_list_combo() method works correctly
        """
        # GIVEN: A mocked Screen() object and an initialised First Run Wizard and a mocked display_combo_box
        expected_screen_list = ['Screen 1', 'Screen 2']
        mocked_screens = MagicMock()
        mocked_screens.get_screen_list.return_value = expected_screen_list
        frw = FirstTimeForm(None)
        frw.initialize(mocked_screens)
        with patch.object(frw, 'display_combo_box') as mocked_display_combo_box:
            mocked_display_combo_box.count.return_value = 2

            # WHEN: update_screen_list_combo() is called
            frw.update_screen_list_combo()

            # THEN: The combobox should have been updated
            mocked_display_combo_box.clear.assert_called_with()
            mocked_screens.get_screen_list.assert_called_with()
            mocked_display_combo_box.addItems.assert_called_with(expected_screen_list)
            mocked_display_combo_box.count.assert_called_with()
            mocked_display_combo_box.setCurrentIndex.assert_called_with(1)

    @patch('openlp.core.ui.firsttimeform.time')
    @patch('openlp.core.ui.firsttimeform.get_thread_worker')
    @patch('openlp.core.ui.firsttimeform.is_thread_finished')
    def test_on_cancel_button_clicked(self, mocked_is_thread_finished, mocked_get_thread_worker, mocked_time):
        """
        Test that the cancel button click slot shuts down the threads correctly
        """
        # GIVEN: A FRW, some mocked threads and workers (that isn't quite done) and other mocked stuff
        mocked_worker = MagicMock()
        mocked_get_thread_worker.return_value = mocked_worker
        mocked_is_thread_finished.side_effect = [False, True]
        frw = FirstTimeForm(None)
        frw.initialize(MagicMock())
        frw.theme_screenshot_threads = ['test_thread']
        with patch.object(frw.application, 'set_normal_cursor') as mocked_set_normal_cursor:

            # WHEN: on_cancel_button_clicked() is called
            frw.on_cancel_button_clicked()

            # THEN: The right things should be called in the right order
            assert frw.was_cancelled is True, 'The was_cancelled property should have been set to True'
            mocked_get_thread_worker.assert_called_once_with('test_thread')
            mocked_worker.set_download_canceled.assert_called_with(True)
            mocked_is_thread_finished.assert_called_with('test_thread')
            assert mocked_is_thread_finished.call_count == 2, 'isRunning() should have been called twice'
            mocked_time.sleep.assert_called_once_with(0.1)
            mocked_set_normal_cursor.assert_called_once_with()

    def test_broken_config(self):
        """
        Test if we can handle an config file with missing data
        """
        # GIVEN: A mocked get_web_page, a First Time Wizard, an expected screen object, and a mocked broken config file
        with patch('openlp.core.ui.firsttimeform.get_web_page') as mocked_get_web_page:
            first_time_form = FirstTimeForm(None)
            first_time_form.initialize(MagicMock())
            mocked_get_web_page.return_value = FAKE_BROKEN_CONFIG

            # WHEN: The First Time Wizard is downloads the config file
            first_time_form._download_index()

            # THEN: The First Time Form should not have web access
            assert first_time_form.web_access is False, 'There should not be web access with a broken config file'

    def test_invalid_config(self):
        """
        Test if we can handle an config file in invalid format
        """
        # GIVEN: A mocked get_web_page, a First Time Wizard, an expected screen object, and a mocked invalid config file
        with patch('openlp.core.ui.firsttimeform.get_web_page') as mocked_get_web_page:
            first_time_form = FirstTimeForm(None)
            first_time_form.initialize(MagicMock())
            mocked_get_web_page.return_value = FAKE_INVALID_CONFIG

            # WHEN: The First Time Wizard is downloads the config file
            first_time_form._download_index()

            # THEN: The First Time Form should not have web access
            assert first_time_form.web_access is False, 'There should not be web access with an invalid config file'

    @patch('openlp.core.ui.firsttimeform.get_web_page')
    @patch('openlp.core.ui.firsttimeform.QtWidgets.QMessageBox')
    def test_network_error(self, mocked_message_box, mocked_get_web_page):
        """
        Test we catch a network error in First Time Wizard - bug 1409627
        """
        # GIVEN: Initial setup and mocks
        first_time_form = FirstTimeForm(None)
        first_time_form.initialize(MagicMock())
        mocked_get_web_page.side_effect = ConnectionError('')
        mocked_message_box.Ok = 'OK'

        # WHEN: the First Time Wizard calls to get the initial configuration
        first_time_form._download_index()

        # THEN: the critical_error_message_box should have been called
        mocked_message_box.critical.assert_called_once_with(
            first_time_form, 'Network Error', 'There was a network error attempting to connect to retrieve '
            'initial configuration information', 'OK')
