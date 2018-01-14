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

# from openlp.core.projectors.db import Projector
# from openlp.core.projectors.pjlink import PJLink
# from tests.resources.projector.data import TEST1_DATA


class TestPJLinkBugs(TestCase):
    """
    Tests for the PJLink module bugfixes
    """
    def bug_1550891_process_clss_nonstandard_reply_1(self):
        """
        Bugfix 1550891: CLSS request returns non-standard reply with Optoma/Viewsonic projector
        """
        # Test now part of test_projector_pjlink_commands_01
        # Keeping here for bug reference
        pass

    def bug_1550891_process_clss_nonstandard_reply_2(self):
        """
        Bugfix 1550891: CLSS request returns non-standard reply with BenQ projector
        """
        # Test now part of test_projector_pjlink_commands_01
        # Keeping here for bug reference
        pass

    def bug_1593882_no_pin_authenticated_connection(self):
        """
        Test bug 1593882 no pin and authenticated request exception
        """
        # Test now part of test_projector_pjlink_commands_02
        # Keeping here for bug reference
        pass

    def bug_1593883_pjlink_authentication(self):
        """
        Test bugfix 1593883 pjlink authentication and ticket 92187
        """
        # Test now part of test_projector_pjlink_commands_02
        # Keeping here for bug reference
        pass

    def bug_1734275_process_lamp_nonstandard_reply(self):
        """
        Test bugfix 17342785 non-standard LAMP response with one lamp hours only
        """
        # Test now part of test_projector_pjlink_commands_01
        # Keeping here for bug reference
        pass
