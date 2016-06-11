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

from openlp.core.api.errors import NotFound, ServerError


class TestApiError(TestCase):
    """
    A test suite to test out the Error in the API code
    """
    def test_not_found(self):
        """
        Test the Not Found error displays the correct information
        """
        with self.assertRaises(Exception) as context:
            raise NotFound()

        self.assertEquals('Not Found', context.exception.message, 'A Not Found exception should be thrown')
        self.assertEquals(404, context.exception.status, 'A 404 status should be thrown')

    def test_server_error(self):
        """
        Test the server error displays the correct information
        """
        with self.assertRaises(Exception) as context:
            raise ServerError()

        self.assertEquals('Server Error', context.exception.message, 'A Not Found exception should be thrown')
        self.assertEquals(500, context.exception.status, 'A 500 status should be thrown')