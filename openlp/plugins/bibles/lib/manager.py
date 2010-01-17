# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2010 Raoul Snyman                                        #
# Portions copyright (c) 2008-2010 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Maikel Stuivenberg, Martin Thompson, Jon Tibble,   #
# Carsten Tinggaard                                                           #
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
import os

from common import parse_reference
from opensong import OpenSongBible
from osis import OSISBible
from csv import CSVBible
from db import BibleDB
from http import HTTPBible

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
    def get_class(id):
        """
        Return the appropriate imeplementation class.
        """
        if id == BibleFormat.OSIS:
            return OSISBible
        elif id == BibleFormat.CSV:
            return CSVBible
        elif id == BibleFormat.OpenSong:
            return OpenSongBible
        elif id == BibleFormat.WebDownload:
            return HTTPBible
        else:
            return None

    @staticmethod
    def list():
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
    global log
    log = logging.getLogger(u'BibleManager')
    log.info(u'Bible manager loaded')

    def __init__(self, config):
        """
        Finds all the bibles defined for the system and creates an interface
        object for each bible containing connection information. Throws
        Exception if no Bibles are found.

        Init confirms the bible exists and stores the database path.

        ``config``
            The plugin's configuration object.
        """
        self.config = config
        log.debug(u'Bible Initialising')
        self.web = u'Web'
        # dict of bible database objects
        self.db_cache = None
        # dict of bible http readers
        self.http_cache = None
        self.path = self.config.get_data_path()
        #get proxy name for screen
        self.proxy_name = self.config.get_config(u'proxy name')
        self.suffix = u'sqlite'
        self.import_wizard = None
        self.reload_bibles()
        self.media = None

    def reload_bibles(self):
        log.debug(u'Reload bibles')
        files = self.config.get_files(self.suffix)
        log.debug(u'Bible Files %s', files)
        self.db_cache = {}
        self.http_cache = {}
        # books of the bible with testaments
        self.book_testaments = {}
        # books of the bible with chapter count
        self.book_chapters = []
        # books of the bible with abbreviation
        self.book_abbreviations = {}
        self.web_bibles_present = False
        for filename in files:
            name, extension = os.path.splitext(filename)
            self.db_cache[name] = BibleDB(path=self.path, name=name, config=self.config)
            # look to see if lazy load bible exists and get create getter.
            source = self.db_cache[name].get_meta(u'web')
            if source:
                self.web_bibles_present = True
                web_bible = HTTPBible()
                # tell The Server where to get the verses from.
                web_bible.set_source(source.value)
                self.http_cache[name] = web_bible
                # look to see if lazy load bible exists and get create getter.
                meta_proxy = self.db_cache[name].get_meta(u'proxy url')
                proxy_url = None
                if meta_proxy:
                    proxy_url = meta_proxy.value
                    # tell The Server where to get the verses from.
                web_bible.set_proxy_url(proxy_url)
                # look to see if lazy load bible exists and get create getter.
                bible_id = self.db_cache[name].get_meta(u'bible id').value
                # tell The Server where to get the verses from.
                web_bible.set_bible_id(bible_id)
            #else:
            #    # makes the Full / partial code easier.
            #    self.http_cache[name] = None
            if self.web_bibles_present:
                filepath = os.path.split(os.path.abspath(__file__))[0]
                filepath = os.path.abspath(os.path.join(
                    filepath, u'..', u'resources', u'httpbooks.csv'))
                fbibles = None
                try:
                    fbibles = open(filepath, u'r')
                    for line in fbibles:
                        parts = line.split(u',')
                        self.book_abbreviations[parts[0]] = parts[1].replace(u'\n', '')
                        self.book_testaments[parts[0]] = parts[2].replace(u'\n', '')
                        self.book_chapters.append({
                            u'book': parts[0],
                            u'total': parts[3].replace(u'\n', '')
                        })
                except:
                    log.exception(u'Failed to load bible')
                finally:
                    if fbibles:
                        fbibles.close()
        log.debug(u'Bible Initialised')

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
            What type of Bible, one of the BibleFormat values.

        ``**kwargs``
            Keyword arguments to send to the actualy importer class.
        """
        class_ = BibleFormat.get_class(type)
        kwargs['path'] = self.path
        kwargs['config'] = self.config
        importer = class_(**kwargs)
        name = importer.register(self.import_wizard)
        self.db_cache[name] = importer
        return importer.do_import()

    def register_http_bible(self, biblename, biblesource, bibleid,
                            proxyurl=None, proxyid=None, proxypass=None):
        """
        Return a list of bibles from a given URL. The selected Bible
        can then be registered and LazyLoaded into a database.

        ``biblename``
            The name of the bible to register.

        ``biblesource``
            Where this Bible stores it's verses.

        ``bibleid``
            The identifier for a Bible.

        ``proxyurl``
            Defaults to *None*. An optional URL to a proxy server.

        ``proxyid``
            Defaults to *None*. A username for logging into the proxy
            server.

        ``proxypass``
            Defaults to *None*. The password to accompany the username.
        """
        log.debug(u'register_HTTP_bible %s, %s, %s, %s, %s, %s',
            biblename, biblesource, bibleid, proxyurl, proxyid, proxypass)
        if self._is_new_bible(biblename):
            # Create new Bible
            nbible = BibleDBImpl(self.bible_path, biblename, self.config)
            # Create Database
            nbible.create_tables()
            self.db_cache[biblename] = nbible
            nhttp = BibleHTTPImpl()
            nhttp.set_bible_source(biblesource)
            self.bible_http_cache[biblename] = nhttp
            # register a lazy loading interest
            nbible.create_meta(u'WEB', biblesource)
            # store the web id of the bible
            nbible.create_meta(u'bibleid', bibleid)
            if proxyurl:
                # store the proxy URL
                nbible.save_meta(u'proxy', proxyurl)
                nhttp.set_proxy(proxyurl)
            if proxyid:
                # store the proxy userid
                nbible.save_meta(u'proxyid', proxyid)
            if proxypass:
                # store the proxy password
                nbible.save_meta(u'proxypass', proxypass)
            return True
        else:
            log.debug(u'register_http_file_bible %s not created already exists',
                biblename)
            return False

    def register_csv_file_bible(self, biblename, booksfile, versefile):
        """
        Method to load a bible from a set of files into a database.
        If the database exists it is deleted and the database is reloaded
        from scratch.
        """
        log.debug(u'register_CSV_file_bible %s,%s,%s',
            biblename, booksfile, versefile)
        if self._is_new_bible(biblename):
            # Create new Bible
            nbible = BibleDBImpl(self.bible_path, biblename, self.config)
            # Create database
            nbible.create_tables()
            # Cache the database for use later
            self.bible_db_cache[biblename] = nbible
            # Create the loader and pass in the database
            bcsv = BibleCSVImpl(nbible)
            return bcsv.load_data(booksfile, versefile, self.dialogobject)
        else:
            log.debug(u'register_csv_file_bible %s not created already exists',
                biblename)
            return False

    def register_osis_file_bible(self, biblename, osisfile):
        """
        Method to load a bible from a osis xml file extracted from Sword bible
        viewer.  If the database exists it is deleted and the database is
        reloaded from scratch.
        """
        log.debug(u'register_OSIS_file_bible %s, %s', biblename, osisfile)
        if self._is_new_bible(biblename):
            # Create new Bible
            nbible = BibleDBImpl(self.bible_path, biblename, self.config)
            # Create Database
            nbible.create_tables()
            # Cache the database for use later
            self.bible_db_cache[biblename] = nbible
            # Create the loader and pass in the database
            bosis = BibleOSISImpl(self.bible_path, nbible)
            return bosis.load_data(osisfile, self.dialogobject)
        else:
            log.debug(
                u'register_OSIS_file_bible %s, %s not created already exists',
                biblename, osisfile)
            return False

    def register_opensong_bible(self, biblename, opensongfile):
        """
        Method to load a bible from an OpenSong xml file. If the database
        exists it is deleted and the database is reloaded from scratch.
        """
        log.debug(u'register_opensong_file_bible %s, %s', biblename, opensongfile)
        if self._is_new_bible(biblename):
            # Create new Bible
            nbible = BibleDBImpl(self.bible_path, biblename, self.config)
            # Create Database
            nbible.create_tables()
            # Cache the database for use later
            self.bible_db_cache[biblename] = nbible
            # Create the loader and pass in the database
            bcsv = BibleOpenSongImpl(self.bible_path, nbible)
            bcsv.load_data(opensongfile, self.dialogobject)
            return True
        else:
            log.debug(u'register_opensong_file_bible %s, %s not created '
                u'already exists', biblename, opensongfile)
            return False

    def get_bibles(self, mode=BibleMode.Full):
        """
        Returns a list of Books of the bible. When ``mode`` is set to
        ``BibleMode.Full`` this method returns all the Bibles for the Advanced
        Search, and when the mode is ``BibleMode.Partial`` this method returns
        all the bibles for the Quick Search.
        """
        log.debug(u'get_bibles')
        bible_list = []
        for bible_name, bible_object in self.db_cache.iteritems():
            if bible_name in self.http_cache and self.http_cache[bible_name]:
                bible_name = u'%s (%s)' % (bible_name, self.web)
            bible_list.append(bible_name)
        return bible_list

    def is_bible_web(self, bible):
        pos_end = bible.find(u' (%s)' % self.web)
        if pos_end != -1:
            return True, bible[:pos_end]
        return False, bible

    def get_bible_books(self):
        """
        Returns a list of the books of the bible
        """
        log.debug(u'get_bible_books')
        return self.book_chapters

    def get_book_chapter_count(self, book):
        """
        Returns the number of Chapters for a given book
        """
        log.debug(u'get_book_chapter_count %s', book)
        return self.book_chapters[book]

    def get_book_verse_count(self, bible, book, chapter):
        """
        Returns all the number of verses for a given
        book and chapterMaxBibleBookVerses
        """
        log.debug(u'get_book_verse_count %s,%s,%s', bible, book, chapter)
        web, bible = self.is_bible_web(bible)
        if web:
            count = self.db_cache[bible].get_max_bible_book_verses(
                    book, chapter)
            if count == 0:
                # Make sure the first chapter has been downloaded
                self.get_verse_text(bible, book, chapter, chapter, 1, 1)
                count = self.db_cache[bible].get_max_bible_book_verses(
                    book, chapter)
            return count
        else:
            return self.db_cache[bible].get_max_bible_book_verses(
                book, chapter)

    def get_verses(self, bible, versetext):
        """
        Returns all the number of verses for a given
        book and chapterMaxBibleBookVerses
        """
        log.debug(u'get_verses_from_text %s,%s', bible, versetext)
        reflist = parse_reference(versetext)
        web, bible = self.is_bible_web(bible)
        return self.db_cache[bible].get_verses(reflist)

    def save_meta_data(self, bible, version, copyright, permissions):
        """
        Saves the bibles meta data
        """
        log.debug(u'save_meta data %s,%s, %s,%s',
            bible, version, copyright, permissions)
        self.db_cache[bible].create_meta(u'Version', version)
        self.db_cache[bible].create_meta(u'Copyright', copyright)
        self.db_cache[bible].create_meta(u'Permissions', permissions)

    def get_meta_data(self, bible, key):
        """
        Returns the meta data for a given key
        """
        log.debug(u'get_meta %s,%s', bible, key)
        web, bible = self.is_bible_web(bible)
        return self.db_cache[bible].get_meta(key)

    def get_verse_text(self, bible, bookname, schapter, echapter, sverse,
        everse=0):
        """
        Returns a list of verses for a given Book, Chapter and ranges of verses.
        If the end verse(everse) is less then the start verse(sverse)
        then only one verse is returned

        ``bible``
            The name of the bible to be used

        Rest can be guessed at !
        """
        text = []
        self.media.setQuickMessage(u'')
        log.debug(u'get_verse_text %s,%s,%s,%s,%s,%s',
            bible, bookname, schapter, echapter, sverse, everse)
        # check to see if book/chapter exists fow HTTP bibles and load cache
        # if necessary
        web, bible = self.is_bible_web(bible)
        if self.http_cache[bible]:
            book = self.db_cache[bible].get_bible_book(bookname)
            if book is None:
                log.debug(u'get_verse_text : new book')
                for chapter in range(schapter, echapter + 1):
                    self.media.setQuickMessage(
                        unicode(self.media.trUtf8('Downloading %s: %s')) %
                            (bookname, chapter))
                    search_results = \
                        self.http_cache[bible].get_bible_chapter(
                            bible, bookname, chapter)
                    if search_results.has_verselist() :
                        ## We have found a book of the bible lets check to see
                        ## if it was there.  By reusing the returned book name
                        ## we get a correct book.  For example it is possible
                        ## to request ac and get Acts back.
                        bookname = search_results.get_book()
                        # check to see if book/chapter exists
                        book = self.db_cache[bible].get_bible_book(
                            bookname)
                        if book is None:
                            ## Then create book, chapter and text
                            book = self.db_cache[bible].create_book(
                                bookname, self.book_abbreviations[bookname],
                                self.book_testaments[bookname])
                            log.debug(u'New http book %s, %s, %s',
                                book, book.id, book.name)
                            self.db_cache[bible].create_chapter(
                                book.id, search_results.get_chapter(),
                                search_results.get_verselist())
                        else:
                            ## Book exists check chapter and texts only.
                            v = self.db_cache[bible].get_bible_chapter(
                                book.id, chapter)
                            if v is None:
                                self.media.setQuickMessage(
                                    unicode(self.media.trUtf8('%Downloading %s: %s'))\
                                        % (bookname, chapter))
                                self.db_cache[bible].create_chapter(
                                    book.id, chapter,
                                    search_results.get_verselist())
            else:
                log.debug(u'get_verse_text : old book')
                for chapter in range(schapter, echapter + 1):
                    v = self.db_cache[bible].get_bible_chapter(
                        book.id, chapter)
                    if v is None:
                        try:
                            self.media.setQuickMessage(\
                                 unicode(self.media.trUtf8('Downloading %s: %s'))
                                         % (bookname, chapter))
                            search_results = \
                                self.http_cache[bible].get_bible_chapter(
                                    bible, bookname, chapter)
                            if search_results.has_verselist():
                                self.db_cache[bible].create_chapter(
                                    book.id, search_results.get_chapter(),
                                    search_results.get_verselist())
                        except:
                            log.exception(u'Problem getting scripture online')
        #Now get verses from database
        if schapter == echapter:
            text = self.db_cache[bible].get_bible_text(bookname,
                schapter, sverse, everse)
        else:
            for i in range (schapter, echapter + 1):
                if i == schapter:
                    start = sverse
                    end = self.get_book_verse_count(bible, bookname, i)
                elif i == echapter:
                    start = 1
                    end = everse
                else:
                    start = 1
                    end = self.get_book_verse_count(bible, bookname, i)

                txt = self.db_cache[bible].get_bible_text(
                    bookname, i, start, end)
                text.extend(txt)
        return text

    def exists(self, name):
        """
        Check cache to see if new bible
        """
        for bible, db_object in self.db_cache.iteritems():
            log.debug(u'Bible from cache in is_new_bible %s', bible)
            if bible == name:
                return True
        return False

