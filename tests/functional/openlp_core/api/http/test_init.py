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
Functional tests to test the Http init.
"""
from unittest import TestCase
from unittest.mock import MagicMock

from openlp.core.api.http import check_auth, requires_auth, authenticate
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings

from tests.helpers.testmixin import TestMixin


class TestInit(TestCase, TestMixin):
    """
    A test suite to test the functions on the init
    """

    def setUp(self):
        """
        Create the UI
        """
        Registry().create()
        Registry().register('service_list', MagicMock())
        self.build_settings()

    def tearDown(self):
        self.destroy_settings()

    def test_auth(self):
        """
        Test the check_auth method with a match
        :return:
        """
        # GIVEN: a known user
        Settings().setValue('api/user id', "superfly")
        Settings().setValue('api/password', "lamas")

        # WHEN : I check the authorisation
        is_valid = check_auth(['aaaaa', 'c3VwZXJmbHk6bGFtYXM='])

        # THEN:
        assert is_valid is True

    def test_auth_falure(self):
        """
        Test the check_auth method with a match
        :return:
        """
        # GIVEN: a known user
        Settings().setValue('api/user id', 'superfly')
        Settings().setValue('api/password', 'lamas')

        # WHEN : I check the authorisation
        is_valid = check_auth(['aaaaa', 'monkey123'])

        # THEN:
        assert is_valid is False

    def test_requires_auth_disabled(self):
        """
        Test the requires_auth wrapper with disabled security
        :return:
        """
        # GIVEN: A disabled security
        Settings().setValue('api/authentication enabled', False)

        # WHEN: I call the function
        wrapped_function = requires_auth(func)
        value = wrapped_function()

        # THEN: the result will be as expected
        assert value == 'called'

    def test_requires_auth_enabled(self):
        """
        Test the requires_auth wrapper with enabled security
        :return:
        """
        # GIVEN: A disabled security
        Settings().setValue('api/authentication enabled', True)

        # WHEN: I call the function
        wrapped_function = requires_auth(func)
        value = wrapped_function(['a'])

        # THEN: the result will be as expected
        assert str(value) == str(authenticate())


def func():
    return 'called'
