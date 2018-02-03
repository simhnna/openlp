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
Functional tests to test the remote index
"""
from unittest.mock import MagicMock, patch

from openlp.core.api.endpoint.remote import index
from openlp.core.api.endpoint.core import TRANSLATED_STRINGS


@patch('openlp.core.api.endpoint.remote.remote_endpoint')
def test_index(mocked_endpoint):
    """
    Test the index method of the remote
    """
    # GIVEN: A mocked Endpoint
    mocked_endpoint.render_template.return_value = 'test template'

    # WHEN: index is called
    result = index(MagicMock(), 'index')

    # THEN: The result should be "test template" and the right methods should have been called
    mocked_endpoint.render_template.assert_called_once_with('index.mako', **TRANSLATED_STRINGS)
    assert result == 'test template'
