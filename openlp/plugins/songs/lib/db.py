# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2011 Raoul Snyman                                        #
# Portions copyright (c) 2008-2011 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Meinert Jordan, Andreas Preikschat, Christian      #
# Richter, Philip Ridout, Maikel Stuivenberg, Martin Thompson, Jon Tibble,    #
# Carsten Tinggaard, Frode Woldsund                                           #
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
The :mod:`db` module provides the database and schema that is the backend for
the Songs plugin
"""

from sqlalchemy import Column, ForeignKey, Index, Table, types
from sqlalchemy.orm import mapper, relation

from openlp.core.lib.db import BaseModel, init_db

class Author(BaseModel):
    """
    Author model
    """
    pass


class Book(BaseModel):
    """
    Book model
    """
    def __repr__(self):
        return u'<Book id="%s" name="%s" publisher="%s" />' % (
            str(self.id), self.name, self.publisher)


class MediaFile(BaseModel):
    """
    MediaFile model
    """
    pass


class Song(BaseModel):
    """
    Song model
    """
    pass


class Topic(BaseModel):
    """
    Topic model
    """
    pass


def init_schema(url):
    """
    Setup the songs database connection and initialise the database schema.

    ``url``
        The database to setup

    The song database contains the following tables:
        * authors
        * authors_songs
        * media_files
        * media_files_songs
        * song_books
        * songs
        * songs_topics
        * topics

        *authors* Table
        ---------------
        This table holds the names of all the authors. It has the following
        columns:
        * id
        * first_name
        * last_name
        * display_name

        *authors_songs* Table
        ---------------------
        This is a bridging table between the *authors* and *songs* tables, which
        serves to create a many-to-many relationship between the two tables. It
        has the following columns:
        * author_id
        * song_id

        *media_files* Table
        -------------------
        * id
        * file_name
        * type

        *media_files_songs* Table
        -------------------------
        * media_file_id
        * song_id

        *song_books* Table
        ------------------
        The *song_books* table holds a list of books that a congregation gets
        their songs from, or old hymnals now no longer used. This table has the
        following columns:
        * id
        * name
        * publisher

        *songs* Table
        -------------
        This table contains the songs, and each song has a list of attributes.
        The *songs* table has the following columns:
        * id
        * song_book_id
        * title
        * alternate_title
        * lyrics
        * verse_order
        * copyright
        * comments
        * ccli_number
        * song_number
        * theme_name
        * search_title
        * search_lyrics

        *songs_topics* Table
        --------------------
        This is a bridging table between the *songs* and *topics* tables, which
        serves to create a many-to-many relationship between the two tables. It
        has the following columns:
        * song_id
        * topic_id

        *topics* Table
        --------------
        The topics table holds a selection of topics that songs can cover. This
        is useful when a worship leader wants to select songs with a certain
        theme. This table has the following columns:
        * id
        * name
    """
    session, metadata = init_db(url)

    # Definition of the "authors" table
    authors_table = Table(u'authors', metadata,
        Column(u'id', types.Integer, primary_key=True),
        Column(u'first_name', types.Unicode(128)),
        Column(u'last_name', types.Unicode(128)),
        Column(u'display_name', types.Unicode(255), nullable=False)
    )

    # Definition of the "media_files" table
    media_files_table = Table(u'media_files', metadata,
        Column(u'id', types.Integer, primary_key=True),
        Column(u'file_name', types.Unicode(255), nullable=False),
        Column(u'type', types.Unicode(64), nullable=False, default=u'audio')
    )

    # Definition of the "song_books" table
    song_books_table = Table(u'song_books', metadata,
        Column(u'id', types.Integer, primary_key=True),
        Column(u'name', types.Unicode(128), nullable=False),
        Column(u'publisher', types.Unicode(128))
    )

    # Definition of the "songs" table
    songs_table = Table(u'songs', metadata,
        Column(u'id', types.Integer, primary_key=True),
        Column(u'song_book_id', types.Integer,
            ForeignKey(u'song_books.id'), default=0),
        Column(u'title', types.Unicode(255), nullable=False),
        Column(u'alternate_title', types.Unicode(255)),
        Column(u'lyrics', types.UnicodeText, nullable=False),
        Column(u'verse_order', types.Unicode(128)),
        Column(u'copyright', types.Unicode(255)),
        Column(u'comments', types.UnicodeText),
        Column(u'ccli_number', types.Unicode(64)),
        Column(u'song_number', types.Unicode(64)),
        Column(u'theme_name', types.Unicode(128)),
        Column(u'search_title', types.Unicode(255), index=True, nullable=False),
        Column(u'search_lyrics', types.UnicodeText, index=True, nullable=False)
    )

    # Definition of the "topics" table
    topics_table = Table(u'topics', metadata,
        Column(u'id', types.Integer, primary_key=True),
        Column(u'name', types.Unicode(128), nullable=False)
    )

    # Definition of the "authors_songs" table
    authors_songs_table = Table(u'authors_songs', metadata,
        Column(u'author_id', types.Integer,
            ForeignKey(u'authors.id'), primary_key=True),
        Column(u'song_id', types.Integer,
            ForeignKey(u'songs.id'), primary_key=True)
    )

    # Definition of the "media_files_songs" table
    media_files_songs_table = Table(u'media_files_songs', metadata,
        Column(u'media_file_id', types.Integer,
            ForeignKey(u'media_files.id'), primary_key=True),
        Column(u'song_id', types.Integer,
            ForeignKey(u'songs.id'), primary_key=True)
    )

    # Definition of the "songs_topics" table
    songs_topics_table = Table(u'songs_topics', metadata,
        Column(u'song_id', types.Integer,
            ForeignKey(u'songs.id'), primary_key=True),
        Column(u'topic_id', types.Integer,
            ForeignKey(u'topics.id'), primary_key=True)
    )

    # Define table indexes
    Index(u'authors_id', authors_table.c.id)
    Index(u'authors_display_name_id', authors_table.c.display_name,
        authors_table.c.id)
    Index(u'media_files_id', media_files_table.c.id)
    Index(u'song_books_id', song_books_table.c.id)
    Index(u'songs_id', songs_table.c.id)
    Index(u'topics_id', topics_table.c.id)
    Index(u'authors_songs_author', authors_songs_table.c.author_id,
        authors_songs_table.c.song_id)
    Index(u'authors_songs_song', authors_songs_table.c.song_id,
        authors_songs_table.c.author_id)
    Index(u'media_files_songs_file', media_files_songs_table.c.media_file_id,
        media_files_songs_table.c.song_id)
    Index(u'media_files_songs_song', media_files_songs_table.c.song_id,
        media_files_songs_table.c.media_file_id)
    Index(u'topics_song_topic', songs_topics_table.c.topic_id,
        songs_topics_table.c.song_id)
    Index(u'topics_song_song', songs_topics_table.c.song_id,
        songs_topics_table.c.topic_id)

    mapper(Author, authors_table)
    mapper(Book, song_books_table)
    mapper(MediaFile, media_files_table)
    mapper(Song, songs_table,
        properties={
            'authors': relation(Author, backref='songs',
                secondary=authors_songs_table),
            'book': relation(Book, backref='songs'),
            'media_files': relation(MediaFile, backref='songs',
                secondary=media_files_songs_table),
            'topics': relation(Topic, backref='songs',
                secondary=songs_topics_table)
        })
    mapper(Topic, topics_table)

    metadata.create_all(checkfirst=True)
    return session
