property# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2010 Raoul Snyman                                        #
# Portions copyright (c) 2008-2010 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Christian Richter, Maikel Stuivenberg, Martin      #
# Thompson, Jon Tibble, Carsten Tinggaard                                     #
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

# OOo API documentation:
# http://wiki.services.openoffice.org/wiki/Documentation/BASIC_Guide/Structure_of_Text_Documents
# http://wiki.services.openoffice.org/wiki/Documentation/DevGuide/Text/Iterating_over_Text
# http://www.oooforum.org/forum/viewtopic.phtml?t=14409
# http://wiki.services.openoffice.org/wiki/Python

import re
import os
import time
from PyQt4 import QtCore
from songimport import SongImport

if os.name == u'nt':
    from win32com.client import Dispatch
    BOLD = 150.0
    ITALIC = 2
    PAGE_BEFORE = 4
    PAGE_AFTER = 5
    PAGE_BOTH = 6
else:
    import uno
    from com.sun.star.awt.FontWeight import BOLD
    from com.sun.star.awt.FontSlant import ITALIC
    from com.sun.star.style.BreakType import PAGE_BEFORE, PAGE_AFTER, PAGE_BOTH

class SofImport(object):
    """
    Import songs provided on disks with the Songs of Fellowship music books
    VOLS1_2.RTF, sof3words.rtf and sof4words.rtf
    
    Use OpenOffice.org Writer for processing the rtf file

    The three books are not only inconsistant with each other, they are 
    inconsistant in themselves too with their formatting. Not only this, but
    the 1+2 book does not space out verses correctly. This script attempts
    to sort it out, but doesn't get it 100% right. But better than having to 
    type them all out!

    It attempts to detect italiced verses, and treats these as choruses in
    the verse ordering. Again not perfect, but a start.
    """
    def __init__(self, songmanager):
        """
        Initialise the class. Requires a songmanager class which is passed
        to SongImport for writing song to disk
        """
        self.song = None
        self.manager = songmanager
        self.process_started = False

    def import_sof(self, filename):
        self.start_ooo()
        self.open_ooo_file(filename)
        self.process_doc()
        self.close_ooo()

    def start_ooo(self):
        """
        Start OpenOffice.org process
        TODO: The presentation/Impress plugin may already have it running
        """
        if os.name == u'nt':
            self.start_ooo_process()
            self.desktop = self.manager.createInstance(u'com.sun.star.frame.Desktop')
        else:
            context = uno.getComponentContext()
            resolver = context.ServiceManager.createInstanceWithContext(
                u'com.sun.star.bridge.UnoUrlResolver', context)
            ctx = None
            loop = 0
            while ctx is None and loop < 5:
                try:
                    ctx = resolver.resolve(u'uno:socket,host=localhost,' \
                        + 'port=2002;urp;StarOffice.ComponentContext')
                except:
                    pass
                self.start_ooo_process()
                loop += 1
            manager = ctx.ServiceManager
            self.desktop = manager.createInstanceWithContext(
                "com.sun.star.frame.Desktop", ctx )
            
    def start_ooo_process(self):
        try:
            if os.name == u'nt':
                self.manager = Dispatch(u'com.sun.star.ServiceManager')
                self.manager._FlagAsMethod(u'Bridge_GetStruct')
                self.manager._FlagAsMethod(u'Bridge_GetValueObject')
            else:
                cmd = u'openoffice.org -nologo -norestore -minimized -invisible ' \
                    + u'-nofirststartwizard ' \
                    + '-accept="socket,host=localhost,port=2002;urp;"'
                process = QtCore.QProcess()
                process.startDetached(cmd)
                process.waitForStarted()
            self.process_started = True
        except:
            pass

    def open_ooo_file(self, filepath):
        """
        Open the passed file in OpenOffice.org Writer
        """
        if os.name == u'nt':
            url = u'file:///' + filepath.replace(u'\\', u'/')
            url = url.replace(u':', u'|').replace(u' ', u'%20')
        else:
            url = uno.systemPathToFileUrl(filepath)
        properties = []
        properties = tuple(properties)
        self.document = self.desktop.loadComponentFromURL(url, u'_blank',
            0, properties)

    def close_ooo(self):
        """
        Close RTF file. Note, on Windows we'll leave OOo running
        Leave running on Windows
        """
        self.document.close(True)
        if self.process_started:
            self.desktop.terminate()

    def process_doc(self):
        """
        Process the RTF file, a paragraph at a time
        """            
        self.blanklines = 0
        self.new_song()
        paragraphs = self.document.getText().createEnumeration()
        while paragraphs.hasMoreElements():
            paragraph = paragraphs.nextElement()
            if paragraph.supportsService("com.sun.star.text.Paragraph"):
                self.process_paragraph(paragraph)
        if self.song:
            self.song.finish()
            self.song = None

    def process_paragraph(self, paragraph):
        """
        Process a paragraph. 
        In the first book, a paragraph is a single line. In the latter ones
        they may contain multiple lines.
        Each paragraph contains textportions. Each textportion has it's own
        styling, e.g. italics, bold etc. 
        Also check for page breaks, which indicates a new song in books 1+2.
        In later books, there may not be line breaks, so check for 3 or more
        newlines
        """
        text = u''
        textportions = paragraph.createEnumeration()
        while textportions.hasMoreElements():
            textportion = textportions.nextElement()
            if textportion.BreakType in (PAGE_BEFORE, PAGE_BOTH):
                self.process_paragraph_text(text)
                self.new_song()
                text = u''
            text += self.process_textportion(textportion)
            if textportion.BreakType in (PAGE_AFTER, PAGE_BOTH):
                self.process_paragraph_text(text)
                self.new_song()
                text = u''
        self.process_paragraph_text(text)
        
    def process_paragraph_text(self, text):
        """
        Split the paragraph text into multiple lines and process
        """
        for line in text.split(u'\n'):
            self.process_paragraph_line(line)
        if self.blanklines > 2:
            self.new_song()

    def process_paragraph_line(self, text):
        """ 
        Process a single line. Throw away that text which isn't relevant, i.e.
        stuff that appears at the end of the song.
        Anything that is OK, append to the current verse
        """
        text = text.strip()        
        if text == u'':
            self.blanklines += 1
            if self.blanklines > 1:
                return
            if self.song.get_title() != u'':
                self.finish_verse()
            return
        self.blanklines = 0
        if self.skip_to_close_bracket:
            if text.endswith(u')'):
                self.skip_to_close_bracket = False
            return 
        if text.startswith(u'CCL Licence'):
            self.italics = False
            return
        if text == u'A Songs of Fellowship Worship Resource':
            return
        if text.startswith(u'(NB.') or text.startswith(u'(Regrettably') \
            or text.startswith(u'(From'):
            self.skip_to_close_bracket = True
            return
        if text.startswith(u'Copyright'):
            self.song.add_copyright(text)
            return
        if text == u'(Repeat)':
            self.finish_verse()
            self.song.repeat_verse()
            return
        if self.song.get_title() == u'':
            if self.song.get_copyright() == u'':
                self.add_author(text)
            else:
                self.song.add_copyright(text)
            return
        self.add_verse_line(text)

    def process_textportion(self, textportion):
        """
        Process a text portion. Here we just get the text and detect if
        it's bold or italics. If it's bold then its a song number or song title.
        Song titles are in all capitals, so we must bring the capitalization
        into line
        """
        text = textportion.getString()
        text = self.tidy_text(text)
        if text.strip() == u'':
            return text
        if textportion.CharWeight == BOLD:
            boldtext = text.strip()
            if boldtext.isdigit() and self.song.get_song_number() == '':
                self.add_songnumber(boldtext)
                return u''
            if self.song.get_title() == u'':
                text = self.uncap_text(text)
                self.add_title(text)
            return text
        if text.strip().startswith(u'('):
            return text
        self.italics = (textportion.CharPosture == ITALIC)
        return text

    def new_song(self):
        """
        A change of song. Store the old, create a new
        ... but only if the last song was complete. If not, stick with it
        """
        if self.song:
            self.finish_verse()
            if not self.song.check_complete():
                return
            self.song.finish()
        self.song = SongImport(self.manager)
        self.skip_to_close_bracket = False
        self.is_chorus = False
        self.italics = False
        self.currentverse = u''

    def add_songnumber(self, song_no):
        """
        Add a song number, store as alternate title. Also use the song
        number to work out which songbook we're in
        """
        self.song.set_song_number(song_no)
        self.song.set_alternate_title(song_no + u'.')
        if int(song_no) <= 640:
            self.song.set_song_book(u'Songs of Fellowship 1', 
                u'Kingsway Publications')
        elif int(song_no) <= 1150:
            self.song.set_song_book(u'Songs of Fellowship 2', 
                u'Kingsway Publications')
        elif int(song_no) <= 1690:
            self.song.set_song_book(u'Songs of Fellowship 3', 
                u'Kingsway Publications')
        else:
            self.song.set_song_book(u'Songs of Fellowship 4', 
                u'Kingsway Publications')

    def add_title(self, text):
        """
        Add the title to the song. Strip some leading/trailing punctuation that
        we don't want in a title
        """
        title = text.strip()
        if title.startswith(u'\''):
            title = title[1:]
        if title.endswith(u','):
            title = title[:-1]
        self.song.set_title(title)

    def add_author(self, text):
        """
        Add the author. OpenLP stores them individually so split by 'and', '&'
        and comma.
        However need to check for "Mr and Mrs Smith" and turn it to 
        "Mr Smith" and "Mrs Smith".
        """
        text = text.replace(u' and ', u' & ')
        for author in text.split(u','):
            authors = author.split(u'&')
            for i in range(len(authors)):
                author2 = authors[i].strip()
                if author2.find(u' ') == -1 and i < len(authors) - 1:
                    author2 = author2 + u' ' \
                        + authors[i + 1].strip().split(u' ')[-1]
                if author2.endswith(u'.'):
                    author2 = author2[:-1]
                if author2:
                    self.song.add_author(author2)

    def add_verse_line(self, text):
        """
        Add a line to the current verse. If the formatting has changed and
        we're beyond the second line of first verse, then this indicates
        a change of verse. Italics are a chorus
        """
        if self.italics != self.is_chorus and ((len(self.song.verses) > 0) or 
            (self.currentverse.count(u'\n') > 1)):
            self.finish_verse()
        if self.italics:
            self.is_chorus = True
        self.currentverse += text + u'\n'

    def finish_verse(self):
        """
        Verse is finished, store it. Note in book 1+2, some songs are formatted
        incorrectly. Here we try and split songs with missing line breaks into
        the correct number of verses.
        """
        if self.currentverse.strip() == u'':
            return
        if self.is_chorus:
            versetag = u'C'
            splitat = None
        else:
            versetag = u'V'
            splitat = self.verse_splits(self.song.get_song_number())
        if splitat:
            ln = 0
            verse = u''
            for line in self.currentverse.split(u'\n'):
                ln += 1
                if line == u'' or ln > splitat:
                    self.song.add_verse(verse, versetag)
                    ln = 0
                    if line:
                        verse = line + u'\n'
                    else:   
                        verse = u''
                else:
                    verse += line + u'\n'
            if verse:
                self.song.add_verse(verse, versetag)
        else:
            self.song.add_verse(self.currentverse, versetag)
        self.currentverse = u''
        self.is_chorus = False

    def tidy_text(self, text):
        """
        Get rid of some dodgy unicode and formatting characters we're not
        interested in. Some can be converted to ascii.
        """
        text = text.replace(u'\t', u' ')
        text = text.replace(u'\r', u'\n')
        text = text.replace(u'\u2018', u'\'')
        text = text.replace(u'\u2019', u'\'')
        text = text.replace(u'\u201c', u'"')
        text = text.replace(u'\u201d', u'"')
        text = text.replace(u'\u2026', u'...')
        text = text.replace(u'\u2013', u'-')
        text = text.replace(u'\u2014', u'-')
        return text

    def uncap_text(self, text):
        """ 
        Words in the title are in all capitals, so we lowercase them.
        However some of these words, e.g. referring to God need a leading 
        capital letter.
        
        There is a complicated word "One", which is sometimes lower and 
        sometimes upper depending on context. Never mind, keep it lower.
        """
        textarr = re.split(u'(\W+)', text)
        textarr[0] = textarr[0].capitalize()
        for i in range(1, len(textarr)):
            # Do not translate these. Fixed strings in SOF song file
            if textarr[i] in (u'JESUS', u'CHRIST', u'KING', u'ALMIGHTY', 
                u'REDEEMER', u'SHEPHERD', u'SON', u'GOD', u'LORD', u'FATHER', 
                u'HOLY', u'SPIRIT', u'LAMB', u'YOU', u'YOUR', u'I', u'I\'VE', 
                u'I\'M', u'I\'LL', u'SAVIOUR', u'O', u'YOU\'RE', u'HE', u'HIS', 
                u'HIM', u'ZION', u'EMMANUEL', u'MAJESTY', u'JESUS\'', u'JIREH', 
                u'JUDAH', u'LION', u'LORD\'S', u'ABRAHAM', u'GOD\'S', 
                u'FATHER\'S', u'ELIJAH'):
                textarr[i] = textarr[i].capitalize()
            else:
                textarr[i] = textarr[i].lower()
        text = u''.join(textarr)
        return text
        
    def verse_splits(self, song_number):
        """
        Because someone at Kingsway forgot to check the 1+2 RTF file, 
        some verses were not formatted correctly.
        """
        if song_number == 11: return 8
        if song_number == 18: return 5
        if song_number == 21: return 6
        if song_number == 23: return 4
        if song_number == 24: return 7
        if song_number == 27: return 4
        if song_number == 31: return 6
        if song_number == 49: return 4
        if song_number == 50: return 8
        if song_number == 70: return 4	
        if song_number == 75: return 8
        if song_number == 79: return 6
        if song_number == 97: return 7
        if song_number == 107: return 4
        if song_number == 109: return 4
        if song_number == 133: return 4
        if song_number == 155: return 10
        if song_number == 156: return 8
        if song_number == 171: return 4
        if song_number == 188: return 7
        if song_number == 192: return 4
        if song_number == 208: return 8
        if song_number == 215: return 8
        if song_number == 220: return 4
        if song_number == 247: return 6
        if song_number == 248: return 6
        if song_number == 251: return 8
        if song_number == 295: return 8
        if song_number == 307: return 5
        if song_number == 314: return 6
        if song_number == 325: return 8
        if song_number == 386: return 6
        if song_number == 415: return 4
        if song_number == 426: return 4
        if song_number == 434: return 5
        if song_number == 437: return 4
        if song_number == 438: return 6
        if song_number == 456: return 8
        if song_number == 461: return 4
        if song_number == 469: return 4
        if song_number == 470: return 5
        if song_number == 476: return 6
        if song_number == 477: return 7
        if song_number == 480: return 8
        if song_number == 482: return 4
        if song_number == 512: return 4
        if song_number == 513: return 8
        if song_number == 518: return 5
        if song_number == 520: return 4
        if song_number == 523: return 6
        if song_number == 526: return 8
        if song_number == 527: return 4
        if song_number == 529: return 4
        if song_number == 537: return 4
        if song_number == 555: return 6
        if song_number == 581: return 4
        if song_number == 589: return 6
        if song_number == 590: return 4
        if song_number == 593: return 8
        if song_number == 596: return 4
        if song_number == 610: return 6
        if song_number == 611: return 6
        if song_number == 619: return 8
        if song_number == 645: return 5
        if song_number == 653: return 6
        if song_number == 683: return 7
        if song_number == 686: return 4
        if song_number == 697: return 8
        if song_number == 698: return 4
        if song_number == 704: return 6
        if song_number == 716: return 4
        if song_number == 717: return 6
        if song_number == 730: return 4
        if song_number == 731: return 8
        if song_number == 732: return 8
        if song_number == 738: return 4
        if song_number == 756: return 9
        if song_number == 815: return 6
        if song_number == 830: return 8
        if song_number == 831: return 4
        if song_number == 876: return 6
        if song_number == 877: return 6
        if song_number == 892: return 4
        if song_number == 894: return 6
        if song_number == 902: return 8
        if song_number == 905: return 8
        if song_number == 921: return 6
        if song_number == 940: return 7
        if song_number == 955: return 9
        if song_number == 968: return 8		
        if song_number == 972: return 7
        if song_number == 974: return 4
        if song_number == 988: return 6
        if song_number == 991: return 5
        if song_number == 1002: return 8
        if song_number == 1024: return 8
        if song_number == 1044: return 9
        if song_number == 1088: return 6
        if song_number == 1117: return 6
        if song_number == 1119: return 7
        return None
                    
