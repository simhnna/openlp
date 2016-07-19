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
Functional test the routing code.
"""
from openlp.core.api.http.endpoint.core import main_endpoint

from unittest import TestCase
from openlp.core.common import Registry
from openlp.core.api.http import application

from tests.functional import MagicMock
from openlp.core.api.http import NotFound


class TestRouting(TestCase):
    """
    Test First Time Wizard import functions
    """
    def setUp(self):
        """
        Convert the application to a test application
        :return:
        """
        for route, views in application.route_map.items():
            application.route_map[route]['GET'] = MagicMock()

    def test_routing(self):
        """
        Test the Routing in the new application
        :return:
        """
        # GIVE: I a new test suite
        Registry().create()
        Registry().register('service_list', MagicMock())

        # WHEN: when the URL is not correct and dispatch called
        rqst = MagicMock()
        rqst.path = '/api'
        rqst.method = 'GET'
        with self.assertRaises(NotFound) as context:
            application.dispatch(rqst)

        # THEN: the not found returned
        self.assertEqual(context.exception.args[0], 'Not Found', 'URL not found in dispatcher')

        # WHEN: when the URL is correct and dispatch called
        rqst = MagicMock()
        rqst.path = '/main'
        rqst.method = 'GET'
        application.dispatch(rqst)

        # THEN: the not found id called
        self.assertEqual(1, application.route_map['^\\/main$']['GET'].call_count,
                         'main_index function should have been called')
