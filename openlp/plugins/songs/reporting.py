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
import csv
import logging

from PyQt5 import QtWidgets

from openlp.core.common import Registry, translate
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
    report_file_name, filter_used = QtWidgets.QFileDialog.getSaveFileName(
        main_window,
        translate('SongPlugin.ReportSongList', 'Save File'),
        translate('SongPlugin.ReportSongList', 'song_extract.csv'),
        translate('SongPlugin.ReportSongList', 'CSV format (*.csv)'))

    if not report_file_name:
        main_window.error_message(
            translate('SongPlugin.ReportSongList', 'Output Path Not Selected'),
            translate('SongPlugin.ReportSongList', 'You have not set a valid output location for your '
                                                   'report. \nPlease select an existing path '
                                                   'on your computer.')
        )
        return
    if not report_file_name.endswith('csv'):
        report_file_name += '.csv'
    file_handle = None
    Registry().get('application').set_busy_cursor()
    try:
        file_handle = open(report_file_name, 'wt')
        fieldnames = ('Title', 'Alternative Title', 'Copyright', 'Author(s)', 'Song Book', 'Topic')
        writer = csv.DictWriter(file_handle, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        headers = dict((n, n) for n in fieldnames)
        writer.writerow(headers)
        song_list = plugin.manager.get_all_objects(Song)
        for song in song_list:
            author_list = []
            for author_song in song.authors_songs:
                author_list.append(author_song.author.display_name)
            author_string = ' | '.join(author_list)
            book_list = []
            for book_song in song.songbook_entries:
                if hasattr(book_song, 'entry') and book_song.entry:
                    book_list.append('{name} #{entry}'.format(name=book_song.songbook.name, entry=book_song.entry))
            book_string = ' | '.join(book_list)
            topic_list = []
            for topic_song in song.topics:
                if hasattr(topic_song, 'name'):
                    topic_list.append(topic_song.name)
            topic_string = ' | '.join(topic_list)
            writer.writerow({'Title': song.title,
                             'Alternative Title': song.alternate_title,
                             'Copyright': song.copyright,
                             'Author(s)': author_string,
                             'Song Book': book_string,
                             'Topic': topic_string})
        Registry().get('application').set_normal_cursor()
        main_window.information_message(
            translate('SongPlugin.ReportSongList', 'Report Creation'),
            translate('SongPlugin.ReportSongList',
                      'Report \n{name} \nhas been successfully created. ').format(name=report_file_name)
        )
    except OSError as ose:
        Registry().get('application').set_normal_cursor()
        log.exception('Failed to write out song usage records')
        critical_error_message_box(translate('SongPlugin.ReportSongList', 'Song Extraction Failed'),
                                   translate('SongPlugin.ReportSongList',
                                             'An error occurred while extracting: {error}'
                                             ).format(error=ose.strerror))
    finally:
        if file_handle:
            file_handle.close()
