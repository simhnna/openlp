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
Package to test the openlp.core.projectors.pjlink base package.
"""
from unittest import TestCase
from unittest.mock import call, patch, MagicMock

from openlp.core.projectors.constants import E_PARAMETER, ERROR_STRING, S_ON, S_CONNECTED, S_QSOCKET_STATE
from openlp.core.projectors.db import Projector
from openlp.core.projectors.pjlink import PJLink

from tests.resources.projector.data import TEST1_DATA

pjlink_test = PJLink(Projector(**TEST1_DATA), no_poll=True)


class TestPJLinkBase(TestCase):
    """
    Tests for the PJLink module
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

    @patch.object(pjlink_test, 'change_status')
    def test_status_change(self, mock_change_status):
        """
        Test process_command call with ERR2 (Parameter) status
        """
        # GIVEN: Test object
        pjlink = pjlink_test

        # WHEN: process_command is called with "ERR2" status from projector
        pjlink.process_command('POWR', 'ERR2')

        # THEN: change_status should have called change_status with E_UNDEFINED
        #       as first parameter
        mock_change_status.called_with(E_PARAMETER,
                                       'change_status should have been called with "{}"'.format(
                                           ERROR_STRING[E_PARAMETER]))

    @patch.object(pjlink_test, 'disconnect_from_host')
    def test_socket_abort(self, mock_disconnect):
        """
        Test PJLink.socket_abort calls disconnect_from_host
        """
        # GIVEN: Test object
        pjlink = pjlink_test

        # WHEN: Calling socket_abort
        pjlink.socket_abort()

        # THEN: disconnect_from_host should be called
        self.assertTrue(mock_disconnect.called, 'Should have called disconnect_from_host')

    def test_poll_loop_not_connected(self):
        """
        Test PJLink.poll_loop not connected return
        """
        # GIVEN: Test object and mocks
        pjlink = pjlink_test
        pjlink.state = MagicMock()
        pjlink.timer = MagicMock()
        pjlink.state.return_value = False
        pjlink.ConnectedState = True

        # WHEN: PJLink.poll_loop called
        pjlink.poll_loop()

        # THEN: poll_loop should exit without calling any other method
        self.assertFalse(pjlink.timer.called, 'Should have returned without calling any other method')

    def test_poll_loop_start(self):
        """
        Test PJLink.poll_loop makes correct calls
        """
        # GIVEN: Mocks and test data
        mock_state = patch.object(self.pjlink_test, 'state').start()
        mock_state.return_value = S_QSOCKET_STATE['ConnectedState']
        mock_timer = patch.object(self.pjlink_test, 'timer').start()
        mock_timer.interval.return_value = 10
        mock_send_command = patch.object(self.pjlink_test, 'send_command').start()

        pjlink = self.pjlink_test
        pjlink.poll_time = 20
        pjlink.power = S_ON
        pjlink.source_available = None
        pjlink.other_info = None
        pjlink.manufacturer = None
        pjlink.model = None
        pjlink.pjlink_name = None
        pjlink.ConnectedState = S_CONNECTED
        call_list = [
            call('POWR'),
            call('ERST'),
            call('LAMP'),
            call('AVMT'),
            call('INPT'),
            call('INST'),
            call('INFO'),
            call('INF1'),
            call('INF2'),
            call('NAME'),
        ]

        # WHEN: PJLink.poll_loop is called
        pjlink.poll_loop()

        # THEN: proper calls were made to retrieve projector data
        # First, call to update the timer with the next interval
        self.assertTrue(mock_timer.setInterval.called)
        # Next, should have called the timer to start
        self.assertTrue(mock_timer.start.called, 'Should have started the timer')
        # Finally, should have called send_command with a list of projetctor status checks
        mock_send_command.assert_has_calls(call_list, 'Should have queued projector queries')
