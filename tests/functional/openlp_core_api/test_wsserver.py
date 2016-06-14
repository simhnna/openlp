# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2016 OpenLP Developers                                   #
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
Functional tests to test the Http Server Class.
"""

from unittest import TestCase

from openlp.core.api import WsServer

from tests.functional import patch


class TestWSServer(TestCase):
    """
    A test suite to test starting the websocket server
    """
    @patch('openlp.core.api.wsserver.WSThread')
    @patch('openlp.core.api.wsserver.QtCore.QThread')
    def test_serverstart(self, mock_qthread, mock_thread):
        """
        Test the starting of the WebSockets Server
        """
        # GIVEN: A new httpserver
        # WHEN: I start the server
        server = WsServer()

        # THEN: the api environment should have been created
        self.assertEquals(1, mock_qthread.call_count, 'The qthread should have been called once')
        self.assertEquals(1, mock_thread.call_count, 'The http thread should have been called once')
