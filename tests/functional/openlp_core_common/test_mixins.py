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
Package to test the openlp.core.common package.
"""
from unittest import TestCase

from openlp.core.common.mixins import RegistryMixin
from openlp.core.common.registry import Registry


class PlainStub(object):
    def __init__(self):
        pass


class MixinStub(RegistryMixin):
    def __init__(self):
        super().__init__(None)


class TestRegistryMixin(TestCase):

    def test_registry_mixin_missing(self):
        """
        Test the registry creation and its usage
        """
        # GIVEN: A new registry
        Registry.create()

        # WHEN: I create an instance of a class that doesn't inherit from RegistryMixin
        PlainStub()

        # THEN: Nothing is registered with the registry
        self.assertEqual(len(Registry().functions_list), 0), 'The function should not be in the dict anymore.'

    def test_registry_mixin_present(self):
        """
        Test the registry creation and its usage
        """
        # GIVEN: A new registry
        Registry.create()

        # WHEN: I create an instance of a class that inherits from RegistryMixin
        MixinStub()

        # THEN: The bootstrap methods should be registered
        self.assertEqual(len(Registry().functions_list), 2), 'The bootstrap functions should be in the dict.'
