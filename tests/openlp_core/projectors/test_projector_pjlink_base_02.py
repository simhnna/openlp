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
from unittest.mock import call, patch

import openlp.core.projectors.pjlink

from openlp.core.projectors.constants import S_NOT_CONNECTED
from openlp.core.projectors.db import Projector
from openlp.core.projectors.pjlink import PJLink
from tests.resources.projector.data import TEST1_DATA


class TestPJLinkBase(TestCase):
    """
    Tests for the PJLink module
    """
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'state')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'reset_information')
    @patch.object(openlp.core.projectors.pjlink.PJLink, '_send_command')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_send_command_no_data(self, mock_log, mock_send_command, mock_reset, mock_state):
        """
        Test _send_command with no data to send
        """
        # GIVEN: Test object
        log_warning_calls = [call('({ip}) send_command(): Not connected - returning'.format(ip=TEST1_DATA['name']))]

        log_debug_calls = [call('PJlink(projector="< Projector(id="None", ip="111.111.111.111", port="1111", '
                                'mac_adx="11:11:11:11:11:11", pin="1111", name="___TEST_ONE___", '
                                'location="location one", notes="notes one", pjlink_name="None", '
                                'pjlink_class="None", manufacturer="None", model="None", '
                                'serial_no="Serial Number 1", other="None", sources="None", source_list="[]", '
                                'model_filter="Filter type 1", model_lamp="Lamp type 1", '
                                'sw_version="Version 1") >", args="()" kwargs="{\'no_poll\': True}")'),
                           call('PJlinkCommands(args=() kwargs={})')]
        mock_state.return_value = S_NOT_CONNECTED
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.send_queue = []
        pjlink.priority_queue = []

        # WHEN: _send_command called with no data and queue's empty
        pjlink.send_command(cmd='DONTCARE')

        # THEN:
        mock_log.debug.assert_has_calls(log_debug_calls)
        mock_log.warning.assert_has_calls(log_warning_calls)
        assert mock_reset.called is True
        assert mock_reset.called is True

    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_local_send_command_no_data(self, mock_log):
        """
        Test _send_command with no data to send
        """
        # GIVEN: Test object
        log_debug_calls = [call('PJlink(projector="< Projector(id="None", ip="111.111.111.111", port="1111", '
                                'mac_adx="11:11:11:11:11:11", pin="1111", name="___TEST_ONE___", '
                                'location="location one", notes="notes one", pjlink_name="None", '
                                'pjlink_class="None", manufacturer="None", model="None", '
                                'serial_no="Serial Number 1", other="None", sources="None", source_list="[]", '
                                'model_filter="Filter type 1", model_lamp="Lamp type 1", '
                                'sw_version="Version 1") >", args="()" kwargs="{\'no_poll\': True}")'),
                           call('PJlinkCommands(args=() kwargs={})'),
                           call('(___TEST_ONE___) reset_information() connect status is S_NOT_CONNECTED'),
                           call('(___TEST_ONE___) _send_command(): Nothing to send - returning')]

        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.send_queue = []
        pjlink.priority_queue = []

        # WHEN: _send_command called with no data and queue's emtpy
        # Patch here since pjlink does not have socket_timer until after instantiation
        with patch.object(pjlink, 'socket_timer') as mock_timer:
            pjlink._send_command(data=None, utf8=False)

            # THEN:
            mock_log.debug.assert_has_calls(log_debug_calls)
            assert mock_timer.called is False
