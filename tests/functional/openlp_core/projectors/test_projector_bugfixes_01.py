# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2015 OpenLP Developers                                   #
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
Package to test the openlp.core.projectors.pjlink base package.
"""
from unittest import TestCase

from openlp.core.projectors.db import Projector
from openlp.core.projectors.pjlink import PJLink

from tests.resources.projector.data import TEST1_DATA


class TestPJLinkBugs(TestCase):
    """
    Tests for the PJLink module bugfixes
    """
    def setUp(self):
        '''
        Initialization
        '''
        self.pjlink_test = PJLink(Projector(**TEST1_DATA), no_poll=True)

    def tearDown(self):
        '''
        Cleanups
        '''
        self.pjlink_test = None

    def test_bug_1550891_process_clss_nonstandard_reply_1(self):
        """
        Bugfix 1550891: CLSS request returns non-standard reply with Optoma/Viewsonic projector
        """
        # GIVEN: Test object
        pjlink = self.pjlink_test

        # WHEN: Process non-standard reply
        pjlink.process_clss('Class 1')

        # THEN: Projector class should be set with proper value
        self.assertEqual(pjlink.pjlink_class, '1',
                         'Non-standard class reply should have set class=1')

    def test_bug_1550891_process_clss_nonstandard_reply_2(self):
        """
        Bugfix 1550891: CLSS request returns non-standard reply with BenQ projector
        """
        # GIVEN: Test object
        pjlink = self.pjlink_test

        # WHEN: Process non-standard reply
        pjlink.process_clss('Version2')

        # THEN: Projector class should be set with proper value
        # NOTE: At this time BenQ is Class 1, but we're trying a different value to verify
        self.assertEqual(pjlink.pjlink_class, '2',
                         'Non-standard class reply should have set class=2')

    def test_bug_1593882_no_pin_authenticated_connection(self):
        """
        Test bug 1593882 no pin and authenticated request exception
        """
        # Test now part of test_projector_pjlink_commands_02
        # Keeping here for bug reference
        pass

    def test_bug_1593883_pjlink_authentication(self):
        """
        Test bugfix 1593883 pjlink authentication and ticket 92187
        """
        # Test now part of test_projector_pjlink_commands_02
        # Keeping here for bug reference
        pass

    def test_bug_1734275_process_lamp_nonstandard_reply(self):
        """
        Test bugfix 17342785 non-standard LAMP response
        """
        # GIVEN: Test object
        pjlink = self.pjlink_test

        # WHEN: Process lamp command called with only hours and no lamp power state
        pjlink.process_lamp("45")

        # THEN: Lamp should show hours as 45 and lamp power as Unavailable
        self.assertEqual(len(pjlink.lamp), 1, 'There should only be 1 lamp available')
        self.assertEqual(pjlink.lamp[0]['Hours'], 45, 'Lamp hours should have equalled 45')
        self.assertIsNone(pjlink.lamp[0]['On'], 'Lamp power should be "None"')
