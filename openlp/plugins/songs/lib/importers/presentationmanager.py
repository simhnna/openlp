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
The :mod:`presentationmanager` module provides the functionality for importing
Presentationmanager song files into the current database.
"""
import re

from lxml import objectify, etree

from openlp.core.common import get_file_encoding
from openlp.core.common.i18n import translate
from openlp.core.widgets.wizard import WizardStrings
from openlp.plugins.songs.lib.importers.songimport import SongImport


class PresentationManagerImport(SongImport):
    """
    The :class:`PresentationManagerImport` class provides OpenLP with the
    ability to import Presentationmanager song files.
    """
    def do_import(self):
        self.import_wizard.progress_bar.setMaximum(len(self.import_source))
        for file_path in self.import_source:
            if self.stop_import_flag:
                return
            self.import_wizard.increment_progress_bar(WizardStrings.ImportingType.format(source=file_path.name))
            try:
                tree = etree.parse(str(file_path), parser=etree.XMLParser(recover=True))
            except etree.XMLSyntaxError:
                # Try to detect encoding and use it
                encoding = get_file_encoding(file_path)['encoding']
                # Open file with detected encoding and remove encoding declaration
                text = file_path.read_text(encoding=encoding)
                text = re.sub(r'.+\?>\n', '', text)
                try:
                    tree = etree.fromstring(text, parser=etree.XMLParser(recover=True))
                except ValueError:
                    self.log_error(file_path,
                                   translate('SongsPlugin.PresentationManagerImport',
                                             'File is not in XML-format, which is the only format supported.'))
                    continue
            root = objectify.fromstring(etree.tostring(tree))
            self.process_song(root, file_path)

    def _get_attr(self, elem, name):
        """
        Due to PresentationManager's habit of sometimes capitilising the first letter of an element, we have to do
        some gymnastics.
        """
        if hasattr(elem, name):
            return str(getattr(elem, name))
        name = name[0].upper() + name[1:]
        if hasattr(elem, name):
            return str(getattr(elem, name))
        else:
            return ''

    def process_song(self, root, file_path):
        """
        :param root:
        :param openlp.core.common.path.Path file_path: Path to the file to process
        :rtype: None
        """
        self.set_defaults()
        attrs = None
        if hasattr(root, 'attributes'):
            attrs = root.attributes
        elif hasattr(root, 'Attributes'):
            attrs = root.Attributes
        if attrs is not None:
            self.title = self._get_attr(root.attributes, 'title')
            self.add_author(self._get_attr(root.attributes, 'author'))
            self.copyright = self._get_attr(root.attributes, 'copyright')
            self.ccli_number = self._get_attr(root.attributes, 'ccli_number')
            self.comments = str(root.attributes.comments) if hasattr(root.attributes, 'comments') else None
        verse_order_list = []
        verse_count = {}
        duplicates = []
        for verse in root.verses.verse:
            original_verse_def = verse.get('id')
            # Presentation Manager stores duplicate verses instead of a verse order.
            # We need to create the verse order from that.
            is_duplicate = False
            if original_verse_def in duplicates:
                is_duplicate = True
            else:
                duplicates.append(original_verse_def)
            if original_verse_def.startswith("Verse"):
                verse_def = 'v'
            elif original_verse_def.startswith("Chorus") or original_verse_def.startswith("Refrain"):
                verse_def = 'c'
            elif original_verse_def.startswith("Bridge"):
                verse_def = 'b'
            elif original_verse_def.startswith("End"):
                verse_def = 'e'
            else:
                verse_def = 'o'
            if not is_duplicate:  # Only increment verse number if no duplicate
                verse_count[verse_def] = verse_count.get(verse_def, 0) + 1
            verse_def = '{verse}{count:d}'.format(verse=verse_def, count=verse_count[verse_def])
            if not is_duplicate:  # Only add verse if no duplicate
                self.add_verse(str(verse).strip(), verse_def)
            verse_order_list.append(verse_def)

        self.verse_order_list = verse_order_list
        if not self.finish():
            self.log_error(file_path.name)
