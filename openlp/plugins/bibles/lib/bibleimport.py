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

import logging

from lxml import etree, objectify

from openlp.core.common import languages
from openlp.plugins.bibles.lib.db import BibleDB

log = logging.getLogger(__name__)


class BibleImport(BibleDB):
    """
    Helper class to import bibles from a third party source into OpenLP
    """
    #TODO: Test
    def __init__(self, *args, **kwargs):
        log.debug(self.__class__.__name__)
        super().__init__(*args, **kwargs)
        self.filename = kwargs['filename'] if 'filename' in kwargs else None

    def get_language_id(self, file_language=None, bible_name=None):
        """
        Get the language_id for the language of the bible. Fallback to user input if we cannot do this pragmatically.

        :param file_language: Language of the bible. Possibly retrieved from the file being imported. Str
        :param bible_name: Name of the bible to display on the get_language dialog. Str
        :return: The id of a language Int or None
        """
        language_id = None
        if file_language:
            language = languages.get_language(file_language)
            if language and language.id:
                language_id = language.id
        if not language_id:
            # The language couldn't be detected, ask the user
            language_id = self.get_language(bible_name)
        if not language_id:
            # User cancelled get_language dialog
            log.error('Language detection failed when importing from "{name}". User aborted language selection.'
                      .format(name=bible_name))
            return None
        self.save_meta('language_id', language_id)
        return language_id

    @staticmethod
    def parse_xml(filename, use_objectify=False, elements=None, tags=None):
        """
        Parse and clean the supplied file by removing any elements or tags we don't use.
        :param filename: The filename of the xml file to parse. Str
        :param use_objectify: Use the objectify parser rather than the etree parser. (Bool)
        :param elements: A tuple of element names (Str) to remove along with their content.
        :param tags: A tuple of element names (Str) to remove, preserving their content.
        :return: The root element of the xml document
        """
        with open(filename, 'rb') as import_file:
            # NOTE: We don't need to do any of the normal encoding detection here, because lxml does it's own encoding
            # detection, and the two mechanisms together interfere with each other.
            if not use_objectify:
                tree = etree.parse(import_file, parser=etree.XMLParser(recover=True))
            else:
                tree = objectify.parse(import_file, parser=objectify.makeparser(recover=True))
            if elements:
                # Strip tags we don't use - remove content
                etree.strip_elements(tree, elements, with_tail=False)
            if tags:
                # Strip tags we don't use - keep content
                etree.strip_tags(tree, tags)
            return tree.getroot()
