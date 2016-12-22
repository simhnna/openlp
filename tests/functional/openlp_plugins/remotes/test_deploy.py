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

import os
import shutil

from tempfile import mkdtemp
from unittest import TestCase

from openlp.plugins.remotes.deploy import check_for_previous_deployment, deploy_zipfile

from tests.functional import patch


TEST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'resources'))


class TestRemoteDeploy(TestCase):
    """
    Test the Remote plugin deploy functions
    """

    def setUp(self):
        """
        Setup for tests
        """
        self.app_root = mkdtemp()

    def tearDown(self):
        """
        Clean up after tests
        """
        shutil.rmtree(self.app_root)

    @patch('openlp.plugins.remotes.deploy.os.path.isfile')
    @patch('openlp.plugins.remotes.deploy.os.mknod')
    def test_check_for_previous_deployment_false(self, mocked_mknod, mocked_isfile):
        """
        Remote Deploy tests - Test when the marker file is missing
        """
        # GIVEN: A new setup with no marker file
        # WHEN: I check for a deployment which does not create the marker file
        mocked_isfile.return_value = False
        processed = check_for_previous_deployment(self.app_root)

        # THEN test the see if marker has not been created
        self.assertFalse(processed, "should return False as marker does not exist")
        mocked_isfile.assert_called_once_with(os.path.join(self.app_root, "marker.txt"))
        mocked_mknod.assert_not_called()

    @patch('openlp.plugins.remotes.deploy.os.path.isfile')
    @patch('openlp.plugins.remotes.deploy.os.mknod')
    def test_check_for_previous_deployment_true(self, mocked_mknod, mocked_isfile):
        """
        Remote Deploy tests - Test when the marker file is missing
        """
        # GIVEN: A new setup with not market file
        # WHEN: I check for a deployment which does create the marker file
        mocked_isfile.return_value = False
        processed = check_for_previous_deployment(self.app_root, True)

        # THEN test the see if marker has been created
        marker_file = os.path.join(self.app_root, "marker.txt")
        self.assertFalse(processed, "should return False as marker does not exist")
        mocked_isfile.assert_called_once_with(marker_file)
        mocked_mknod.assert_called_once_with(marker_file)

    @patch('openlp.plugins.remotes.deploy.os.path.isfile')
    @patch('openlp.plugins.remotes.deploy.os.mknod')
    def test_check_for_previous_deployment_true(self, mocked_mknod, mocked_isfile):
        """
        Remote Deploy tests - Test when the marker file is present
        """
        # GIVEN: A new setup with not market file
        # WHEN: I check for a deployment which does not create the marker file
        mocked_isfile.return_value = True
        processed = check_for_previous_deployment(self.app_root, True)

        # THEN test the see if marker is present and has not been created
        marker_file = os.path.join(self.app_root, "marker.txt")
        self.assertTrue(processed, "should return True as marker does exist")
        mocked_isfile.assert_called_once_with(marker_file)
        mocked_mknod.assert_not_called()

    @patch('openlp.plugins.remotes.deploy.open')
    def test_deploy_zipfile(self, mocked_open):
        # GIVEN: A new downloaded zip file
        zip_file = os.path.join(TEST_PATH, "remotes", "deploy.zip")
        # WHEN: I process the zipfile
        deploy_zipfile(zip_file, self.app_root)

        # THEN test the see if marker is present and has not been created
        self.assertEqual(mocked_open.call_count, 46, "We should write 46 files")
