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
This module contains tests for the OpenOffice/LibreOffice importer.
"""
from unittest import TestCase, skipIf
from unittest.mock import MagicMock, patch

from openlp.core.common.registry import Registry
from tests.helpers.testmixin import TestMixin

try:
    from openlp.plugins.songs.lib.importers.openoffice import OpenOfficeImport
except ImportError:
    OpenOfficeImport = None


@skipIf(OpenOfficeImport is None, 'Could not import OpenOfficeImport probably due to unavailability of uno')
class TestOpenOfficeImport(TestCase, TestMixin):
    """
    Test the :class:`~openlp.plugins.songs.lib.importer.openoffice.OpenOfficeImport` class
    """

    def setUp(self):
        """
        Create the registry
        """
        Registry.create()

    @patch('openlp.plugins.songs.lib.importers.openoffice.SongImport')
    def test_create_importer(self, mocked_songimport):
        """
        Test creating an instance of the OpenOfficeImport file importer
        """
        # GIVEN: A mocked out SongImport class, and a mocked out "manager"
        mocked_manager = MagicMock()

        # WHEN: An importer object is created
        importer = OpenOfficeImport(mocked_manager, file_paths=[])

        # THEN: The importer object should not be None
        assert importer is not None, 'Import should not be none'

    @patch('openlp.plugins.songs.lib.importers.openoffice.SongImport')
    def test_close_ooo_file(self, mocked_songimport):
        """
        Test that close_ooo_file catches raised exceptions
        """
        # GIVEN: A mocked out SongImport class, a mocked out "manager" and a document that raises an exception
        mocked_manager = MagicMock()
        importer = OpenOfficeImport(mocked_manager, file_paths=[])
        importer.document = MagicMock()
        importer.document.close = MagicMock(side_effect=Exception())

        # WHEN: Calling close_ooo_file
        importer.close_ooo_file()

        # THEN: The document attribute should be None even if an exception is raised')
        assert importer.document is None, 'Document should be None even if an exception is raised'
