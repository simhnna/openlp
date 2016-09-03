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
The :mod:`db` module provides the ability to provide a csv file of all songs
"""
import logging
import os

from PyQt5 import QtWidgets

from openlp.core.common import Registry, check_directory_exists, translate
from openlp.core.lib.ui import critical_error_message_box
from openlp.plugins.songs.lib.db import Song


log = logging.getLogger(__name__)


def report_song_list():
    """
    Export the song list as a CSV file.
    :return: Nothing
    """
    main_window = Registry().get('main_window')
    plugin = Registry().get('songs').plugin
    path = QtWidgets.QFileDialog.getExistingDirectory(
        main_window, translate('SongPlugin.ReportSongList', 'Output File Location'))
    if not path:
        main_window.error_message(
            translate('SongPlugin.ReportSongList', 'Output Path Not Selected'),
            translate('SongPlugin.ReportSongList', 'You have not set a valid output location for your'
                                                   'report. \nPlease select an existing path '
                                                   'on your computer.')
        )
        return
    check_directory_exists(path)
    report_file_name = os.path.join(path, 'song_index.csv')
    file_handle = None
    try:
        file_handle = open(report_file_name, 'wb')
        song_list = plugin.manager.get_all_objects(Song)
        for song in song_list:
            record = '\"{title}\",'.format(title=song.title)
            record += '\"{title}\",'.format(title=song.alternate_title)
            record += '\"{title}\",'.format(title=song.copyright)
            author_list = []
            for author_song in song.authors_songs:
                author_list.append(author_song.author.display_name)
            author_string = '\"{name}\"'.format(name=' | '.join(author_list))
            book_list = []
            for book_song in song.songbook_entries:
                if hasattr(book_song, 'entry') and book_song.entry:
                    book_list.append('{name} #{entry}'.format(name=book_song.songbook.name, entry=book_song.entry))
            book_string = '\"{name}\"'.format(name=' | '.join(book_list))
            topic_list = []
            for topic_song in song.topics:
                if hasattr(topic_song, 'name'):
                    topic_list.append(topic_song.name)
            topic_string = '\"{name}\"'.format(name=' | '.join(topic_list))
            record += '{title},'.format(title=author_string)
            record += '{title},'.format(title=book_string)
            record += '{title},'.format(title=topic_string)
            record += '\n'
            file_handle.write(record.encode('utf-8'))
        main_window.information_message(
            translate('SongPlugin.ReportSongList', 'Report Creation'),
            translate('SongPlugin.ReportSongList',
                      'Report \n{name} \nhas been successfully created. ').format(name=report_file_name)
        )
    except OSError as ose:
        log.exception('Failed to write out song usage records')
        critical_error_message_box(translate('SongPlugin.ReportSongList', 'Song Extraction Failed'),
                                   translate('SongPlugin.ReportSongList',
                                             'An error occurred while extracting: {error}'
                                             ).format(error=ose.strerror))
    finally:
        if file_handle:
            file_handle.close()
