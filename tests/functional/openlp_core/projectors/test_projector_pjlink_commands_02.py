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
Package to test the openlp.core.projectors.pjlink commands package.
"""
from unittest import TestCase
from unittest.mock import patch, call

import openlp.core.projectors.pjlink
from openlp.core.projectors.constants import S_CONNECTED
from openlp.core.projectors.db import Projector
from openlp.core.projectors.pjlink import PJLink

from tests.resources.projector.data import TEST_HASH, TEST_PIN, TEST_SALT, TEST1_DATA


class TestPJLinkCommands(TestCase):
    """
    Tests for the PJLinkCommands class part 2
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

    def test_process_pjlink_normal(self):
        """
        Test initial connection prompt with no authentication
        """
        # GIVEN: Initial mocks and data
        mock_log = patch.object(openlp.core.projectors.pjlink, "log").start()
        mock_disconnect_from_host = patch.object(self.pjlink_test, 'disconnect_from_host').start()
        mock_send_command = patch.object(self.pjlink_test, 'send_command').start()
        mock_readyRead = patch.object(self.pjlink_test, 'readyRead').start()
        mock_change_status = patch.object(self.pjlink_test, 'change_status').start()
        pjlink = self.pjlink_test
        pjlink.pin = None
        log_check = [call("({111.111.111.111}) process_pjlink(): Sending 'CLSS' initial command'"), ]

        # WHEN: process_pjlink called with no authentication required
        pjlink.process_pjlink(data="0")

        # THEN: proper processing should have occured
        mock_log.debug.has_calls(log_check)
        mock_disconnect_from_host.assert_not_called()
        self.assertEqual(mock_readyRead.connect.call_count, 1, 'Should have only been called once')
        mock_change_status.assert_called_once_with(S_CONNECTED)
        mock_send_command.assert_called_with(cmd='CLSS', priority=True, salt=None)

    def test_process_pjlink_authenticate(self):
        """
        Test initial connection prompt with authentication
        """
        # GIVEN: Initial mocks and data
        mock_log = patch.object(openlp.core.projectors.pjlink, "log").start()
        mock_disconnect_from_host = patch.object(self.pjlink_test, 'disconnect_from_host').start()
        mock_send_command = patch.object(self.pjlink_test, 'send_command').start()
        mock_readyRead = patch.object(self.pjlink_test, 'readyRead').start()
        mock_change_status = patch.object(self.pjlink_test, 'change_status').start()
        pjlink = self.pjlink_test
        pjlink.pin = TEST_PIN
        log_check = [call("({111.111.111.111}) process_pjlink(): Sending 'CLSS' initial command'"), ]

        # WHEN: process_pjlink called with no authentication required
        pjlink.process_pjlink(data='1 {salt}'.format(salt=TEST_SALT))

        # THEN: proper processing should have occured
        mock_log.debug.has_calls(log_check)
        mock_disconnect_from_host.assert_not_called()
        self.assertEqual(mock_readyRead.connect.call_count, 1, 'Should have only been called once')
        mock_change_status.assert_called_once_with(S_CONNECTED)
        mock_send_command.assert_called_with(cmd='CLSS', priority=True, salt=TEST_HASH)

    def test_process_pjlink_normal_pin_set_error(self):
        """
        Test process_pjlinnk called with no authentication but pin is set
        """
        # GIVEN: Initial mocks and data
        # GIVEN: Initial mocks and data
        mock_log = patch.object(openlp.core.projectors.pjlink, 'log').start()
        mock_disconnect_from_host = patch.object(self.pjlink_test, 'disconnect_from_host').start()
        mock_send_command = patch.object(self.pjlink_test, 'send_command').start()
        pjlink = self.pjlink_test
        pjlink.pin = TEST_PIN
        log_check = [call('(111.111.111.111) Normal connection but PIN set - aborting'), ]

        # WHEN: process_pjlink called with invalid authentication scheme
        pjlink.process_pjlink(data='0')

        # THEN: Proper calls should be made
        mock_log.error.assert_has_calls(log_check)
        self.assertEqual(mock_disconnect_from_host.call_count, 1, 'Should have only been called once')
        mock_send_command.assert_not_called()

    def test_process_pjlink_normal_with_salt_error(self):
        """
        Test process_pjlinnk called with no authentication but pin is set
        """
        # GIVEN: Initial mocks and data
        # GIVEN: Initial mocks and data
        mock_log = patch.object(openlp.core.projectors.pjlink, 'log').start()
        mock_disconnect_from_host = patch.object(self.pjlink_test, 'disconnect_from_host').start()
        mock_send_command = patch.object(self.pjlink_test, 'send_command').start()
        pjlink = self.pjlink_test
        pjlink.pin = TEST_PIN
        log_check = [call('(111.111.111.111) Normal connection with extra information - aborting'), ]

        # WHEN: process_pjlink called with invalid authentication scheme
        pjlink.process_pjlink(data='0 {salt}'.format(salt=TEST_SALT))

        # THEN: Proper calls should be made
        mock_log.error.assert_has_calls(log_check)
        self.assertEqual(mock_disconnect_from_host.call_count, 1, 'Should have only been called once')
        mock_send_command.assert_not_called()

    def test_process_pjlink_invalid_authentication_scheme_length_error(self):
        """
        Test initial connection prompt with authentication scheme longer than 1 character
        """
        # GIVEN: Initial mocks and data
        mock_log = patch.object(openlp.core.projectors.pjlink, 'log').start()
        mock_disconnect_from_host = patch.object(self.pjlink_test, 'disconnect_from_host').start()
        mock_send_command = patch.object(self.pjlink_test, 'send_command').start()
        pjlink = self.pjlink_test
        log_check = [call('(111.111.111.111) Invalid initial authentication scheme - aborting'), ]

        # WHEN: process_pjlink called with invalid authentication scheme
        pjlink.process_pjlink(data='01')

        # THEN: socket should be closed and invalid data logged
        mock_log.error.assert_has_calls(log_check)
        self.assertEqual(mock_disconnect_from_host.call_count, 1, 'Should have only been called once')
        mock_send_command.assert_not_called()

    def test_process_pjlink_invalid_authentication_data_length_error(self):
        """
        Test initial connection prompt with authentication no salt
        """
        # GIVEN: Initial mocks and data
        mock_log = patch.object(openlp.core.projectors.pjlink, 'log').start()
        mock_disconnect_from_host = patch.object(self.pjlink_test, 'disconnect_from_host').start()
        mock_send_command = patch.object(self.pjlink_test, 'send_command').start()
        log_check = [call('(111.111.111.111) Authenticated connection but not enough info - aborting'), ]
        pjlink = self.pjlink_test

        # WHEN: process_pjlink called with no salt
        pjlink.process_pjlink(data='1')

        # THEN: socket should be closed and invalid data logged
        mock_log.error.assert_has_calls(log_check)
        self.assertEqual(mock_disconnect_from_host.call_count, 1, 'Should have only been called once')
        mock_send_command.assert_not_called()

    def test_process_pjlink_authenticate_pin_not_set_error(self):
        """
        Test process_pjlink authentication but pin not set
        """
        # GIVEN: Initial mocks and data
        mock_log = patch.object(openlp.core.projectors.pjlink, 'log').start()
        mock_disconnect_from_host = patch.object(self.pjlink_test, 'disconnect_from_host').start()
        mock_send_command = patch.object(self.pjlink_test, 'send_command').start()
        log_check = [call('(111.111.111.111) Authenticate connection but no PIN - aborting'), ]
        pjlink = self.pjlink_test
        pjlink.pin = None

        # WHEN: process_pjlink called with no salt
        pjlink.process_pjlink(data='1 {salt}'.format(salt=TEST_SALT))

        # THEN: socket should be closed and invalid data logged
        mock_log.error.assert_has_calls(log_check)
        self.assertEqual(mock_disconnect_from_host.call_count, 1, 'Should have only been called once')
        mock_send_command.assert_not_called()
