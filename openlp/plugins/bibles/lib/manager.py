# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2010 Raoul Snyman                                        #
# Portions copyright (c) 2008-2010 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Meinert Jordan, Andreas Preikschat, Christian      #
# Richter, Philip Ridout, Maikel Stuivenberg, Martin Thompson, Jon Tibble,    #
# Carsten Tinggaard, Frode Woldsund                                           #
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

from PyQt4 import QtCore, QtGui

from openlp.core.lib import SettingsManager, translate
from openlp.core.utils import AppLocation
from openlp.plugins.bibles.lib import parse_reference
from openlp.plugins.bibles.lib.db import BibleDB, BibleMeta

from opensong import OpenSongBible
from osis import OSISBible
from csvbible import CSVBible
from http import HTTPBible

log = logging.getLogger(__name__)

class BibleMode(object):
    """
    This is basically an enumeration class which specifies the mode of a Bible.
    Mode refers to whether or not a Bible in OpenLP is a full Bible or needs to
    be downloaded from the Internet on an as-needed basis.
    """
    Full = 1
    Partial = 2


class BibleFormat(object):
    """
    This is a special enumeration class that holds the various types of Bibles,
    plus a few helper functions to facilitate generic handling of Bible types
    for importing.
    """
    Unknown = -1
    OSIS = 0
    CSV = 1
    OpenSong = 2
    WebDownload = 3

    @staticmethod
    def get_class(format):
        """
        Return the appropriate imeplementation class.

        ``format``
            The Bible format.
        """
        if format == BibleFormat.OSIS:
            return OSISBible
        elif format == BibleFormat.CSV:
            return CSVBible
        elif format == BibleFormat.OpenSong:
            return OpenSongBible
        elif format == BibleFormat.WebDownload:
            return HTTPBible
        else:
            return None

    @staticmethod
    def list():
        """
        Return a list of the supported Bible formats.
        """
        return [
            BibleFormat.OSIS,
            BibleFormat.CSV,
            BibleFormat.OpenSong,
            BibleFormat.WebDownload
        ]


class BibleManager(object):
    """
    The Bible manager which holds and manages all the Bibles.
    """
    log.info(u'Bible manager loaded')

    def __init__(self, parent):
        """
        Finds all the bibles defined for the system and creates an interface
        object for each bible containing connection information. Throws
        Exception if no Bibles are found.

        Init confirms the bible exists and stores the database path.
        """
        log.debug(u'Bible Initialising')
        self.parent = parent
        self.settingsSection = u'bibles'
        self.web = u'Web'
        self.db_cache = None
        self.path = AppLocation.get_section_data_path(self.settingsSection)
        self.proxy_name = unicode(
            QtCore.QSettings().value(self.settingsSection + u'/proxy name',
            QtCore.QVariant(u'')).toString())
        self.suffix = u'.sqlite'
        self.import_wizard = None
        self.reload_bibles()
        self.media = None

    def reload_bibles(self):
        """
        Reloads the Bibles from the available Bible databases on disk. If a web
        Bible is encountered, an instance of HTTPBible is loaded instead of the
        BibleDB class.
        """
        log.debug(u'Reload bibles')
        files = SettingsManager.get_files(self.settingsSection, self.suffix)
        log.debug(u'Bible Files %s', files)
        self.db_cache = {}
        for filename in files:
            bible = BibleDB(self.parent, path=self.path, file=filename)
            name = bible.get_name()
            log.debug(u'Bible Name: "%s"', name)
            self.db_cache[name] = bible
            # Look to see if lazy load bible exists and get create getter.
            source = self.db_cache[name].get_object(BibleMeta,
                u'download source')
            if source:
                download_name = self.db_cache[name].get_object(BibleMeta,
                    u'download name').value
                meta_proxy = self.db_cache[name].get_object(BibleMeta,
                    u'proxy url')
                web_bible = HTTPBible(self.parent, path=self.path,
                    file=filename, download_source=source.value,
                    download_name=download_name)
                if meta_proxy:
                    web_bible.proxy_server = meta_proxy.value
                self.db_cache[name] = web_bible
        log.debug(u'Bibles reloaded')

    def set_process_dialog(self, wizard):
        """
        Sets the reference to the dialog with the progress bar on it.

        ``dialog``
            The reference to the import wizard.
        """
        self.import_wizard = wizard

    def import_bible(self, type, **kwargs):
        """
        Register a bible in the bible cache, and then import the verses.

        ``type``
            What type of Bible, one of the ``BibleFormat`` values.

        ``**kwargs``
            Keyword arguments to send to the actual importer class.
        """
        class_ = BibleFormat.get_class(type)
        kwargs['path'] = self.path
        importer = class_(self.parent, **kwargs)
        name = importer.register(self.import_wizard)
        self.db_cache[name] = importer
        return importer

    def get_bibles(self):
        """
        Returns a dict with all available Bibles.
        """
        log.debug(u'get_bibles')
        return self.db_cache

    def get_books(self, bible):
        """
        Returns a list of Bible books, and the number of chapters in that book.

        ``bible``
            Unicode. The Bible to get the list of books from.
        """
        log.debug(u'BibleManager.get_books("%s")', bible)
        return [
            {
                u'name': book.name,
                u'chapters': self.db_cache[bible].get_chapter_count(book.name)
            }
            for book in self.db_cache[bible].get_books()
        ]

    def get_chapter_count(self, bible, book):
        """
        Returns the number of Chapters for a given book.
        """
        log.debug(u'get_book_chapter_count %s', book)
        return self.db_cache[bible].get_chapter_count(book)

    def get_verse_count(self, bible, book, chapter):
        """
        Returns all the number of verses for a given
        book and chapterMaxBibleBookVerses.
        """
        log.debug(u'BibleManager.get_verse_count("%s", "%s", %s)',
            bible, book, chapter)
        return self.db_cache[bible].get_verse_count(book, chapter)

    def get_verses(self, bible, versetext):
        """
        Parses a scripture reference, fetches the verses from the Bible
        specified, and returns a list of ``Verse`` objects.

        ``bible``
            Unicode. The Bible to use.

        ``versetext``
            Unicode. The scripture reference. Valid scripture references are:

                - Genesis 1
                - Genesis 1-2
                - Genesis 1:1
                - Genesis 1:1-10
                - Genesis 1:1-10,15-20
                - Genesis 1:1-2:10
                - Genesis 1:1-10,2:1-10
        """
        log.debug(u'BibleManager.get_verses("%s", "%s")', bible, versetext)
        reflist = parse_reference(versetext)
        if reflist:
            return self.db_cache[bible].get_verses(reflist)
        else:
            QtGui.QMessageBox.information(self.parent.mediaItem,
                translate('BiblesPlugin.BibleManager',
                'Scripture Reference Error'),
                translate('BiblesPlugin.BibleManager', 'Your scripture '
                'reference is either not supported by OpenLP or is invalid. '
                'Please make sure your reference conforms to one of the '
                'following patterns:\n\n'
                'Book Chapter\n'
                'Book Chapter-Chapter\n'
                'Book Chapter:Verse-Verse\n'
                'Book Chapter:Verse-Verse,Verse-Verse\n'
                'Book Chapter:Verse-Verse,Chapter:Verse-Verse\n'
                'Book Chapter:Verse-Chapter:Verse'))
            return None

    def verse_search(self, bible, text):
        """
        Does a verse search for the given bible and text.

        ``bible``
            The bible to seach in (unicode).

        ``text``
            The text to search for (unicode).
        """
        log.debug(u'BibleManager.verse_search("%s", "%s")', bible,  text)
        if text:
            return self.db_cache[bible].verse_search(text)
        else:
            QtGui.QMessageBox.information(self.parent.mediaItem,
                translate('BiblesPlugin.BibleManager',
                'Scripture Reference Error'),
                translate('BiblesPlugin.BibleManager', 'You did not enter a '
                'search keyword.\nYou can separate different keywords by a '
                'space to search for all of your keywords and you can seperate '
                'them by a comma to search for one of them.'))
            return None

    def save_meta_data(self, bible, version, copyright, permissions):
        """
        Saves the bibles meta data.
        """
        log.debug(u'save_meta data %s,%s, %s,%s',
            bible, version, copyright, permissions)
        self.db_cache[bible].create_meta(u'Version', version)
        self.db_cache[bible].create_meta(u'Copyright', copyright)
        self.db_cache[bible].create_meta(u'Permissions', permissions)

    def get_meta_data(self, bible, key):
        """
        Returns the meta data for a given key.
        """
        log.debug(u'get_meta %s,%s', bible, key)
        return self.db_cache[bible].get_object(BibleMeta, key)

    def exists(self, name):
        """
        Check cache to see if new bible.
        """
        if not isinstance(name, unicode):
            name = unicode(name)
        for bible in self.db_cache.keys():
            log.debug(u'Bible from cache in is_new_bible %s', bible)
            if not isinstance(bible, unicode):
                bible = unicode(bible)
            if bible == name:
                return True
        return False

    def finalise(self):
        """
        Loop through the databases to VACUUM them.
        """
        for bible in self.db_cache:
            self.db_cache[bible].finalise

