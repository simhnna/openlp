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
Functional tests to test the Http Server Class.
"""
from unittest import TestCase
from unittest.mock import MagicMock, patch

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.api.websockets import WebSocketServer
from openlp.core.api.poll import Poller
from tests.helpers.testmixin import TestMixin

__default_settings__ = {
    'api/twelve hour': True,
    'api/port': 4316,
    'api/user id': 'openlp',
    'api/password': 'password',
    'api/authentication enabled': False,
    'api/ip address': '0.0.0.0',
    'api/thumbnails': True,
    'songs/chord notation': True
}


class TestWSServer(TestCase, TestMixin):
    """
    A test suite to test starting the websocket server
    """
    def setUp(self):
        """
        Create the UI
        """
        self.build_settings()
        Settings().extend_default_settings(__default_settings__)
        Registry().create()
        self.poll = Poller()

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        self.destroy_settings()

    @patch('openlp.core.api.websockets.WebSocketWorker')
    @patch('openlp.core.api.websockets.QtCore.QThread')
    def test_serverstart(self, mock_qthread, mock_worker):
        """
        Test the starting of the WebSockets Server with the disabled flag set on
        """
        # GIVEN: A new httpserver
        # WHEN: I start the server
        Registry().set_flag('no_web_server', True)
        WebSocketServer()

        # THEN: the api environment should have been created
        assert mock_qthread.call_count == 1, 'The qthread should have been called once'
        assert mock_worker.call_count == 1, 'The http thread should have been called once'

    @patch('openlp.core.api.websockets.WebSocketWorker')
    @patch('openlp.core.api.websockets.QtCore.QThread')
    def test_serverstart_not_required(self, mock_qthread, mock_worker):
        """
        Test the starting of the WebSockets Server with the disabled flag set off
        """
        # GIVEN: A new httpserver and the server is not required
        # WHEN: I start the server
        Registry().set_flag('no_web_server', False)
        WebSocketServer()

        # THEN: the api environment should have been created
        assert mock_qthread.call_count == 0, 'The qthread should not have been called'
        assert mock_worker.call_count == 0, 'The http thread should not have been called'

    def test_main_poll(self):
        """
        Test the main_poll function returns the correct JSON
        """
        # WHEN: the live controller has 5 slides
        mocked_live_controller = MagicMock()
        mocked_live_controller.slide_count = 5
        Registry().register('live_controller', mocked_live_controller)
        # THEN: the live json should be generated
        main_json = self.poll.main_poll()
        assert b'{"results": {"slide_count": 5}}' == main_json, 'The return value should match the defined json'

    def test_poll(self):
        """
        Test the poll function returns the correct JSON
        """
        # GIVEN: the system is configured with a set of data
        mocked_service_manager = MagicMock()
        mocked_service_manager.service_id = 21
        mocked_live_controller = MagicMock()
        mocked_live_controller.selected_row = 5
        mocked_live_controller.service_item = MagicMock()
        mocked_live_controller.service_item.unique_identifier = '23-34-45'
        mocked_live_controller.blank_screen.isChecked.return_value = True
        mocked_live_controller.theme_screen.isChecked.return_value = False
        mocked_live_controller.desktop_screen.isChecked.return_value = False
        Registry().register('live_controller', mocked_live_controller)
        Registry().register('service_manager', mocked_service_manager)
        # WHEN: The poller polls
        with patch.object(self.poll, 'is_stage_active') as mocked_is_stage_active, \
                patch.object(self.poll, 'is_live_active') as mocked_is_live_active, \
                patch.object(self.poll, 'is_chords_active') as mocked_is_chords_active:
            mocked_is_stage_active.return_value = True
            mocked_is_live_active.return_value = True
            mocked_is_chords_active.return_value = True
            poll_json = self.poll.poll()
        # THEN: the live json should be generated and match expected results
        assert poll_json['results']['blank'] is True, 'The blank return value should be True'
        assert poll_json['results']['theme'] is False, 'The theme return value should be False'
        assert poll_json['results']['display'] is False, 'The display return value should be False'
        assert poll_json['results']['isSecure'] is False, 'The isSecure return value should be False'
        assert poll_json['results']['isAuthorised'] is False, 'The isAuthorised return value should be False'
        assert poll_json['results']['twelve'] is False, 'The twelve return value should be False'
        assert poll_json['results']['version'] == 3, 'The version return value should be 3'
        assert poll_json['results']['slide'] == 5, 'The slide return value should be 5'
        assert poll_json['results']['service'] == 21, 'The version return value should be 21'
        assert poll_json['results']['item'] == '23-34-45', 'The item return value should match 23-34-45'
