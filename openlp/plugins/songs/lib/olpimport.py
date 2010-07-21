# -*- coding: utf-8 -*-
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
"""
The :mod:`olpimport` module provides the functionality for importing OpenLP
song databases into the current installation database.
"""
import logging

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import class_mapper, mapper, relation, scoped_session, \
    sessionmaker
from sqlalchemy.orm.exc import UnmappedClassError

from openlp.core.lib.db import BaseModel
from openlp.plugins.songs.lib.db import Author, Book, Song, Topic #, MediaFile

log = logging.getLogger(__name__)

class OldAuthor(BaseModel):
    """
    Author model
    """
    pass

class OldBook(BaseModel):
    """
    Book model
    """
    pass

class OldMediaFile(BaseModel):
    """
    MediaFile model
    """
    pass

class OldSong(BaseModel):
    """
    Song model
    """
    pass

class OldTopic(BaseModel):
    """
    Topic model
    """
    pass

class OpenLPSongImport(object):
    """

    """
    def __init__(self, master_manager, source_db):
        """

        """
        self.master_manager = master_manager
        self.import_source = source_db
        self.source_session = None

    def import_source_v2_db(self):
        """

        """
        engine = create_engine(self.import_source)
        source_meta = MetaData()
        source_meta.reflect(engine)
        self.source_session = scoped_session(sessionmaker(bind=engine))
        if u'media_files' in source_meta.tables.keys():
            has_media_files = True
        else:
            has_media_files = False
        source_authors_table = source_meta.tables[u'authors']
        source_song_books_table = source_meta.tables[u'song_books']
        source_songs_table = source_meta.tables[u'songs']
        source_topics_table = source_meta.tables[u'topics']
        source_authors_songs_table = source_meta.tables[u'authors_songs']
        source_songs_topics_table = source_meta.tables[u'songs_topics']
        if has_media_files:
            source_media_files_table = source_meta.tables[u'media_files']
            source_media_files_songs_table = \
                source_meta.tables[u'media_files_songs']
            try:
                class_mapper(OldMediaFile)
            except UnmappedClassError:
                mapper(OldMediaFile, source_media_files_table)
        song_props = {
            'authors': relation(OldAuthor, backref='songs',
                secondary=source_authors_songs_table),
            'book': relation(OldBook, backref='songs'),
            'topics': relation(OldTopic, backref='songs',
                secondary=source_songs_topics_table)
        }
        if has_media_files:
            song_props['media_files'] = relation(OldMediaFile, backref='songs',
                secondary=source_media_files_songs_table)
        try:
            class_mapper(OldAuthor)
        except UnmappedClassError:
            mapper(OldAuthor, source_authors_table)
        try:
            class_mapper(OldBook)
        except UnmappedClassError:
            mapper(OldBook, source_song_books_table)
        try:
            class_mapper(OldSong)
        except UnmappedClassError:
            mapper(OldSong, source_songs_table, properties=song_props)
        try:
            class_mapper(OldTopic)
        except UnmappedClassError:
            mapper(OldTopic, source_topics_table)

        source_songs = self.source_session.query(OldSong).all()
        for song in source_songs:
            new_song = Song()
            new_song.title = song.title
            if has_media_files:
                new_song.alternate_title = song.alternate_title
            else:
                new_song.alternate_title = u''
            new_song.search_title = song.search_title
            new_song.song_number = song.song_number
            new_song.lyrics = song.lyrics
            new_song.search_lyrics = song.search_lyrics
            new_song.verse_order = song.verse_order
            new_song.copyright = song.copyright
            new_song.comments = song.comments
            new_song.theme_name = song.theme_name
            new_song.ccli_number = song.ccli_number
            if song.authors:
                for author in song.authors:
                    existing_author = self.master_manager.get_object_filtered(
                        Author, Author.display_name == author.display_name)
                    if existing_author:
                        new_song.authors.append(existing_author)
                    else:
                        new_song.authors.append(Author.populate(
                            first_name=author.first_name,
                            last_name=author.last_name,
                            display_name=author.display_name))
            else:
                au = self.master_manager.get_object_filtered(Author,
                    Author.display_name == u'Author Unknown')
                if au:
                    new_song.authors.append(au)
                else:
                    new_song.authors.append(Author.populate(
                        display_name=u'Author Unknown'))
            if song.book:
                existing_song_book = self.master_manager.get_object_filtered(
                    Book, Book.name == song.book.name)
                if existing_song_book:
                    new_song.book = existing_song_book
                else:
                    new_song.book = Book.populate(name=song.book.name,
                        publisher=song.book.publisher)
            if song.topics:
                for topic in song.topics:
                    existing_topic = self.master_manager.get_object_filtered(
                        Topic, Topic.name == topic.name)
                    if existing_topic:
                        new_song.topics.append(existing_topic)
                    else:
                        new_song.topics.append(Topic.populate(name=topic.name))
#            if has_media_files:
#                if song.media_files:
#                    for media_file in song.media_files:
#                        existing_media_file = \
#                            self.master_manager.get_object_filtered(MediaFile,
#                                MediaFile.file_name == media_file.file_name)
#                        if existing_media_file:
#                            new_song.media_files.append(existing_media_file)
#                        else:
#                            new_song.media_files.append(MediaFile.populate(
#                                file_name=media_file.file_name))
            self.master_manager.save_object(new_song)
        engine.dispose()
