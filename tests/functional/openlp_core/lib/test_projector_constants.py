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
Package to test the openlp.core.lib.projector.constants package.
"""
from unittest import TestCase


class TestProjectorConstants(TestCase):
    """
    Test specific functions in the projector constants module.
    """
    def test_build_pjlink_video_label(self):
        """
        Test building PJLINK_DEFAULT_CODES dictionary
        """
        # GIVEN: Test data
        from tests.resources.projector.data import TEST_VIDEO_CODES

        # WHEN: Import projector PJLINK_DEFAULT_CODES
        from openlp.core.lib.projector.constants import PJLINK_DEFAULT_CODES

        # THEN: Verify dictionary was build correctly
        self.assertEqual(PJLINK_DEFAULT_CODES, TEST_VIDEO_CODES, 'PJLink video strings should match')
