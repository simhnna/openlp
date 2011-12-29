# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2012 Raoul Snyman                                        #
# Portions copyright (c) 2008-2012 Tim Bentley, Gerald Britton, Jonathan      #
# Corwin, Michael Gorven, Scott Guerrieri, Matthias Hub, Meinert Jordan,      #
# Armin Köhler, Joshua Miller, Stevan Pettit, Andreas Preikschat, Mattias     #
# Põldaru, Christian Richter, Philip Ridout, Simon Scudder, Jeffrey Smith,    #
# Maikel Stuivenberg, Martin Thompson, Jon Tibble, Frode Woldsund             #
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
The :mod:`wowimport` module provides the functionality for importing Words of
Worship songs into the OpenLP database.
"""
import os
import logging

from openlp.plugins.songs.lib.songimport import SongImport

BLOCK_TYPES = (u'V', u'C', u'B')

log = logging.getLogger(__name__)

class WowImport(SongImport):
    """
    The :class:`WowImport` class provides the ability to import song files from
    Words of Worship.

    **Words Of Worship Song File Format:**

    The Words Of Worship song file format is as follows:

    * The song title is the file name minus the extension.
    * The song has a header, a number of blocks, followed by footer containing
      the author and the copyright.
    * A block can be a verse, chorus or bridge.

    File Header:
        Bytes are counted from one, i.e. the first byte is byte 1. These bytes,
        up to the 56 byte, can change but no real meaning has been found. The
        56th byte specifies how many blocks there are. The first block starts
        with byte 83 after the "CSongDoc::CBlock" declaration.

    Blocks:
        Each block has a starting header, some lines of text, and an ending
        footer. Each block starts with 4 bytes, the first byte specifies how
        many lines are in that block, the next three bytes are null bytes.

        Each block ends with 4 bytes, the first of which defines what type of
        block it is, and the rest which are null bytes:

        * ``NUL`` (0x00) - Verse
        * ``SOH`` (0x01) - Chorus
        * ``STX`` (0x02) - Bridge

        Blocks are seperated by two bytes. The first byte is 0x01, and the
        second byte is 0x80.

    Lines:
        Each line starts with a byte which specifies how long that line is,
        the line text, and ends with a null byte.


    Footer:
        The footer follows on after the last block, the first byte specifies
        the length of the author text, followed by the author text, if
        this byte is null, then there is no author text. The byte after the
        author text specifies the length of the copyright text, followed
        by the copyright text.

        The file is ended with four null bytes.

    Valid extensions for a Words of Worship song file are:

    * .wsg
    * .wow-song
    """

    def __init__(self, manager, **kwargs):
        """
        Initialise the Words of Worship importer.
        """
        SongImport.__init__(self, manager, **kwargs)

    def doImport(self):
        """
        Receive a single file or a list of files to import.
        """
        if isinstance(self.importSource, list):
            self.importWizard.progressBar.setMaximum(len(self.importSource))
            for file in self.importSource:
                if self.stopImportFlag:
                    return
                file_name = os.path.split(file)[1]
                # Get the song title
                self.title = file_name.rpartition(u'.')[0]
                song_data = open(file, 'rb')
                if song_data.read(19) != u'WoW File\nSong Words':
                    self.logError(file)
                    continue
                # Seek to byte which stores number of blocks in the song
                song_data.seek(56)
                no_of_blocks = ord(song_data.read(1))
                # Seek to the beging of the first block
                song_data.seek(82)
                for block in range(no_of_blocks):
                    self.linesToRead = ord(song_data.read(1))
                    # Skip 3 nulls to the beginnig of the 1st line
                    song_data.seek(3, os.SEEK_CUR)
                    block_text = u''
                    while self.linesToRead:
                        self.lineText = unicode(
                            song_data.read(ord(song_data.read(1))), u'cp1252')
                        song_data.seek(1, os.SEEK_CUR)
                        if block_text:
                            block_text += u'\n'
                        block_text += self.lineText
                        self.linesToRead -= 1
                    block_type = BLOCK_TYPES[ord(song_data.read(1))]
                    # Skip 3 nulls at the end of the block
                    song_data.seek(3, os.SEEK_CUR)
                    # Blocks are seperated by 2 bytes, skip them, but not if
                    # this is the last block!
                    if block + 1 < no_of_blocks:
                        song_data.seek(2, os.SEEK_CUR)
                    self.addVerse(block_text, block_type)
                # Now to extract the author
                author_length = ord(song_data.read(1))
                if author_length:
                    self.parseAuthor(
                        unicode(song_data.read(author_length), u'cp1252'))
                # Finally the copyright
                copyright_length = ord(song_data.read(1))
                if copyright_length:
                    self.addCopyright(unicode(
                        song_data.read(copyright_length), u'cp1252'))
                song_data.close()
                if not self.finish():
                    self.logError(file)
