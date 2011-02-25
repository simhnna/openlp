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
The XML of `Foilpresenter <http://foilpresenter.de/>`_  songs is of the format::

    <?xml version="1.0" encoding="UTF-8"?>
    <foilpresenterfolie version="00300.000092">
    <id>2004.6.18.18.44.37.0767</id>
    <lastchanged>2011.1.21.8.53.5</lastchanged>
    <titel>
        <titelstring>Above all</titelstring>
    </titel>
    <sprache>1</sprache>
    <ccliid></ccliid>
    <tonart></tonart>
    <valign>0</valign>
    <notiz>Notiz</notiz>
    <versionsinfo>1.0</versionsinfo>
    <farben>
        <cback>0,0,0</cback>
        <ctext>255,255,255</ctext>
    </farben>
    <reihenfolge>
        <name>Standard</name>
        <strophennummer>0</strophennummer>
    </reihenfolge>
    <strophen>
        <strophe>
            <align>0</align>
            <font>Verdana</font>
            <textsize>14</textsize>
            <bold>0</bold>
            <italic>0</italic>
            <underline>0</underline>
            <key>1</key>
            <text>Above all powers, above all kings,
    above all nature an all created things;
    above all wisdom and all the ways of man,
    You were here before the world began.</text>
            <sortnr>1</sortnr>
        </strophe>
    </strophen>
    <verkn>
        <filename>Herr du bist maechtig.foil</filename>
    </verkn>
    <copyright>
        <font>Arial</font>
        <textsize>7</textsize>
        <anzeigedauer>3</anzeigedauer>
        <bold>0</bold>
        <italic>1</italic>
        <underline>0</underline>
        <text>Text und Musik: Lenny LeBlanc/Paul Baloche</text>
    </copyright>
    <buch>
        <bucheintrag>
            <name>Feiert Jesus 3</name>
            <nummer>10</nummer>
        </bucheintrag>
    </buch>
    <kategorien>
        <name>Worship</name>
    </kategorien>
    </foilpresenterfolie>
"""

import logging
import re
import os

from lxml import etree, objectify

from openlp.core.ui.wizard import WizardStrings
from openlp.plugins.songs.lib import add_author_unknown, VerseType
from openlp.plugins.songs.lib.songimport import SongImport
from openlp.plugins.songs.lib.db import Author, Book, Song, Topic
from openlp.plugins.songs.lib.xml import SongXML

log = logging.getLogger(__name__)

class FoilPresenterImport(SongImport):
    """
    This provides the Foilpresenter import.
    """
    def __init__(self, manager, **kwargs):
        """
        Initialise the import.
        """
        log.debug(u'initialise FoilPresenterImport')
        SongImport.__init__(self, manager, **kwargs)
        self.FoilPresenter = FoilPresenter(self.manager)

    def do_import(self):
        """
        Imports the songs.
        """
        self.import_wizard.progressBar.setMaximum(len(self.import_source))
        parser = etree.XMLParser(remove_blank_text=True)
        for file_path in self.import_source:
            if self.stop_import_flag:
                return False
            self.import_wizard.incrementProgressBar(
                WizardStrings.ImportingType % os.path.basename(file_path))
            try:
                parsed_file = etree.parse(file_path, parser)
                xml = unicode(etree.tostring(parsed_file))
                if self.FoilPresenter.xml_to_song(xml) is None:
                    log.debug(u'File could not be imported: %s' % file_path)
            except etree.XMLSyntaxError:
                log.exception(u'XML syntax error in file %s' % file_path)
        return True


class FoilPresenter(object):
    """
    This class represents the converter for Foilpresenter XML from a song.

    As Foilpresenter has a rich set of different features, we cannot support
    them all. The following features are supported by the :class:`Foilpresenter`

    OpenPL does not support styletype and font attributes like "align, font,
        textsize, bold, italic, underline"

    *<lastchanged>*
        This property is currently not supported.

    *<title>*
        As OpenLP does only support one title, the first titlestring becomes
            title, all other titlestrings will be alternate titles

    *<sprache>*
        This property is not supported.

    *<ccliid>*
        The *<ccliid>* property is fully supported.

    *<tonart>*
        This property is currently not supported.

    *<valign>*
        This property is not supported.

    *<notiz>*
        The *<notiz>* property is fully supported.

    *<versionsinfo>*
        This property is not supported.

    *<farben>*
        This property is not supported.

    *<reihenfolge>* = verseOrder
        OpenLP supports this property.

    *<strophen>*
        Only the attributes *key* and *text* are supported.

    *<verkn>*
        This property is not supported.

    *<verkn>*
        This property is not supported.

    *<copyright>*
        Only the attribute *text* is supported. => Done

    *<buch>* = songbooks
        As OpenLP does only support one songbook, we cannot consider more than
        one songbook.

    *<kategorien>*
        This property is not supported.

    The tag *<author>* is not support by foilpresenter, mostly the author is
        named in the <copyright> tag. We try to extract the authors from the
        <copyright> tag.

    """
    def __init__(self, manager):
        self.manager = manager

    def xml_to_song(self, xml):
        """
        Create and save a song from Foilpresenter format xml to the database.

        ``xml``
            The XML to parse (unicode).
        """
        # No xml get out of here.
        if not xml:
            return None
        song = Song()
        if xml[:5] == u'<?xml':
            xml = xml[38:]
        # Because "text" seems to be an reserverd word, we have to recompile it.
        xml = re.compile(u'<text>').sub(u'<text_>', xml)
        xml = re.compile(u'</text>').sub(u'</text_>', xml)
        song_xml = objectify.fromstring(xml)
        foilpresenterfolie = song_xml
        self._process_copyright(foilpresenterfolie, song)
        self._process_cclinumber(foilpresenterfolie, song)
        self._process_titles(foilpresenterfolie, song)
        # The verse order is processed with the lyrics!
        self._process_lyrics(foilpresenterfolie, song)
        self._process_comments(foilpresenterfolie, song)
        self._process_authors(foilpresenterfolie, song)
        self._process_songbooks(foilpresenterfolie, song)
        self._process_topics(foilpresenterfolie, song)
        self.manager.save_object(song)
        return song.id

    def _child(self, element):
        """
        This returns the text of an element as unicode string.

        ``element``
            The element.
        """
        if element is not None:
            return unicode(element)
        return u''

    def _process_authors(self, foilpresenterfolie, song):
        """
        Adds the authors specified in the XML to the song.

        ``foilpresenterfolie``
            The property object (lxml.objectify.ObjectifiedElement).

        ``song``
            The song object.
        """
        authors = []
        try:
            copyright = self._child(foilpresenterfolie.copyright.text_)
        except AttributeError:
            copyright = None
        if copyright:
            strings = []
            if copyright.find(u'Copyright') != -1:
                temp = copyright.partition(u'Copyright')
                copyright = temp[0]
            elif copyright.find(u'copyright') != -1:
                temp = copyright.partition(u'copyright')
                copyright = temp[0]
            elif copyright.find(u'©') != -1:
                temp = copyright.partition(u'©')
                copyright = temp[0]
            elif copyright.find(u'(c)') != -1:
                temp = copyright.partition(u'(c)')
                copyright = temp[0]
            elif copyright.find(u'(C)') != -1:
                temp = copyright.partition(u'(C)')
                copyright = temp[0]
            elif copyright.find(u'c)') != -1:
                temp = copyright.partition(u'c)')
                copyright = temp[0]
            elif copyright.find(u'C)') != -1:
                temp = copyright.partition(u'C)')
                copyright = temp[0]
            elif copyright.find(u'C:') != -1:
                temp = copyright.partition(u'C:')
                copyright = temp[0]
            elif copyright.find(u'C,)') != -1:
                temp = copyright.partition(u'C,)')
                copyright = temp[0]
            copyright = re.compile(u'\\n').sub(u' ', copyright)
            copyright = re.compile(u'\(.*\)').sub(u'', copyright)
            if copyright.find(u'Rechte') != -1:
                temp = copyright.partition(u'Rechte')
                copyright = temp[0]
            markers = [u'Text +u\.?n?d? +Melodie[\w\,\. ]*:',
                u'Text +u\.?n?d? +Musik', u'T & M', u'Melodie und Satz',
                u'Text[\w\,\. ]*:', u'Melodie', u'Musik', u'Satz',
                u'Weise', u'[dD]eutsch', u'[dD]t[\.\:]', u'Englisch',
                u'[oO]riginal',  u'Bearbeitung',  u'[R|r]efrain']
            for marker in markers:
                copyright = re.compile(marker).sub(u'<marker>', copyright, re.U)
            copyright = re.compile(u'(?<=<marker>) *:').sub(u'', copyright)
            i = 0
            x = 0
            while i != 1:
                if copyright.find(u'<marker>') != -1:
                    temp = copyright.partition(u'<marker>')
                    if temp[0].strip() and x > 0:
                        strings.append(temp[0])
                    copyright = temp[2]
                    x += 1
                elif x > 0:
                    strings.append(copyright)
                    i = 1
                else:
                    i = 1
            for author in strings:
                temp = re.split(u',(?=\D{2})|(?<=\D),|\/(?=\D{3,})|(?<=\D);',
                    author)
                for tempx in temp:
                    author_temp.append(tempx)
                for author in author_temp:
                    regex = u'^[\/,;\-\s]+|[\/,;\-\s]+$|'\
                        '\s*[0-9]{4}\s*[\-\/]?\s*([0-9]{4})?[\/,;\-\s]*$'
                    author = re.compile(regex).sub(u'', author)
                    author = re.compile(
                        u'[0-9]{1,2}\.\s?J(ahr)?h\.|um\s*$|vor\s*$').sub(u'',
                        author)
                    author = re.compile(u'[N|n]ach.*$').sub(u'', author)
                    author = author.strip()
                    if re.search(
                        u'\w+\.?\s+\w{3,}\s+[a|u]nd\s|\w+\.?\s+\w{3,}\s+&\s',
                        author, re.U):
                        temp = re.split(u'\s[a|u]nd\s|\s&\s', author)
                        for tempx in temp:
                            tempx = tempx.strip()
                            authors.append(tempx)
                    elif len(author) > 2:
                        authors.append(author)
        for display_name in authors:
            author = self.manager.get_object_filtered(Author,
                Author.display_name == display_name)
            if author is None:
                # We need to create a new author, as the author does not exist.
                author = Author.populate(display_name=display_name,
                    last_name = display_name.split(u' ')[-1],
                    first_name = u' '.join(display_name.split(u' ')[:-1]))
                self.manager.save_object(author)
            song.authors.append(author)
        if not song.authors:
            add_author_unknown(self.manager, song)

    def _process_cclinumber(self, foilpresenterfolie, song):
        """
        Adds the CCLI number to the song.

        ``foilpresenterfolie``
            The property object (lxml.objectify.ObjectifiedElement).

        ``song``
            The song object.
        """
        try:
            song.ccli_number = self._child(foilpresenterfolie.ccliid)
        except AttributeError:
            song.ccli_number = u''

    def _process_comments(self, foilpresenterfolie, song):
        """
        Joins the comments specified in the XML and add it to the song.

        ``foilpresenterfolie``
            The property object (lxml.objectify.ObjectifiedElement).

        ``song``
            The song object.
        """
        try:
            song.comments = self._child(foilpresenterfolie.notiz)
        except AttributeError:
            song.comments = u''

    def _process_copyright(self, foilpresenterfolie, song):
        """
        Adds the copyright to the song.

        ``foilpresenterfolie``
            The property object (lxml.objectify.ObjectifiedElement).

        ``song``
            The song object.
        """
        try:
            song.copyright = self._child(foilpresenterfolie.copyright.text_)
        except AttributeError:
            song.copyright = u''

    def _process_lyrics(self, foilpresenterfolie, song):
        """
        Processes the verses and search_lyrics for the song.

        ``foilpresenterfolie``
            The foilpresenterfolie object (lxml.objectify.ObjectifiedElement).

        ``song``
            The song object.
        """
        sxml = SongXML()
        search_text = u''
        temp_verse_order = {}
        temp_verse_order_backup = []
        temp_sortnr_backup = 1
        temp_sortnr_liste = []
        versenumber = {u'V': 1,  u'C': 1, u'B': 1, u'E': 1, u'O': 1, u'I': 1,
            u'P': 1}
        for strophe in foilpresenterfolie.strophen.strophe:
            text = self._child(strophe.text_)
            verse_name = self._child(strophe.key)
            children = strophe.getchildren()
            sortnr = False
            for child in children:
                if child.tag == u'sortnr':
                    verse_sortnr = self._child(strophe.sortnr)
                    sortnr = True
                # In older Version there is no sortnr, but we need one
            if sortnr == False:
                verse_sortnr = unicode(temp_sortnr_backup)
                temp_sortnr_backup += 1
            # Foilpresenter allows e. g. "Ref" or "1", but we need "C1" or "V1".
            temp_sortnr_liste.append(verse_sortnr)
            temp_verse_name = re.compile(u'[0-9].*').sub(u'', verse_name)
            temp_verse_name = temp_verse_name[:3].lower()
            if temp_verse_name == u'ref':
                verse_type = u'C'
            elif temp_verse_name == u'r':
                verse_type = u'C'
            elif temp_verse_name == u'':
                verse_type = u'V'
            elif temp_verse_name == u'v':
                verse_type = u'V'
            elif temp_verse_name == u'bri':
                verse_type = u'B'
            elif temp_verse_name == u'cod':
                verse_type = u'E'
            elif temp_verse_name == u'sch':
                verse_type = u'E'
            elif temp_verse_name == u'pre':
                verse_type = u'P'
            elif temp_verse_name == u'int':
                verse_type = u'I'
            else:
                verse_type = u'O'
            verse_number = re.compile(u'[a-zA-Z.+-_ ]*').sub(u'', verse_name)
            #verse_part = re.compile(u'[0-9]*').sub(u'', verse_name[1:])
            # Foilpresenter allows e. g. "C", but we need "C1".
            if not verse_number:
                verse_number = unicode(versenumber[verse_type])
                versenumber[verse_type] += 1
            else:
                # test if foilpresenter have the same versenumber two times with
                # different parts raise the verse number
                for value in temp_verse_order_backup:
                    if value == (u''.join((verse_type, verse_number))):
                        verse_number = unicode(int(verse_number) + 1)
            verse_type_index = VerseType.from_tag(verse_type[0])
            verse_type = VerseType.Names[verse_type_index]
            temp_verse_order[verse_sortnr] = (u''.join((verse_type[0],
                verse_number)))
            temp_verse_order_backup.append(u''.join((verse_type[0],
                verse_number)))
            sxml.add_verse_to_lyrics(verse_type, verse_number, text)
            search_text = search_text + text
        song.search_lyrics = search_text.lower()
        song.lyrics = unicode(sxml.extract_xml(), u'utf-8')
        # Process verse order
        verse_order = []
        verse_strophenr = []
        for strophennummer in foilpresenterfolie.reihenfolge.strophennummer:
            verse_strophenr.append(strophennummer)
        # Currently we do not support different "parts"!
        if u'0' in temp_verse_order:
            for vers in temp_verse_order_backup:
                verse_order.append(vers)
        else:
            for number in verse_strophenr:
                numberx = temp_sortnr_liste[int(number)]
                verse_order.append(temp_verse_order[unicode(numberx)])
        song.verse_order = u' '.join(verse_order)

    def _process_songbooks(self, foilpresenterfolie, song):
        """
        Adds the song book and song number specified in the XML to the song.

        ``foilpresenterfolie``
            The property object (lxml.objectify.ObjectifiedElement).

        ``song``
            The song object.
        """
        song.song_book_id = 0
        song.song_number = u''
        try:
            for bucheintrag in foilpresenterfolie.buch.bucheintrag:
                bookname = self._child(bucheintrag.name)
                if bookname:
                    book = self.manager.get_object_filtered(Book,
                        Book.name == bookname)
                    if book is None:
                        # We need to create a book, because it does not exist.
                        book = Book.populate(name=bookname, publisher=u'')
                        self.manager.save_object(book)
                    song.song_book_id = book.id
                    try:
                        if self._child(bucheintrag.nummer):
                            song.song_number = self._child(bucheintrag.nummer)
                    except AttributeError:
                        pass
                    # We only support one song book, so take the first one.
                    break
        except AttributeError:
            pass

    def _process_titles(self, foilpresenterfolie, song):
        """
        Processes the titles specified in the song's XML.

        ``foilpresenterfolie``
            The property object (lxml.objectify.ObjectifiedElement).

        ``song``
            The song object.
        """
        for titelstring in foilpresenterfolie.titel.titelstring:
            if not song.title:
                song.title = self._child(titelstring)
                song.search_title = unicode(song.title)
                song.alternate_title = u''
            else:
                song.alternate_title = self._child(titelstring)
                song.search_title += u'@' + song.alternate_title
        song.search_title = re.sub(r'[\'"`,;:(){}?]+', u'',
            unicode(song.search_title)).lower()

    def _process_topics(self, foilpresenterfolie, song):
        """
        Adds the topics to the song.

        ``foilpresenterfolie``
            The property object (lxml.objectify.ObjectifiedElement).

        ``song``
            The song object.
        """
        try:
            for name in foilpresenterfolie.kategorien.name:
                topictext = self._child(name)
                if topictext:
                    topic = self.manager.get_object_filtered(Topic,
                        Topic.name == topictext)
                    if topic is None:
                        # We need to create a topic, because it does not exist.
                        topic = Topic.populate(name=topictext)
                        self.manager.save_object(topic)
                    song.topics.append(topic)
        except AttributeError:
            pass

    def _dump_xml(self, xml):
        """
        Debugging aid to dump XML so that we can see what we have.
        """
        return etree.tostring(xml, encoding=u'UTF-8',
            xml_declaration=True, pretty_print=True)
