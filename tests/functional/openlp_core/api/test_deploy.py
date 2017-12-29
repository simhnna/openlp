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
from tempfile import mkdtemp
from unittest import TestCase

from openlp.core.api.deploy import deploy_zipfile
from openlp.core.common.path import Path, copyfile

TEST_PATH = (Path(__file__).parent / '..' / '..' / '..' / 'resources').resolve()


class TestRemoteDeploy(TestCase):
    """
    Test the Remote plugin deploy functions
    """

    def setUp(self):
        """
        Setup for tests
        """
        self.app_root_path = Path(mkdtemp())

    def tearDown(self):
        """
        Clean up after tests
        """
        self.app_root_path.rmtree()

    def test_deploy_zipfile(self):
        """
        Remote Deploy tests - test the dummy zip file is processed correctly
        """
        # GIVEN: A new downloaded zip file
        zip_path = TEST_PATH / 'remotes' / 'site.zip'
        app_root_path = self.app_root_path / 'site.zip'
        copyfile(zip_path, app_root_path)

        # WHEN: I process the zipfile
        deploy_zipfile(self.app_root_path, 'site.zip')

        # THEN: test if www directory has been created
        assert (self.app_root_path / 'www').is_dir(), 'We should have a www directory'
