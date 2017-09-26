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

import os
import shutil
from tempfile import mkdtemp
from unittest import TestCase

from openlp.core.api.deploy import deploy_zipfile

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

    def test_deploy_zipfile(self):
        """
        Remote Deploy tests - test the dummy zip file is processed correctly
        """
        # GIVEN: A new downloaded zip file
        zip_file = os.path.join(TEST_PATH, 'remotes', 'site.zip')
        app_root = os.path.join(self.app_root, 'site.zip')
        shutil.copyfile(zip_file, app_root)
        # WHEN: I process the zipfile
        deploy_zipfile(self.app_root, 'site.zip')

        # THEN test if www directory has been created
        self.assertTrue(os.path.isdir(os.path.join(self.app_root, 'www')), 'We should have a www directory')
