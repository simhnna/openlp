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
from openlp.core.server import Server
from tests.utils.constants import RESOURCE_PATH
from tests.helpers.testmixin import TestMixin


class TestServer(TestCase, TestMixin):
    """
    Test the OpenLP app class
    """
    def setUp(self):
        #self.setup_application()
        #self.build_settings()
        #self.openlp = OpenLP([])
        with patch('PyQt5.QtNetwork.QLocalSocket'):
            self.server = Server()

    def tearDown(self):
        #self.destroy_settings()
        #del self.openlp
        #self.openlp = None
        self.server.close_server()
        pass

    def test_is_another_instance_running(self):
        # GIVEN: A running Server
        # WHEN: I ask for it to start
        self.server.is_another_instance_running()
        # THEN the following is called
        self.server.out_socket.waitForConnected.assert_called_once_with()
        self.server.out_socket.connectToServer.assert_called_once_with(self.server.id)
