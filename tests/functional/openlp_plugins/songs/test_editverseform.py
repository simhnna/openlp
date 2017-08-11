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
This module contains tests for the editverseform of the Songs plugin.
"""
from unittest import TestCase
from unittest.mock import MagicMock

from PyQt5 import QtCore

from openlp.core.common import Settings
from openlp.plugins.songs.forms.editverseform import EditVerseForm

from tests.helpers.testmixin import TestMixin

__default_settings__ = {
    'songs/enable chords': True,
}


class TestEditVerseForm(TestCase, TestMixin):
    """
    Test the functions in the :mod:`lib` module.
    """
    def setUp(self):
        """
        Set up the components need for all tests.
        """
        self.setup_application()
        self.build_settings()
        Settings().extend_default_settings(__default_settings__)
        self.edit_verse_form = EditVerseForm(None)
        QtCore.QLocale.setDefault(QtCore.QLocale('en_GB'))

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        self.destroy_settings()

    def test_update_suggested_verse_number(self):
        """
        Test that update_suggested_verse_number() has no effect when editing a single verse
        """
        # GIVEN some input values
        self.edit_verse_form.has_single_verse = True
        self.edit_verse_form.verse_type_combo_box.currentIndex = MagicMock(return_value=0)
        self.edit_verse_form.verse_text_edit.toPlainText = MagicMock(return_value='Text')
        self.edit_verse_form.verse_number_box.setValue(3)

        # WHEN the method is called
        self.edit_verse_form.update_suggested_verse_number()

        # THEN the verse number must not be changed
        self.assertEqual(3, self.edit_verse_form.verse_number_box.value(), 'The verse number should be 3')

    def test_on_divide_split_button_clicked(self):
        """
        Test that divide adds text at the correct position
        """
        # GIVEN some input values
        self.edit_verse_form.verse_type_combo_box.currentIndex = MagicMock(return_value=4)
        self.edit_verse_form.verse_text_edit.setPlainText('Text\n')

        # WHEN the method is called
        self.edit_verse_form.on_divide_split_button_clicked()
        # THEN the verse number must not be changed
        self.assertEqual('[--}{--]\nText\n', self.edit_verse_form.verse_text_edit.toPlainText(),
                         'The verse number should be [--}{--]\nText\n')

    def test_on_split_button_clicked(self):
        """
        Test that divide adds text at the correct position
        """
        # GIVEN some input values
        self.edit_verse_form.verse_type_combo_box.currentIndex = MagicMock(return_value=4)
        self.edit_verse_form.verse_text_edit.setPlainText('Text\n')

        # WHEN the method is called
        self.edit_verse_form.on_split_button_clicked()
        # THEN the verse number must not be changed
        self.assertEqual('[---]\nText\n', self.edit_verse_form.verse_text_edit.toPlainText(),
                         'The verse number should be [---]\nText\n')
