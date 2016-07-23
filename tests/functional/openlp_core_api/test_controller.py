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
Functional tests to test the API Error Class.
"""

from unittest import TestCase

from openlp.core.api import ApiController
from openlp.core.common import Registry

from tests.functional import patch


class TestController(TestCase):
    """
    A test suite to test out the Error in the API code
    """
    @patch('openlp.core.api.controller.Poller')
    @patch('openlp.core.api.controller.WebSocketServer')
    @patch('openlp.core.api.controller.HttpServer')
    def test_bootstrap(self, mock_http, mock_ws, mock_poll):
        """
        Test the controller creates the correct objects.
        """
        # GIVEN: A controller
        Registry.create()
        apicontroller = ApiController()

        # WHEN: I call the bootstrap
        apicontroller.bootstrap_post_set_up()

        # THEN: the api environment should have been created
        self.assertEquals(1, mock_http.call_count, 'The Http server should have been called once')
        self.assertEquals(1, mock_ws.call_count, 'The WS server should have been called once')
        self.assertEquals(1, mock_poll.call_count, 'The OpenLPPoll should have been called once')
