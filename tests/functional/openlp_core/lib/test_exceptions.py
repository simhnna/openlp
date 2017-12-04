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
Package to test the openlp.core.lib.exceptions package.
"""
from unittest import TestCase

from openlp.core.lib.exceptions import ValidationError


class TestValidationError(TestCase):
    """
    Test the ValidationError Class
    """
    def test_validation_error(self):
        """
        Test the creation of a ValidationError
        """
        # GIVEN: The ValidationError class

        # WHEN: Creating an instance of ValidationError
        error = ValidationError('Test ValidationError')

        # THEN: Then calling str on the error should return the correct text and it should be an instance of `Exception`
        assert str(error) == 'Test ValidationError'
        assert isinstance(error, Exception)
