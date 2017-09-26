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
Package to test the openlp.core.utils.__init__ package.
"""
from unittest import TestCase
from unittest.mock import patch

from openlp.core.common.httputils import CONNECTION_RETRIES, get_web_page

from tests.helpers.testmixin import TestMixin


class TestFirstTimeWizard(TestMixin, TestCase):
    """
    Test First Time Wizard import functions
    """
    @patch('openlp.core.common.httputils.requests')
    def test_webpage_connection_retry(self, mocked_requests):
        """
        Test get_web_page will attempt CONNECTION_RETRIES+1 connections - bug 1409031
        """
        # GIVEN: Initial settings and mocks
        mocked_requests.get.side_effect = IOError('Unable to connect')

        # WHEN: A webpage is requested
        try:
            get_web_page('http://localhost')
        except Exception as e:
            assert isinstance(e, ConnectionError)

        # THEN: urlopen should have been called CONNECTION_RETRIES + 1 count
        assert mocked_requests.get.call_count == CONNECTION_RETRIES, \
            'get should have been called {} times, but was only called {} times'.format(
                CONNECTION_RETRIES, mocked_requests.get.call_count)
