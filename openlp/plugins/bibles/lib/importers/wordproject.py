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
import re
import logging
from codecs import open as copen
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from bs4 import BeautifulSoup, Tag, NavigableString

from openlp.plugins.bibles.lib.bibleimport import BibleImport

BOOK_NUMBER_PATTERN = re.compile(r'\[(\d+)\]')
REPLACE_SPACES = re.compile(r'\s{2,}')

log = logging.getLogger(__name__)


class WordProjectBible(BibleImport):
    """
    `WordProject <http://www.wordproaudio.com/>`_ Bible format importer class.
    """
    def _cleanup(self):
        """
        Clean up after ourselves
        """
        self.tmp.cleanup()

    def _unzip_file(self):
        """
        Unzip the file to a temporary directory
        """
        self.tmp = TemporaryDirectory()
        zip_file = ZipFile(os.path.abspath(self.filename))
        zip_file.extractall(self.tmp.name)
        self.base_dir = os.path.join(self.tmp.name, os.path.splitext(os.path.basename(self.filename))[0])

    def process_books(self):
        """
        Extract and create the bible books from the parsed html

        :param bible_data: parsed xml
        :return: None
        """
        with copen(os.path.join(self.base_dir, 'index.htm'), encoding='utf-8', errors='ignore') as index_file:
            page = index_file.read()
        soup = BeautifulSoup(page, 'lxml')
        bible_books = soup.find('div', 'textOptions').find_all('li')
        book_count = len(bible_books)
        for li_book in bible_books:
            log.debug(li_book)
            if self.stop_import_flag:
                break
            # Sometimes the structure is "[1] <a>Genesis</a>", and sometimes it's "<a>[1] Genesis</a>"
            if isinstance(li_book.contents[0], NavigableString) and str(li_book.contents[0]).strip():
                book_string = str(li_book.contents[0])
                book_name = str(li_book.a.contents[0])
            elif li_book.a:
                book_string, book_name = str(li_book.a.contents[0]).split(' ', 1)
            book_link = li_book.a['href']
            book_id = int(BOOK_NUMBER_PATTERN.search(book_string).group(1))
            book_name = book_name.strip()
            db_book = self.find_and_create_book(book_name, book_count, self.language_id, book_id)
            self.process_chapters(db_book, book_id, book_link)
            self.session.commit()

    def process_chapters(self, db_book, book_id, book_link):
        """
        Extract the chapters, and do some initial processing of the verses

        :param book: An OpenLP bible database book object
        :param chapters: parsed chapters
        :return: None
        """
        log.debug(book_link)
        book_file = os.path.join(self.base_dir, os.path.normpath(book_link))
        with copen(book_file, encoding='utf-8', errors='ignore') as f:
            page = f.read()
        soup = BeautifulSoup(page, 'lxml')
        header_div = soup.find('div', 'textHeader')
        chapters_p = header_div.find('p')
        if not chapters_p:
            chapters_p = soup.p
        log.debug(chapters_p)
        for item in chapters_p.contents:
            if self.stop_import_flag:
                break
            if isinstance(item, Tag) and item.name in ['a', 'span']:
                chapter_number = int(item.string.strip())
                self.set_current_chapter(db_book.name, chapter_number)
                self.process_verses(db_book, book_id, chapter_number)

    def process_verses(self, db_book, book_number, chapter_number):
        """
        Get the verses for a particular book
        """
        chapter_file_name = os.path.join(self.base_dir, '{:02d}'.format(book_number), '{}.htm'.format(chapter_number))
        with copen(chapter_file_name, encoding='utf-8', errors='ignore') as chapter_file:
            page = chapter_file.read()
        soup = BeautifulSoup(page, 'lxml')
        text_body = soup.find('div', 'textBody')
        if text_body:
            verses_p = text_body.find('p')
        else:
            verses_p = soup.find_all('p')[2]
        verse_number = 0
        verse_text = ''
        for item in verses_p.contents:
            if self.stop_import_flag:
                break
            if isinstance(item, Tag) and 'verse' in item.get('class', []):
                if verse_number > 0:
                    self.process_verse(db_book, chapter_number, verse_number, verse_text.strip())
                verse_number = int(item.string.strip())
                verse_text = ''
            elif isinstance(item, NavigableString):
                verse_text += str(item)
            elif isinstance(item, Tag) and item.name in ['span', 'a']:
                verse_text += str(item.string)
            else:
                log.warning('Can\'t store %s', item)
        self.process_verse(db_book, chapter_number, verse_number, verse_text.strip())

    def process_verse(self, db_book, chapter_number, verse_number, verse_text):
        """
        Process a verse element
        :param book: A database Book object
        :param chapter_number: The chapter number to add the verses to (int)
        :param element: The verse element to process. (etree element type)
        :param use_milestones: set to True to process a 'milestone' verse. Defaults to False
        :return: None
        """
        if verse_text:
            log.debug('%s %s:%s %s', db_book.name, chapter_number, verse_number, verse_text.strip())
            self.create_verse(db_book.id, chapter_number, verse_number, verse_text.strip())

    def do_import(self, bible_name=None):
        """
        Loads a Bible from file.
        """
        self.log_debug('Starting WordProject import from "{name}"'.format(name=self.filename))
        self._unzip_file()
        self.language_id = self.get_language_id(None, bible_name=self.filename)
        result = False
        if self.language_id:
            self.process_books()
            result = True
        self._cleanup()
        return result
