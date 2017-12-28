# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2017 OpenLP Developers                                   #
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
The :mod:`openlyricsexport` module provides the functionality for exporting songs from the database to the OpenLyrics
format.
"""
import logging

from lxml import etree

from openlp.core.common import clean_filename
from openlp.core.common.i18n import translate
from openlp.core.common.mixins import RegistryProperties
from openlp.core.common.path import create_paths
from openlp.plugins.songs.lib.openlyricsxml import OpenLyrics

log = logging.getLogger(__name__)


class OpenLyricsExport(RegistryProperties):
    """
    This provides the Openlyrics export.
    """
    def __init__(self, parent, songs, save_path):
        """
        Initialise the export.

        :param openlp.core.common.path.Path save_path: The directory to save the exported songs in
        :rtype: None
        """
        log.debug('initialise OpenLyricsExport')
        self.parent = parent
        self.manager = parent.plugin.manager
        self.songs = songs
        self.save_path = save_path
        create_paths(self.save_path)

    def do_export(self):
        """
        Export the songs.
        """
        log.debug('started OpenLyricsExport')
        open_lyrics = OpenLyrics(self.manager)
        self.parent.progress_bar.setMaximum(len(self.songs))
        for song in self.songs:
            self.application.process_events()
            if self.parent.stop_export_flag:
                return False
            self.parent.increment_progress_bar(
                translate('SongsPlugin.OpenLyricsExport', 'Exporting "{title}"...').format(title=song.title))
            xml = open_lyrics.song_to_xml(song)
            tree = etree.ElementTree(etree.fromstring(xml.encode()))
            filename = '{title} ({author})'.format(title=song.title,
                                                   author=', '.join([author.display_name for author in song.authors]))
            filename = clean_filename(filename)
            # Ensure the filename isn't too long for some filesystems
            path_length = len(str(self.save_path))
            filename_with_ext = '{name}.xml'.format(name=filename[0:250 - path_length])
            # Make sure we're not overwriting an existing file
            conflicts = 0
            while (self.save_path / filename_with_ext).exists():
                conflicts += 1
                filename_with_ext = '{name}-{extra}.xml'.format(name=filename[0:247 - path_length], extra=conflicts)
            # Pass a file object, because lxml does not cope with some special
            # characters in the path (see lp:757673 and lp:744337).
            with (self.save_path / filename_with_ext).open('wb') as out_file:
                tree.write(out_file, encoding='utf-8', xml_declaration=True, pretty_print=True)
        return True
