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

from openlp.core.common.httputils import url_get_file, get_web_page

from tests.functional import MagicMock


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

    def test_download_and_check_size(self):
        """
        Remote Deploy tests - Test hosted sites file matches the config file
        """
        # GIVEN: a hosted configuration file
        user_agent = 'OpenLP/2.4.4'
        web = 'https://get.openlp.org/webclient/'
        web_config = get_web_page('{host}{name}'.format(host=web, name='download.cfg'),
                                  header=('User-Agent', user_agent))
        sha = web_config.read().decode('utf-8').split()[0]
        callback = MagicMock()
        callback.was_cancelled = False
        f = os.path.join(self.app_root, 'sites.zip')
        # WHEN: I download the sites file
        # THEN: the file will download and match the sha256 from the config file
        url_get_file(callback, web + 'site.zip', f, sha256=sha)


