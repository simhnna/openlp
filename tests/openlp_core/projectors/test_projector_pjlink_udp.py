
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
Package to test the PJLink UDP functions
"""

from unittest import TestCase
from unittest.mock import call, patch

import openlp.core.projectors.pjlink
from openlp.core.projectors.constants import PJLINK_MAX_PACKET, PJLINK_PORT, PJLINK_PREFIX

from openlp.core.projectors.db import Projector
from openlp.core.projectors.pjlink import PJLinkUDP
from tests.resources.projector.data import TEST1_DATA, TEST2_DATA


class TestPJLinkBase(TestCase):
    """
    Tests for the PJLinkUDP class
    """
    def setUp(self):
        """
        Setup generic test conditions
        """
        self.test_list = [Projector(**TEST1_DATA), Projector(**TEST2_DATA)]

    def tearDown(self):
        """
        Close generic test condidtions
        """
        self.test_list = None

    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_get_datagram_data_invalid_class(self, mock_log):
        """
        Test get_datagram with invalid class number
        """
        # GIVEN: Test setup
        pjlink_udp = PJLinkUDP(projector_list=self.test_list)
        log_warn_calls = [call('(UDP) Invalid packet - missing/invalid PJLink class version')]
        log_debug_calls = [call('(UDP) PJLinkUDP() Initialized'),
                           call('(UDP) get_datagram() - Receiving data'),
                           call('(UDP) 24 bytes received from 111.111.111.111 on port 4352'),
                           call('(UDP) packet "%1ACKN=11:11:11:11:11:11"')]
        with patch.object(pjlink_udp, 'pendingDatagramSize') as mock_datagram, \
                patch.object(pjlink_udp, 'readDatagram') as mock_read:
            mock_datagram.return_value = 24
            mock_read.return_value = ('{prefix}1ACKN={mac}'.format(prefix=PJLINK_PREFIX, mac=TEST1_DATA['mac_adx']),
                                      TEST1_DATA['ip'], PJLINK_PORT)

            # WHEN: get_datagram called with 0 bytes ready
            pjlink_udp.get_datagram()

            # THEN: Log entries should be made and method returns
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_log.warn.assert_has_calls(log_warn_calls)

    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_get_datagram_data_invalid_command(self, mock_log):
        """
        Test get_datagram with invalid PJLink UDP command
        """
        # GIVEN: Test setup
        pjlink_udp = PJLinkUDP(projector_list=self.test_list)
        log_warn_calls = [call('(UDP) Invalid packet - not a valid PJLink UDP reply')]
        log_debug_calls = [call('(UDP) PJLinkUDP() Initialized'),
                           call('(UDP) get_datagram() - Receiving data'),
                           call('(UDP) 24 bytes received from 111.111.111.111 on port 4352'),
                           call('(UDP) packet "%2DUMB=11:11:11:11:11:11"')]
        with patch.object(pjlink_udp, 'pendingDatagramSize') as mock_datagram, \
                patch.object(pjlink_udp, 'readDatagram') as mock_read:
            mock_datagram.return_value = 24
            mock_read.return_value = ('{prefix}2DUMB={mac}'.format(prefix=PJLINK_PREFIX, mac=TEST1_DATA['mac_adx']),
                                      TEST1_DATA['ip'], PJLINK_PORT)

            # WHEN: get_datagram called with 0 bytes ready
            pjlink_udp.get_datagram()

            # THEN: Log entries should be made and method returns
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_log.warn.assert_has_calls(log_warn_calls)

    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_get_datagram_data_invalid_prefix(self, mock_log):
        """
        Test get_datagram when prefix != PJLINK_PREFIX
        """
        # GIVEN: Test setup
        pjlink_udp = PJLinkUDP(projector_list=self.test_list)
        log_warn_calls = [call('(UDP) Invalid packet - does not start with PJLINK_PREFIX')]
        log_debug_calls = [call('(UDP) PJLinkUDP() Initialized'),
                           call('(UDP) get_datagram() - Receiving data'),
                           call('(UDP) 24 bytes received from 111.111.111.111 on port 4352'),
                           call('(UDP) packet "$2ACKN=11:11:11:11:11:11"')]
        with patch.object(pjlink_udp, 'pendingDatagramSize') as mock_datagram, \
                patch.object(pjlink_udp, 'readDatagram') as mock_read:
            mock_datagram.return_value = 24
            mock_read.return_value = ('{prefix}2ACKN={mac}'.format(prefix='$', mac=TEST1_DATA['mac_adx']),
                                      TEST1_DATA['ip'], PJLINK_PORT)

            # WHEN: get_datagram called with 0 bytes ready
            pjlink_udp.get_datagram()

            # THEN: Log entries should be made and method returns
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_log.warn.assert_has_calls(log_warn_calls)

    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_get_datagram_data_invalid_separator(self, mock_log):
        """
        Test get_datagram when separator not equal to =
        """
        # GIVEN: Test setup
        pjlink_udp = PJLinkUDP(projector_list=self.test_list)
        log_warn_calls = [call('(UDP) Invalid packet - separator missing')]
        log_debug_calls = [call('(UDP) PJLinkUDP() Initialized'),
                           call('(UDP) get_datagram() - Receiving data'),
                           call('(UDP) 24 bytes received from 111.111.111.111 on port 4352'),
                           call('(UDP) packet "%2ACKN 11:11:11:11:11:11"')]
        with patch.object(pjlink_udp, 'pendingDatagramSize') as mock_datagram, \
                patch.object(pjlink_udp, 'readDatagram') as mock_read:
            mock_datagram.return_value = 24
            mock_read.return_value = ('{prefix}2ACKN {mac}'.format(prefix=PJLINK_PREFIX, mac=TEST1_DATA['mac_adx']),
                                      TEST1_DATA['ip'], PJLINK_PORT)

            # WHEN: get_datagram called with 0 bytes ready
            pjlink_udp.get_datagram()

            # THEN: Log entries should be made and method returns
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_log.warn.assert_has_calls(log_warn_calls)

    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_get_datagram_data_long(self, mock_log):
        """
        Test get_datagram when datagram > PJLINK_MAX_PACKET
        """
        # GIVEN: Test setup
        pjlink_udp = PJLinkUDP(projector_list=self.test_list)
        log_warn_calls = [call('(UDP) Invalid packet - length too long')]
        log_debug_calls = [call('(UDP) PJLinkUDP() Initialized'),
                           call('(UDP) get_datagram() - Receiving data'),
                           call('(UDP) 143 bytes received from 111.111.111.111 on port 4352'),
                           call('(UDP) packet "%2ACKN={long}"'.format(long='X' * PJLINK_MAX_PACKET))]
        with patch.object(pjlink_udp, 'pendingDatagramSize') as mock_datagram, \
                patch.object(pjlink_udp, 'readDatagram') as mock_read:
            mock_datagram.return_value = PJLINK_MAX_PACKET + 7
            mock_read.return_value = ('{prefix}2ACKN={long}'.format(prefix=PJLINK_PREFIX,
                                                                    long='X' * PJLINK_MAX_PACKET),
                                      TEST1_DATA['ip'], PJLINK_PORT)

            # WHEN: get_datagram called with 0 bytes ready
            pjlink_udp.get_datagram()

            # THEN: Log entries should be made and method returns
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_log.warn.assert_has_calls(log_warn_calls)

    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_get_datagram_data_negative_zero_length(self, mock_log):
        """
        Test get_datagram when pendingDatagramSize = 0
        """
        # GIVEN: Test setup
        pjlink_udp = PJLinkUDP(projector_list=self.test_list)
        log_warn_calls = [call('(UDP) No data (-1)')]
        log_debug_calls = [call('(UDP) PJLinkUDP() Initialized'),
                           call('(UDP) get_datagram() - Receiving data')]
        with patch.object(pjlink_udp, 'pendingDatagramSize') as mock_datagram, \
                patch.object(pjlink_udp, 'readDatagram') as mock_read:
            mock_datagram.return_value = -1
            mock_read.return_value = ('', TEST1_DATA['ip'], PJLINK_PORT)

            # WHEN: get_datagram called with 0 bytes ready
            pjlink_udp.get_datagram()

            # THEN: Log entries should be made and method returns
            mock_log.warn.assert_has_calls(log_warn_calls)
            mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_get_datagram_data_no_data(self, mock_log):
        """
        Test get_datagram when data length = 0
        """
        # GIVEN: Test setup
        pjlink_udp = PJLinkUDP(projector_list=self.test_list)
        log_warn_calls = [call('(UDP) Invalid packet - not enough data')]
        log_debug_calls = [call('(UDP) PJLinkUDP() Initialized'),
                           call('(UDP) get_datagram() - Receiving data')]
        with patch.object(pjlink_udp, 'pendingDatagramSize') as mock_datagram, \
                patch.object(pjlink_udp, 'readDatagram') as mock_read:
            mock_datagram.return_value = 1
            mock_read.return_value = ('', TEST1_DATA['ip'], PJLINK_PORT)

            # WHEN: get_datagram called with 0 bytes ready
            pjlink_udp.get_datagram()

            # THEN: Log entries should be made and method returns
            mock_log.warn.assert_has_calls(log_warn_calls)
            mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_get_datagram_data_short(self, mock_log):
        """
        Test get_datagram when data length < 8
        """
        # GIVEN: Test setup
        pjlink_udp = PJLinkUDP(projector_list=self.test_list)
        log_warn_calls = [call('(UDP) Invalid packet - not enough data')]
        log_debug_calls = [call('(UDP) PJLinkUDP() Initialized'),
                           call('(UDP) get_datagram() - Receiving data')]
        with patch.object(pjlink_udp, 'pendingDatagramSize') as mock_datagram, \
                patch.object(pjlink_udp, 'readDatagram') as mock_read:
            mock_datagram.return_value = 6
            mock_read.return_value = ('{prefix}2ACKN'.format(prefix=PJLINK_PREFIX), TEST1_DATA['ip'], PJLINK_PORT)

            # WHEN: get_datagram called with 0 bytes ready
            pjlink_udp.get_datagram()

            # THEN: Log entries should be made and method returns
            mock_log.warn.assert_has_calls(log_warn_calls)
            mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_get_datagram_pending_zero_length(self, mock_log):
        """
        Test get_datagram when pendingDatagramSize = 0
        """
        # GIVEN: Test setup
        pjlink_udp = PJLinkUDP(projector_list=self.test_list)
        log_warn_calls = [call('(UDP) get_datagram() called when pending data size is 0')]
        log_debug_calls = [call('(UDP) PJLinkUDP() Initialized'),
                           call('(UDP) get_datagram() - Receiving data')]
        with patch.object(pjlink_udp, 'pendingDatagramSize') as mock_datagram:
            mock_datagram.return_value = 0

            # WHEN: get_datagram called with 0 bytes ready
            pjlink_udp.get_datagram()

            # THEN: Log entries should be made and method returns
            mock_log.warn.assert_has_calls(log_warn_calls)
            mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_process_ackn_duplicate(self, mock_log):
        """
        Test process_ackn method with multiple calls with same data
        """
        # GIVEN: Test setup
        pjlink_udp = PJLinkUDP(projector_list=self.test_list)
        check_list = {TEST1_DATA['ip']: {'data': TEST1_DATA['mac_adx'], 'port': PJLINK_PORT}}
        log_warn_calls = [call('(UDP) Host {host} already replied - ignoring'.format(host=TEST1_DATA['ip']))]
        log_debug_calls = [call('(UDP) PJLinkUDP() Initialized'),
                           call('(UDP) Processing ACKN packet'),
                           call('(UDP) Adding {host} to ACKN list'.format(host=TEST1_DATA['ip'])),
                           call('(UDP) Processing ACKN packet')]

        # WHEN: process_ackn called twice with same data
        pjlink_udp.process_ackn(data=TEST1_DATA['mac_adx'], host=TEST1_DATA['ip'], port=PJLINK_PORT)
        pjlink_udp.process_ackn(data=TEST1_DATA['mac_adx'], host=TEST1_DATA['ip'], port=PJLINK_PORT)

        # THEN: pjlink_udp.ack_list should equal test_list
        # NOTE: This assert only returns AssertionError - does not list differences. Maybe add a compare function?
        if pjlink_udp.ackn_list != check_list:
            # Check this way so we can print differences to stdout
            print('\nackn_list: ', pjlink_udp.ackn_list)
            print('test_list: ', check_list)
            assert pjlink_udp.ackn_list == check_list
        mock_log.debug.assert_has_calls(log_debug_calls)
        mock_log.warn.assert_has_calls(log_warn_calls)

    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_process_ackn_multiple(self, mock_log):
        """
        Test process_ackn method with multiple calls
        """
        # GIVEN: Test setup
        pjlink_udp = PJLinkUDP(projector_list=self.test_list)
        check_list = {TEST1_DATA['ip']: {'data': TEST1_DATA['mac_adx'], 'port': PJLINK_PORT},
                      TEST2_DATA['ip']: {'data': TEST2_DATA['mac_adx'], 'port': PJLINK_PORT}}
        log_debug_calls = [call('(UDP) PJLinkUDP() Initialized'),
                           call('(UDP) Processing ACKN packet'),
                           call('(UDP) Adding {host} to ACKN list'.format(host=TEST1_DATA['ip'])),
                           call('(UDP) Processing ACKN packet'),
                           call('(UDP) Adding {host} to ACKN list'.format(host=TEST2_DATA['ip']))]

        # WHEN: process_ackn called twice with different data
        pjlink_udp.process_ackn(data=TEST1_DATA['mac_adx'], host=TEST1_DATA['ip'], port=PJLINK_PORT)
        pjlink_udp.process_ackn(data=TEST2_DATA['mac_adx'], host=TEST2_DATA['ip'], port=PJLINK_PORT)

        # THEN: pjlink_udp.ack_list should equal test_list
        # NOTE: This assert only returns AssertionError - does not list differences. Maybe add a compare function?
        if pjlink_udp.ackn_list != check_list:
            # Check this way so we can print differences to stdout
            print('\nackn_list: ', pjlink_udp.ackn_list)
            print('test_list: ', check_list)
            assert pjlink_udp.ackn_list == check_list
        mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_process_ackn_single(self, mock_log):
        """
        Test process_ackn method with single call
        """
        # GIVEN: Test setup
        pjlink_udp = PJLinkUDP(projector_list=self.test_list)
        check_list = {TEST1_DATA['ip']: {'data': TEST1_DATA['mac_adx'], 'port': PJLINK_PORT}}
        log_debug_calls = [call('(UDP) PJLinkUDP() Initialized'),
                           call('(UDP) Processing ACKN packet'),
                           call('(UDP) Adding {host} to ACKN list'.format(host=TEST1_DATA['ip']))]

        # WHEN: process_ackn called twice with different data
        pjlink_udp.process_ackn(data=TEST1_DATA['mac_adx'], host=TEST1_DATA['ip'], port=PJLINK_PORT)

        # THEN: pjlink_udp.ack_list should equal test_list
        # NOTE: This assert only returns AssertionError - does not list differences. Maybe add a compare function?
        if pjlink_udp.ackn_list != check_list:
            # Check this way so we can print differences to stdout
            print('\nackn_list: ', pjlink_udp.ackn_list)
            print('test_list: ', check_list)
            assert pjlink_udp.ackn_list == check_list
        mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_process_srch(self, mock_log):
        """
        Test process_srch method
        """
        # GIVEN: Test setup
        pjlink_udp = PJLinkUDP(projector_list=self.test_list)
        log_debug_calls = [call('(UDP) PJLinkUDP() Initialized'),
                           call('(UDP) SRCH packet received - ignoring')]

        # WHEN: process_srch called
        pjlink_udp.process_srch(data=None, host=None, port=None)

        # THEN: debug log entry should be entered
        mock_log.debug.assert_has_calls(log_debug_calls)
