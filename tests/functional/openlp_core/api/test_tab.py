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
This module contains tests for the lib submodule of the Remotes plugin.
"""
import re
from unittest import TestCase
from unittest.mock import patch

from PyQt5 import QtWidgets

from openlp.core.api.tab import ApiTab
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from tests.helpers.testmixin import TestMixin

__default_settings__ = {
    'api/twelve hour': True,
    'api/port': 4316,
    'api/user id': 'openlp',
    'api/password': 'password',
    'api/authentication enabled': False,
    'api/ip address': '0.0.0.0',
    'api/thumbnails': True,
    'remotes/download version': '0000_00_00'
}
ZERO_URL = '0.0.0.0'


class TestApiTab(TestCase, TestMixin):
    """
    Test the functions in the :mod:`lib` module.
    """
    @patch('openlp.core.api.tab.ApiTab.define_main_window_icon')
    @patch('openlp.core.api.tab.ApiTab.generate_icon')
    def setUp(self, mocked_main_window, mocked_icon):
        """
        Create the UI
        """
        self.setup_application()
        self.build_settings()
        Settings().extend_default_settings(__default_settings__)
        self.parent = QtWidgets.QMainWindow()
        Registry().create()
        Registry().set_flag('website_version', '00-00-0000')
        self.form = ApiTab(self.parent)

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.parent
        del self.form
        self.destroy_settings()

    def test_get_ip_address_default(self):
        """
        Test the get_ip_address function with ZERO_URL
        """
        # WHEN: the default ip address is given
        ip_address = self.form.get_ip_address(ZERO_URL)
        # THEN: the default ip address will be returned
        assert re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip_address), \
            'The return value should be a valid ip address'

    def test_get_ip_address_with_ip(self):
        """
        Test the get_ip_address function with given ip address
        """
        # GIVEN: An ip address
        given_ip = '192.168.1.1'
        # WHEN: the default ip address is given
        ip_address = self.form.get_ip_address(given_ip)
        # THEN: the default ip address will be returned
        assert ip_address == given_ip, 'The return value should be %s' % given_ip

    def test_set_urls(self):
        """
        Test the set_url function to generate correct url links
        """
        # GIVEN: An ip address
        self.form.address_edit.setText('192.168.1.1')
        # WHEN: the urls are generated
        self.form.set_urls()
        # THEN: the following links are returned
        assert self.form.remote_url.text() == "<a href=\"http://192.168.1.1:4316/\">http://192.168.1.1:4316/</a>", \
            'The return value should be a fully formed link'
        assert self.form.stage_url.text() == \
            "<a href=\"http://192.168.1.1:4316/stage\">http://192.168.1.1:4316/stage</a>", \
            'The return value should be a fully formed stage link'
        assert self.form.live_url.text() == \
            "<a href=\"http://192.168.1.1:4316/main\">http://192.168.1.1:4316/main</a>", \
            'The return value should be a fully formed main link'
