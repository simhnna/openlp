# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2015 OpenLP Developers                                   #
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
Package to test the openlp.core.projectors.pjlink command routing.
"""

from unittest import TestCase
from unittest.mock import patch, MagicMock

import openlp.core.projectors.pjlink
from openlp.core.projectors.constants import PJLINK_ERRORS, \
    E_AUTHENTICATION, E_PARAMETER, E_PROJECTOR, E_UNAVAILABLE, E_UNDEFINED
from openlp.core.projectors.db import Projector
from openlp.core.projectors.pjlink import PJLink

'''
from openlp.core.projectors.constants import ERROR_STRING, PJLINK_ERST_DATA, PJLINK_ERST_STATUS, \
    PJLINK_POWR_STATUS, PJLINK_VALID_CMD, E_WARN, E_ERROR, S_OFF, S_STANDBY, S_ON
'''
from tests.resources.projector.data import TEST_PIN, TEST1_DATA

pjlink_test = PJLink(Projector(**TEST1_DATA), pin=TEST_PIN, no_poll=True)
pjlink_test.ip = '127.0.0.1'


class TestPJLinkRouting(TestCase):
    """
    Tests for the PJLink module command routing
    """
    def setUp(self):
        '''
        TestPJLinkCommands part 2 initialization
        '''
        self.pjlink_test = PJLink(Projector(**TEST1_DATA), no_poll=True)

    def tearDown(self):
        '''
        TestPJLinkCommands part 2 cleanups
        '''
        self.pjlink_test = None

    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_process_command_call_clss(self, mock_log):
        """
        Test process_command calls proper function
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        log_text = '(127.0.0.1) Calling function for CLSS'
        mock_log.reset_mock()
        mock_process_clss = MagicMock()
        pjlink.pjlink_functions['CLSS'] = mock_process_clss

        # WHEN: process_command is called with valid function and data
        pjlink.process_command(cmd='CLSS', data='1')

        # THEN: Process method should have been called properly
        mock_log.debug.assert_called_with(log_text)
        mock_process_clss.assert_called_with('1')

    @patch.object(pjlink_test, 'change_status')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_process_command_err1(self, mock_log, mock_change_status):
        """
        Test ERR1 - Undefined projector function
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        log_text = '(127.0.0.1) Projector returned error "ERR1"'
        mock_change_status.reset_mock()
        mock_log.reset_mock()

        # WHEN: process_command called with ERR1
        pjlink.process_command(cmd='CLSS', data=PJLINK_ERRORS[E_UNDEFINED])

        # THEN: Error should be logged and status_change should be called
        mock_change_status.assert_called_once_with(E_UNDEFINED, 'Undefined Command: "CLSS"')
        mock_log.error.assert_called_with(log_text)

    @patch.object(pjlink_test, 'change_status')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_process_command_err2(self, mock_log, mock_change_status):
        """
        Test ERR2 - Parameter Error
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        log_text = '(127.0.0.1) Projector returned error "ERR2"'
        mock_change_status.reset_mock()
        mock_log.reset_mock()

        # WHEN: process_command called with ERR2
        pjlink.process_command(cmd='CLSS', data=PJLINK_ERRORS[E_PARAMETER])

        # THEN: Error should be logged and status_change should be called
        mock_change_status.assert_called_once_with(E_PARAMETER)
        mock_log.error.assert_called_with(log_text)

    @patch.object(pjlink_test, 'change_status')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_process_command_err3(self, mock_log, mock_change_status):
        """
        Test ERR3 - Unavailable error
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        log_text = '(127.0.0.1) Projector returned error "ERR3"'
        mock_change_status.reset_mock()
        mock_log.reset_mock()

        # WHEN: process_command called with ERR3
        pjlink.process_command(cmd='CLSS', data=PJLINK_ERRORS[E_UNAVAILABLE])

        # THEN: Error should be logged and status_change should be called
        mock_change_status.assert_called_once_with(E_UNAVAILABLE)
        mock_log.error.assert_called_with(log_text)

    @patch.object(pjlink_test, 'change_status')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_process_command_err4(self, mock_log, mock_change_status):
        """
        Test ERR3 - Unavailable error
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        log_text = '(127.0.0.1) Projector returned error "ERR4"'
        mock_change_status.reset_mock()
        mock_log.reset_mock()

        # WHEN: process_command called with ERR3
        pjlink.process_command(cmd='CLSS', data=PJLINK_ERRORS[E_PROJECTOR])

        # THEN: Error should be logged and status_change should be called
        mock_change_status.assert_called_once_with(E_PROJECTOR)
        mock_log.error.assert_called_with(log_text)

    @patch.object(pjlink_test, 'projectorAuthentication')
    @patch.object(pjlink_test, 'change_status')
    @patch.object(pjlink_test, 'disconnect_from_host')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_process_command_erra(self, mock_log, mock_disconnect, mock_change_status, mock_err_authenticate):
        """
        Test ERRA - Authentication Error
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        log_text = '(127.0.0.1) Projector returned error "ERRA"'
        mock_change_status.reset_mock()
        mock_log.reset_mock()

        # WHEN: process_command called with ERRA
        pjlink.process_command(cmd='CLSS', data=PJLINK_ERRORS[E_AUTHENTICATION])

        # THEN: Error should be logged and several methods should be called
        self.assertTrue(mock_disconnect.called, 'disconnect_from_host should have been called')
        mock_change_status.assert_called_once_with(E_AUTHENTICATION)
        mock_log.error.assert_called_with(log_text)

    def test_process_command_future(self):
        """
        Test command valid but no method to process yet
        """
        # GIVEN: Initial mocks and data
        mock_log = patch.object(openlp.core.projectors.pjlink, 'log').start()
        mock_functions = patch.object(self.pjlink_test, 'pjlink_functions').start()
        mock_functions.return_value = []

        pjlink = self.pjlink_test
        log_text = '(111.111.111.111) Unable to process command="CLSS" (Future option?)'

        # WHEN: process_command called with an unknown command
        pjlink.process_command(cmd='CLSS', data='DONT CARE')

        # THEN: Error should be logged and no command called
        self.assertFalse(mock_functions.called, 'Should not have gotten to the end of the method')
        mock_log.warning.assert_called_once_with(log_text)

    @patch.object(pjlink_test, 'pjlink_functions')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_process_command_invalid(self, mock_log, mock_functions):
        """
        Test not a valid command
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        mock_functions.reset_mock()
        mock_log.reset_mock()

        # WHEN: process_command called with an unknown command
        pjlink.process_command(cmd='Unknown', data='Dont Care')
        log_text = '(127.0.0.1) Ignoring command="Unknown" (Invalid/Unknown)'

        # THEN: Error should be logged and no command called
        self.assertFalse(mock_functions.called, 'Should not have gotten to the end of the method')
        mock_log.error.assert_called_once_with(log_text)

    def test_process_command_ok(self):
        """
        Test command returned success
        """
        # GIVEN: Initial mocks and data
        mock_log = patch.object(openlp.core.projectors.pjlink, 'log').start()
        mock_send_command = patch.object(self.pjlink_test, 'send_command').start()

        pjlink = self.pjlink_test
        log_text = '(111.111.111.111) Command "POWR" returned OK'

        # WHEN: process_command called with a command that returns OK
        pjlink.process_command(cmd='POWR', data='OK')

        # THEN: Appropriate calls should have been made
        mock_log.debug.assert_called_with(log_text)
        mock_send_command.assert_called_once_with(cmd='POWR')
