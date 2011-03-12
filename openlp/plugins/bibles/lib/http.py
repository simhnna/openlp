# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2011 Raoul Snyman                                        #
# Portions copyright (c) 2008-2011 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Meinert Jordan, Armin Köhler, Andreas Preikschat,  #
# Christian Richter, Philip Ridout, Maikel Stuivenberg, Martin Thompson, Jon  #
# Tibble, Carsten Tinggaard, Frode Woldsund                                   #
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
The :mod:`http` module enables OpenLP to retrieve scripture from bible
websites.
"""
import logging
import os
import re
import sqlite3
import socket
import urllib
from HTMLParser import HTMLParseError

from BeautifulSoup import BeautifulSoup, NavigableString, Tag

from openlp.core.lib import Receiver, translate
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.utils import AppLocation, get_web_page
from openlp.plugins.bibles.lib import SearchResults
from openlp.plugins.bibles.lib.db import BibleDB, BiblesResourcesDB,  Book

log = logging.getLogger(__name__)

class BGExtract(object):
    """
    Extract verses from BibleGateway
    """
    def __init__(self, proxyurl=None):
        log.debug(u'init %s', proxyurl)
        self.proxyurl = proxyurl
        socket.setdefaulttimeout(30)

    def get_bible_chapter(self, version, bookname, chapter):
        """
        Access and decode bibles via the BibleGateway website.

        ``version``
            The version of the bible like 31 for New International version.

        ``bookname``
            Name of the Book.

        ``chapter``
            Chapter number.
        """
        log.debug(u'get_bible_chapter %s, %s, %s', version, bookname, chapter)
        url_params = urllib.urlencode(
            {u'search': u'%s %s' % (bookname, chapter),
            u'version': u'%s' % version})
        cleaner = [(re.compile('&nbsp;|<br />|\'\+\''), lambda match: '')]
        soup = get_soup_for_bible_ref(
            u'http://www.biblegateway.com/passage/?%s' % url_params,
            pre_parse_regex=r'<meta name.*?/>', pre_parse_substitute='',
            cleaner=cleaner)
        if not soup:
            return None
        Receiver.send_message(u'openlp_process_events')
        footnotes = soup.findAll(u'sup', u'footnote')
        if footnotes:
            [footnote.extract() for footnote in footnotes]
        crossrefs = soup.findAll(u'sup', u'xref')
        if crossrefs:
            [crossref.extract() for crossref in crossrefs]
        headings = soup.findAll(u'h5')
        if headings:
            [heading.extract() for heading in headings]
        cleanup = [(re.compile('\s+'), lambda match: ' ')]
        verses = BeautifulSoup(str(soup), markupMassage=cleanup)
        verse_list = {}
        for verse in verses(u'sup', u'versenum'):
            raw_verse_num =  verse.next
            clean_verse_num = 0
            # Not all verses exist in all translations and may or may not be
            # represented by a verse number. If they are not fine, if they are
            # it will probably be in a format that breaks int(). We will then
            # have no idea what garbage may be sucked in to the verse text so
            # if we do not get a clean int() then ignore the verse completely.
            try:
                clean_verse_num = int(str(raw_verse_num))
            except ValueError:
                log.exception(u'Illegal verse number in %s %s %s:%s',
                    version, bookname, chapter, unicode(raw_verse_num))
            if clean_verse_num:
                verse_text = raw_verse_num.next
                part = raw_verse_num.next.next
                while not (isinstance(part, Tag) and part.attrMap and
                    part.attrMap[u'class'] == u'versenum'):
                    # While we are still in the same verse grab all the text.
                    if isinstance(part, NavigableString):
                        verse_text = verse_text + part
                    if isinstance(part.next, Tag) and part.next.name == u'div':
                        # Run out of verses so stop.
                        break
                    part = part.next 
                verse_list[clean_verse_num] = unicode(verse_text)
        if not verse_list:
            log.debug(u'No content found in the BibleGateway response.')
            send_error_message(u'parse')
            return None
        return SearchResults(bookname, chapter, verse_list)


class BSExtract(object):
    """
    Extract verses from Bibleserver.com
    """
    def __init__(self, proxyurl=None):
        log.debug(u'init %s', proxyurl)
        self.proxyurl = proxyurl
        socket.setdefaulttimeout(30)

    def get_bible_chapter(self, version, bookname, chapter):
        """
        Access and decode bibles via Bibleserver mobile website

        ``version``
            The version of the bible like NIV for New International Version

        ``bookname``
            Text name of bible book e.g. Genesis, 1. John, 1John or Offenbarung

        ``chapter``
            Chapter number
        """
        log.debug(u'get_bible_chapter %s,%s,%s', version, bookname, chapter)
        chapter_url = u'http://m.bibleserver.com/text/%s/%s%s' % \
            (version, bookname, chapter)
        header = (u'Accept-Language', u'en')
        soup = get_soup_for_bible_ref(chapter_url, header)
        if not soup:
            return None
        Receiver.send_message(u'openlp_process_events')
        content = soup.find(u'div', u'content')
        if not content:
            log.exception(u'No verses found in the Bibleserver response.')
            send_error_message(u'parse')
            return None
        content = content.find(u'div').findAll(u'div')
        verse_number = re.compile(r'v(\d{1,2})(\d{3})(\d{3}) verse')
        verses = {}
        for verse in content:
            Receiver.send_message(u'openlp_process_events')
            versenumber = int(verse_number.sub(r'\3', verse[u'class']))
            verses[versenumber] = verse.contents[1].rstrip(u'\n')
        return SearchResults(bookname, chapter, verses)


class CWExtract(object):
    """
    Extract verses from CrossWalk/BibleStudyTools
    """
    def __init__(self, proxyurl=None):
        log.debug(u'init %s', proxyurl)
        self.proxyurl = proxyurl
        socket.setdefaulttimeout(30)

    def get_bible_chapter(self, version, bookname, chapter):
        """
        Access and decode bibles via the Crosswalk website

        ``version``
            The version of the bible like niv for New International Version

        ``bookname``
            Text name of in english e.g. 'gen' for Genesis

        ``chapter``
            Chapter number
        """
        log.debug(u'get_bible_chapter %s,%s,%s', version, bookname, chapter)
        urlbookname = bookname.replace(u' ', u'-')
        chapter_url = u'http://www.biblestudytools.com/%s/%s/%s.html' % \
            (version, urlbookname.lower(), chapter)
        soup = get_soup_for_bible_ref(chapter_url)
        if not soup:
            return None
        Receiver.send_message(u'openlp_process_events')
        htmlverses = soup.findAll(u'span', u'versetext')
        if not htmlverses:
            log.debug(u'No verses found in the CrossWalk response.')
            send_error_message(u'parse')
            return None
        verses = {}
        reduce_spaces = re.compile(r'[ ]{2,}')
        fix_punctuation = re.compile(r'[ ]+([.,;])')
        for verse in htmlverses:
            Receiver.send_message(u'openlp_process_events')
            versenumber = int(verse.contents[0].contents[0])
            versetext = u''
            for part in verse.contents:
                Receiver.send_message(u'openlp_process_events')
                if isinstance(part, NavigableString):
                    versetext = versetext + part
                elif part and part.attrMap and \
                    (part.attrMap[u'class'] == u'WordsOfChrist' or \
                    part.attrMap[u'class'] == u'strongs'):
                    for subpart in part.contents:
                        Receiver.send_message(u'openlp_process_events')
                        if isinstance(subpart, NavigableString):
                            versetext = versetext + subpart
                        elif subpart and subpart.attrMap and \
                            subpart.attrMap[u'class'] == u'strongs':
                            for subsub in subpart.contents:
                                Receiver.send_message(u'openlp_process_events')
                                if isinstance(subsub, NavigableString):
                                    versetext = versetext + subsub
            Receiver.send_message(u'openlp_process_events')
            # Fix up leading and trailing spaces, multiple spaces, and spaces
            # between text and , and .
            versetext = versetext.strip(u'\n\r\t ')
            versetext = reduce_spaces.sub(u' ', versetext)
            versetext = fix_punctuation.sub(r'\1', versetext)
            verses[versenumber] = versetext
        return SearchResults(bookname, chapter, verses)


class HTTPBible(BibleDB):
    log.info(u'%s HTTPBible loaded' , __name__)

    def __init__(self, parent, **kwargs):
        """
        Finds all the bibles defined for the system
        Creates an Interface Object for each bible containing connection
        information

        Throws Exception if no Bibles are found.

        Init confirms the bible exists and stores the database path.
        """
        BibleDB.__init__(self, parent, **kwargs)
        self.download_source = kwargs[u'download_source']
        self.download_name = kwargs[u'download_name']
        # TODO: Clean up proxy stuff. We probably want one global proxy per
        # connection type (HTTP and HTTPS) at most.
        self.proxy_server = None
        self.proxy_username = None
        self.proxy_password = None
        if u'proxy_server' in kwargs:
            self.proxy_server = kwargs[u'proxy_server']
        if u'proxy_username' in kwargs:
            self.proxy_username = kwargs[u'proxy_username']
        if u'proxy_password' in kwargs:
            self.proxy_password = kwargs[u'proxy_password']

    def do_import(self):
        """
        Run the import. This method overrides the parent class method. Returns
        ``True`` on success, ``False`` on failure.
        """
        self.wizard.progressBar.setMaximum(2)
        self.wizard.incrementProgressBar('Registering bible...')
        self.create_meta(u'download source', self.download_source)
        self.create_meta(u'download name', self.download_name)
        if self.proxy_server:
            self.create_meta(u'proxy server', self.proxy_server)
        if self.proxy_username:
            # Store the proxy userid.
            self.create_meta(u'proxy username', self.proxy_username)
        if self.proxy_password:
            # Store the proxy password.
            self.create_meta(u'proxy password', self.proxy_password)
        return True

    def get_verses(self, reference_list):
        """
        A reimplementation of the ``BibleDB.get_verses`` method, this one is
        specifically for web Bibles. It first checks to see if the particular
        chapter exists in the DB, and if not it pulls it from the web. If the
        chapter DOES exist, it simply pulls the verses from the DB using the
        ancestor method.

        ``reference_list``
            This is the list of references the media manager item wants. It is
            a list of tuples, with the following format::

                (book, chapter, start_verse, end_verse)

            Therefore, when you are looking for multiple items, simply break
            them up into references like this, bundle them into a list. This
            function then runs through the list, and returns an amalgamated
            list of ``Verse`` objects. For example::

                [(u'Genesis', 1, 1, 1), (u'Genesis', 2, 2, 3)]
        """
        for reference in reference_list:
            log.debug(u'Reference: %s', reference)
            book = reference[0]
            db_book = self.get_book(book)
            if not db_book:
                book_details = BiblesResourcesDB.get_book(book)
                if not book_details:
                    critical_error_message_box(
                        translate('BiblesPlugin', 'No Book Found'),
                        translate('BiblesPlugin', 'No matching '
                        'book could be found in this Bible. Check that you '
                        'have spelled the name of the book correctly.'))
                    return []
                db_book = self.create_book(book_details[u'name'],
                    book_details[u'abbreviation'],
                    book_details[u'testament_id'])
            book = db_book.name
            if BibleDB.get_verse_count(self, book, reference[1]) == 0:
                Receiver.send_message(u'cursor_busy')
                search_results = self.get_chapter(book, reference[1])
                if search_results and search_results.has_verselist():
                    ## We have found a book of the bible lets check to see
                    ## if it was there. By reusing the returned book name
                    ## we get a correct book. For example it is possible
                    ## to request ac and get Acts back.
                    bookname = search_results.book
                    Receiver.send_message(u'openlp_process_events')
                    # Check to see if book/chapter exists.
                    db_book = self.get_book(bookname)
                    self.create_chapter(db_book.id, search_results.chapter,
                        search_results.verselist)
                    Receiver.send_message(u'openlp_process_events')
                Receiver.send_message(u'cursor_normal')
            Receiver.send_message(u'openlp_process_events')
        return BibleDB.get_verses(self, reference_list)

    def get_chapter(self, book, chapter):
        """
        Receive the request and call the relevant handler methods.
        """
        log.debug(u'get_chapter %s, %s', book, chapter)
        log.debug(u'source = %s', self.download_source)
        if self.download_source.lower() == u'crosswalk':
            handler = CWExtract(self.proxy_server)
        elif self.download_source.lower() == u'biblegateway':
            handler = BGExtract(self.proxy_server)
        elif self.download_source.lower() == u'bibleserver':
            handler = BSExtract(self.proxy_server)
        return handler.get_bible_chapter(self.download_name, book, chapter)

    def get_books(self):
        """
        Return the list of books.
        """
        return [Book.populate(name=book['name'])
            for book in BiblesResourcesDB.get_books()]

    def get_chapter_count(self, book):
        """
        Return the number of chapters in a particular book.
        """
        return BiblesResourcesDB.get_chapter_count(book)

    def get_verse_count(self, book, chapter):
        """
        Return the number of verses for the specified chapter and book.

        ``book``
            The name of the book.

        ``chapter``
            The chapter whose verses are being counted.
        """
        return BiblesResourcesDB.get_verse_count(book, chapter)

def get_soup_for_bible_ref(reference_url, header=None, pre_parse_regex=None,
    pre_parse_substitute=None, cleaner=None):
    """
    Gets a webpage and returns a parsed and optionally cleaned soup or None.

    ``reference_url``
        The URL to obtain the soup from.

    ``header``
        An optional HTTP header to pass to the bible web server.

    ``pre_parse_regex``
        A regular expression to run on the webpage. Allows manipulation of the
        webpage before passing to BeautifulSoup for parsing.

    ``pre_parse_substitute``
        The text to replace any matches to the regular expression with.

    ``cleaner``
        An optional regex to use during webpage parsing.
    """
    if not reference_url:
        return None
    page = get_web_page(reference_url, header, True)
    if not page:
        send_error_message(u'download')
        return None
    page_source = page.read()
    if pre_parse_regex and pre_parse_substitute is not None:
        page_source = re.sub(pre_parse_regex, pre_parse_substitute, page_source)
    soup = None
    try:
        if cleaner:
            soup = BeautifulSoup(page_source, markupMassage=cleaner)
        else:
            soup = BeautifulSoup(page_source)
    except HTMLParseError:
        log.exception(u'BeautifulSoup could not parse the bible page.')
    if not soup:
        send_error_message(u'parse')
        return None
    Receiver.send_message(u'openlp_process_events')
    return soup

def send_error_message(error_type):
    """
    Send a standard error message informing the user of an issue.

    ``error_type``
        The type of error that occured for the issue.
    """
    if error_type == u'download':
        critical_error_message_box(
            translate('BiblePlugin.HTTPBible', 'Download Error'),
            translate('BiblePlugin.HTTPBible', 'There was a '
            'problem downloading your verse selection. Please check your '
            'Internet connection, and if this error continues to occur '
            'please consider reporting a bug.'))
    elif error_type == u'parse':
        critical_error_message_box(
            translate('BiblePlugin.HTTPBible', 'Parse Error'),
            translate('BiblePlugin.HTTPBible', 'There was a '
            'problem extracting your verse selection. If this error continues '
            'to occur please consider reporting a bug.'))
