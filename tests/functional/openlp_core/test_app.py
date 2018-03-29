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
import sys
from unittest import TestCase, skip
from unittest.mock import MagicMock, patch

from PyQt5 import QtCore, QtWidgets

from openlp.core.app import OpenLP, parse_options
from openlp.core.common.settings import Settings
from tests.utils.constants import RESOURCE_PATH
from tests.helpers.testmixin import TestMixin


def test_parse_options_basic():
    """
    Test the parse options process works
    """
    # GIVEN: a a set of system arguments.
    sys.argv[1:] = []

    # WHEN: We we parse them to expand to options
    args = parse_options()

    # THEN: the following fields will have been extracted.
    assert args.loglevel == 'warning', 'The log level should be set to warning'
    assert args.no_error_form is False, 'The no_error_form should be set to False'
    assert args.portable is False, 'The portable flag should be set to false'
    assert args.rargs == [], 'The service file should be blank'


def test_parse_options_debug():
    """
    Test the parse options process works for debug only
    """
    # GIVEN: a a set of system arguments.
    sys.argv[1:] = ['-l debug']

    # WHEN: We we parse them to expand to options
    args = parse_options()

    # THEN: the following fields will have been extracted.
    assert args.loglevel == ' debug', 'The log level should be set to debug'
    assert args.no_error_form is False, 'The no_error_form should be set to False'
    assert args.portable is False, 'The portable flag should be set to false'
    assert args.rargs == [], 'The service file should be blank'


def test_parse_options_debug_and_portable():
    """
    Test the parse options process works for debug and portable
    """
    # GIVEN: a a set of system arguments.
    sys.argv[1:] = ['--portable']

    # WHEN: We we parse them to expand to options
    args = parse_options()

    # THEN: the following fields will have been extracted.
    assert args.loglevel == 'warning', 'The log level should be set to warning'
    assert args.no_error_form is False, 'The no_error_form should be set to False'
    assert args.portable is True, 'The portable flag should be set to true'
    assert args.rargs == [], 'The service file should be blank'


def test_parse_options_all_no_file():
    """
    Test the parse options process works with two options
    """
    # GIVEN: a a set of system arguments.
    sys.argv[1:] = ['-l debug', '-p']

    # WHEN: We we parse them to expand to options
    args = parse_options()

    # THEN: the following fields will have been extracted.
    assert args.loglevel == ' debug', 'The log level should be set to debug'
    assert args.no_error_form is False, 'The no_error_form should be set to False'
    assert args.portable is True, 'The portable flag should be set to True'
    assert args.rargs == [], 'The service file should be blank'


def test_parse_options_file():
    """
    Test the parse options process works with a file
    """
    # GIVEN: a a set of system arguments.
    sys.argv[1:] = ['dummy_temp']

    # WHEN: We we parse them to expand to options
    args = parse_options()

    # THEN: the following fields will have been extracted.
    assert args.loglevel == 'warning', 'The log level should be set to warning'
    assert args.no_error_form is False, 'The no_error_form should be set to False'
    assert args.portable is False, 'The portable flag should be set to false'
    assert args.rargs == 'dummy_temp', 'The service file should not be blank'


def test_parse_options_file_and_debug():
    """
    Test the parse options process works with a file and the debug log level
    """
    # GIVEN: a a set of system arguments.
    sys.argv[1:] = ['-l debug', 'dummy_temp']

    # WHEN: We we parse them to expand to options
    args = parse_options()

    # THEN: the following fields will have been extracted.
    assert args.loglevel == ' debug', 'The log level should be set to debug'
    assert args.no_error_form is False, 'The no_error_form should be set to False'
    assert args.portable is False, 'The portable flag should be set to false'
    assert args.rargs == 'dummy_temp', 'The service file should not be blank'


class TestOpenLP(TestCase, TestMixin):
    """
    Test the OpenLP app class
    """
    def setUp(self):
        self.setup_application()
        self.build_settings()
        self.openlp = OpenLP([])

    def tearDown(self):
        self.destroy_settings()
        del self.openlp
        self.openlp = None

    @skip("This one fails")
    def test_exec(self):
        """
        Test the exec method
        """
        # GIVEN: An app
        self.mocked_qapplication.exec.return_value = False

        # WHEN: exec() is called
        result = self.openlp.exec()

        # THEN: The right things should be called
        assert self.openlp.is_event_loop_active is True
        self.mocked_qapplication.exec.assert_called_once_with()
        assert result is False

    @patch('openlp.core.app.QtWidgets.QMessageBox.critical')
    @patch('openlp.core.app.QtWidgets.QMessageBox.StandardButtons')
    def test_is_already_running_is_running(self, MockedStandardButtons, mocked_critical):
        """
        Test the is_already_running() method when OpenLP IS running and the user chooses to continue
        """
        # GIVEN: An OpenLP app and some mocks
        MockedStandardButtons.return_value = 0
        mocked_critical.return_value = QtWidgets.QMessageBox.Ok

        # WHEN: is_already_running() is called
        self.openlp.is_already_running()

        # THEN: The result should be false
        MockedStandardButtons.assert_called_once_with(QtWidgets.QMessageBox.Ok)

    @skip("This one fails")
    def test_process_events(self):
        """
        Test that the app.process_events() method simply calls the Qt method
        """
        # GIVEN: An app
        # WHEN: process_events() is called
        with patch.object(self.openlp, 'processEvents') as mocked_processEvents:
            self.openlp.process_events()

        # THEN: processEvents was called
        mocked_processEvents.assert_called_once_with()

    @skip("This one fails")
    def test_set_busy_cursor(self):
        """
        Test that the set_busy_cursor() method sets the cursor
        """
        # GIVEN: An app
        # WHEN: set_busy_cursor() is called
        with patch.object(self.openlp, 'setOverrideCursor') as mocked_setOverrideCursor, \
                patch.object(self.openlp, 'processEvents') as mocked_processEvents:
            self.openlp.set_busy_cursor()

        # THEN: The cursor should have been set
        mocked_setOverrideCursor.assert_called_once_with(QtCore.Qt.BusyCursor)
        mocked_processEvents.assert_called_once_with()

    @skip("This one fails")
    def test_set_normal_cursor(self):
        """
        Test that the set_normal_cursor() method resets the cursor
        """
        # GIVEN: An app
        # WHEN: set_normal_cursor() is called
        with patch.object(self.openlp, 'restoreOverrideCursor') as mocked_restoreOverrideCursor, \
                patch.object(self.openlp, 'processEvents') as mocked_processEvents:
            self.openlp.set_normal_cursor()

        # THEN: The cursor should have been set
        mocked_restoreOverrideCursor.assert_called_once_with()
        mocked_processEvents.assert_called_once_with()

    @skip("This one fails")
    def test_event(self):
        """
        Test the reimplemented event method
        """
        # GIVEN: A file path and a QEvent.
        file_path = str(RESOURCE_PATH / 'church.jpg')
        mocked_file_method = MagicMock(return_value=file_path)
        event = QtCore.QEvent(QtCore.QEvent.FileOpen)
        event.file = mocked_file_method

        # WHEN: Call the vent method.
        result = self.openlp.event(event)

        # THEN: The path should be inserted.
        assert result is True, "The method should have returned True."
        mocked_file_method.assert_called_once_with()
        assert self.openlp.args[0] == file_path, "The path should be in args."

    @skip("This one fails")
    @patch('openlp.core.app.is_macosx')
    def test_application_activate_event(self, mocked_is_macosx):
        """
        Test that clicking on the dock icon on Mac OS X restores the main window if it is minimized
        """
        # GIVEN: Mac OS X and an ApplicationActivate event
        mocked_is_macosx.return_value = True
        event = MagicMock()
        event.type.return_value = QtCore.QEvent.ApplicationActivate
        mocked_main_window = MagicMock()
        self.openlp.main_window = mocked_main_window

        # WHEN: The icon in the dock is clicked
        result = self.openlp.event(event)

        # THEN:
        assert result is True, "The method should have returned True."
        # assert self.openlp.main_window.isMinimized() is False

    @skip("This one fails")
    @patch('openlp.core.app.get_version')
    @patch('openlp.core.app.QtWidgets.QMessageBox.question')
    def test_backup_on_upgrade_first_install(self, mocked_question, mocked_get_version):
        """
        Test that we don't try to backup on a new install
        """
        # GIVEN: Mocked data version and OpenLP version which are the same
        old_install = False
        MOCKED_VERSION = {
            'full': '2.4.0-bzr000',
            'version': '2.4.0',
            'build': 'bzr000'
        }
        Settings().setValue('core/application version', '2.4.0')
        mocked_get_version.return_value = MOCKED_VERSION
        mocked_question.return_value = QtWidgets.QMessageBox.No

        # WHEN: We check if a backup should be created
        self.openlp.backup_on_upgrade(old_install, False)

        # THEN: It should not ask if we want to create a backup
        assert Settings().value('core/application version') == '2.4.0', 'Version should be the same!'
        assert mocked_question.call_count == 0, 'No question should have been asked!'

    @skip("This one fails")
    @patch('openlp.core.app.get_version')
    @patch('openlp.core.app.QtWidgets.QMessageBox.question')
    def test_backup_on_upgrade(self, mocked_question, mocked_get_version):
        """
        Test that we try to backup on a new install
        """
        # GIVEN: Mocked data version and OpenLP version which are different
        old_install = True
        MOCKED_VERSION = {
            'full': '2.4.0-bzr000',
            'version': '2.4.0',
            'build': 'bzr000'
        }
        Settings().setValue('core/application version', '2.0.5')
        self.openlp.splash = MagicMock()
        self.openlp.splash.isVisible.return_value = True
        mocked_get_version.return_value = MOCKED_VERSION
        mocked_question.return_value = QtWidgets.QMessageBox.No

        # WHEN: We check if a backup should be created
        self.openlp.backup_on_upgrade(old_install, True)

        # THEN: It should ask if we want to create a backup
        assert Settings().value('core/application version') == '2.4.0', 'Version should be upgraded!'
        assert mocked_question.call_count == 1, 'A question should have been asked!'
        self.openlp.splash.hide.assert_called_once_with()
        self.openlp.splash.show.assert_called_once_with()
