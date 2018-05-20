
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
from openlp.core.projectors.constants import PJLINK_PORT

from openlp.core.projectors.pjlink import PJLinkUDP
from tests.resources.projector.data import TEST1_DATA


class TestPJLinkBase(TestCase):
    """
    Tests for the PJLinkUDP class
    """
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_get_datagram_data_negative_zero_length(self, mock_log):
        """
        Test get_datagram when pendingDatagramSize = 0
        """
        # GIVEN: Test setup
        pjlink_udp = PJLinkUDP()
        log_warning_calls = [call('(UDP) No data (-1)')]
        log_debug_calls = [call('(UDP) PJLinkUDP() Initialized for port 4352'),
                           call('(UDP) get_datagram() - Receiving data')]
        with patch.object(pjlink_udp, 'pendingDatagramSize') as mock_datagram, \
                patch.object(pjlink_udp, 'readDatagram') as mock_read:
            mock_datagram.return_value = -1
            mock_read.return_value = ('', TEST1_DATA['ip'], PJLINK_PORT)

            # WHEN: get_datagram called with 0 bytes ready
            pjlink_udp.get_datagram()

            # THEN: Log entries should be made and method returns
            mock_log.warning.assert_has_calls(log_warning_calls)
            mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_get_datagram_data_no_data(self, mock_log):
        """
        Test get_datagram when data length = 0
        """
        # GIVEN: Test setup
        pjlink_udp = PJLinkUDP()
        log_warning_calls = [call('(UDP) get_datagram() called when pending data size is 0')]
        log_debug_calls = [call('(UDP) PJLinkUDP() Initialized for port 4352'),
                           call('(UDP) get_datagram() - Receiving data')]
        with patch.object(pjlink_udp, 'pendingDatagramSize') as mock_datagram, \
                patch.object(pjlink_udp, 'readDatagram') as mock_read:
            mock_datagram.return_value = 0
            mock_read.return_value = ('', TEST1_DATA['ip'], PJLINK_PORT)

            # WHEN: get_datagram called with 0 bytes ready
            pjlink_udp.get_datagram()

            # THEN: Log entries should be made and method returns
            mock_log.warning.assert_has_calls(log_warning_calls)
            mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_get_datagram_pending_zero_length(self, mock_log):
        """
        Test get_datagram when pendingDatagramSize = 0
        """
        # GIVEN: Test setup
        pjlink_udp = PJLinkUDP()
        log_warning_calls = [call('(UDP) get_datagram() called when pending data size is 0')]
        log_debug_calls = [call('(UDP) PJLinkUDP() Initialized for port 4352'),
                           call('(UDP) get_datagram() - Receiving data')]
        with patch.object(pjlink_udp, 'pendingDatagramSize') as mock_datagram:
            mock_datagram.return_value = 0

            # WHEN: get_datagram called with 0 bytes ready
            pjlink_udp.get_datagram()

            # THEN: Log entries should be made and method returns
            mock_log.warning.assert_has_calls(log_warning_calls)
            mock_log.debug.assert_has_calls(log_debug_calls)
