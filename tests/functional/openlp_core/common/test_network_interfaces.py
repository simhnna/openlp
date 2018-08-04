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
Functional tests to test calls for network interfaces.
"""
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

import openlp.core.common
from openlp.core.common import get_local_ip4

from tests.helpers.testmixin import TestMixin

lo_address_attrs = {'isValid.return_value': True,
                    'flags.return_value': True,
                    'InterfaceFlags.return_value': True,
                    'name.return_value': 'lo',
                    'broadcast.toString.return_value': '127.0.0.255',
                    'netmask.toString.return_value': '255.0.0.0',
                    'prefixLength.return_value': 8,
                    'ip.protocol.return_value': True}


class TestInterfaces(TestCase, TestMixin):
    """
    A test suite to test out functions/methods that use network interface(s).
    """
    def setUp(self):
        """
        Create an instance and a few example actions.
        """
        self.build_settings()

        self.ip4_lo_address = MagicMock()
        self.ip4_lo_address.configure_mock(**lo_address_attrs)

    def tearDown(self):
        """
        Clean up
        """
        self.destroy_settings()

    @patch.object(openlp.core.common, 'log')
    def test_ip4_no_interfaces(self, mock_log):
        """
        Test no interfaces available
        """
        # GIVEN: Test environment
        call_warning = [call('No active IPv4 network interfaces detected')]

        with patch('openlp.core.common.QNetworkInterface') as mock_newtork_interface:
            mock_newtork_interface.allInterfaces.return_value = []

            # WHEN: get_local_ip4 is called
            ifaces = get_local_ip4()

            # THEN: There should not be any interfaces detected
            assert not ifaces, 'There should have been no active interfaces'
            mock_log.warning.assert_has_calls(call_warning)
