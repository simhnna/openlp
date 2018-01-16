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
Functional tests to test the API Error Class.
"""
from openlp.core.api.http.errors import HttpError, NotFound, ServerError


def test_http_error():
    """
    Test the HTTPError class
    """
    # GIVEN: An HTTPError class
    # WHEN: An instance is created
    error = HttpError(400, 'Access Denied')

    # THEN: The to_response() method should return the correct information
    assert error.to_response() == ('Access Denied', 400), 'to_response() should have returned the correct info'


def test_not_found():
    """
    Test the Not Found error displays the correct information
    """
    # GIVEN: A NotFound class
    # WHEN: An instance is created
    error = NotFound()

    # THEN: The to_response() method should return the correct information
    assert error.to_response() == ('Not Found', 404), 'to_response() should have returned the correct info'


def test_server_error():
    """
    Test the server error displays the correct information
    """
    # GIVEN: A ServerError class
    # WHEN: An instance of the class is created
    error = ServerError()

    # THEN: The to_response() method should return the correct information
    assert error.to_response() == ('Server Error', 500), 'to_response() should have returned the correct info'
