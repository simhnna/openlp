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
"""
The :mod:`chordpro` module provides the functionality for importing
ChordPro files into the current database.
"""

import logging

from .songimport import SongImport


log = logging.getLogger(__name__)


class ChordProImport(SongImport):
    """
    The :class:`ChordProImport` class provides OpenLP with the
    ability to import ChordPro files.
    This importer is based on the information available on these webpages:
    http://webchord.sourceforge.net/tech.html
    http://www.vromans.org/johan/projects/Chordii/chordpro/
    http://www.tenbyten.com/software/songsgen/help/HtmlHelp/files_reference.htm
    http://linkesoft.com/songbook/chordproformat.html
    """
    def do_import(self):
        self.import_wizard.progress_bar.setMaximum(len(self.import_source))
        for filename in self.import_source:
            if self.stop_import_flag:
                return
            song_file = open(filename, 'rt')
            self.do_import_file(song_file)
            song_file.close()

    def do_import_file(self, song_file):
        """
        Imports the songs in the given file
        :param song_file: The file object to be imported from.
        """
        self.set_defaults()
        # Loop over the lines of the file
        file_content = song_file.read()
        current_verse = ''
        current_verse_type = 'v'
        skip_block = False
        for line in file_content.splitlines():
            line = line.rstrip()
            # Detect tags
            if line.startswith('{'):
                tag_name, tag_value = self.parse_tag(line)
                # Detect which tag
                if tag_name in ['title', 't']:
                    self.title = tag_value
                elif tag_name in ['subtitle', 'su', 'st']:
                    self.alternate_title = tag_value
                elif tag_name in ['comment', 'c', 'comment_italic', 'ci', 'comment_box', 'cb']:
                    # Detect if the comment is used as a chorus repeat marker
                    if tag_value.lower().startswith('chorus'):
                        if current_verse.strip():
                            # Add collected verse to the lyrics
                            self.add_verse(current_verse.rstrip(), current_verse_type)
                            current_verse_type = 'v'
                            current_verse = ''
                        self.repeat_verse('c1')
                    else:
                        self.add_comment(tag_value)
                elif tag_name in ['start_of_chorus', 'soc']:
                    current_verse_type = 'c'
                elif tag_name in ['end_of_chorus', 'eoc']:
                    # Add collected chorus to the lyrics
                    self.add_verse(current_verse.rstrip(), current_verse_type)
                    current_verse_type = 'v'
                    current_verse = ''
                elif tag_name in ['start_of_tab', 'sot']:
                    if current_verse.strip():
                        # Add collected verse to the lyrics
                        self.add_verse(current_verse.rstrip(), current_verse_type)
                        current_verse_type = 'v'
                        current_verse = ''
                    skip_block = True
                elif tag_name in ['end_of_tab', 'eot']:
                    skip_block = False
                elif tag_name in ['new_song', 'ns']:
                    # A new song starts below this tag
                    if self.verses and self.title:
                        if current_verse.strip():
                            self.add_verse(current_verse.rstrip(), current_verse_type)
                        if not self.finish():
                            self.log_error(song_file.name)
                    self.set_defaults()
                    current_verse_type = 'v'
                    current_verse = ''
                else:
                    # Unsupported tag
                    log.debug('unsupported tag: %s' % line)
            elif line.startswith('#'):
                # Found a comment line, which is ignored...
                continue
            elif line == "['|]":
                # Found a vertical bar
                continue
            else:
                if skip_block:
                    continue
                elif line == '' and current_verse.strip() and current_verse_type != 'c':
                    # Add collected verse to the lyrics
                    self.add_verse(current_verse.rstrip(), current_verse_type)
                    current_verse_type = 'v'
                    current_verse = ''
                else:
                    if current_verse.strip() == '':
                        current_verse = line + '\n'
                    else:
                        current_verse += line + '\n'
        if current_verse.strip():
            self.add_verse(current_verse.rstrip(), current_verse_type)
        if not self.finish():
            self.log_error(song_file.name)

    def parse_tag(self, line):
        """
        :param line: Line with the tag to be parsed
        :return: A tuple with tag name and tag value (if any)
        """
        # Strip the first '}'
        line = line[1:].strip()
        colon_idx = line.find(':')
        # check if this is a tag without value
        if colon_idx < 0:
            # strip the final '}' and return the tag name
            return line[:-1], None
        tag_name = line[:colon_idx]
        tag_value = line[colon_idx + 1:-1].strip()
        return tag_name, tag_value
