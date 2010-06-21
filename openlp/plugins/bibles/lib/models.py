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

from sqlalchemy import Column, Table, MetaData, ForeignKey, types, \
    create_engine
from sqlalchemy.orm import mapper, relation, sessionmaker, scoped_session

from openlp.core.lib import BaseModel


class BibleMeta(BaseModel):
    """
    Bible Meta Data
    """
    pass


class Testament(BaseModel):
    """
    Bible Testaments
    """
    pass


class Book(BaseModel):
    """
    Song model
    """
    pass


class Verse(BaseModel):
    """
    Topic model
    """
    pass

def init_models(db_url):
    engine = create_engine(db_url)
    metadata.bind = engine
    session = scoped_session(sessionmaker(autoflush=True, autocommit=False,
        bind=engine))
    return session

metadata = MetaData()
meta_table = Table(u'metadata', metadata,
    Column(u'key', types.Unicode(255), primary_key=True, index=True),
    Column(u'value', types.Unicode(255)),
)
testament_table = Table(u'testament', metadata,
    Column(u'id', types.Integer, primary_key=True),
    Column(u'name', types.Unicode(50)),
)
book_table = Table(u'book', metadata,
    Column(u'id', types.Integer, primary_key=True),
    Column(u'testament_id', types.Integer, ForeignKey(u'testament.id')),
    Column(u'name', types.Unicode(50), index=True),
    Column(u'abbreviation', types.Unicode(5), index=True),
)
verse_table = Table(u'verse', metadata,
   Column(u'id', types.Integer, primary_key=True, index=True),
    Column(u'book_id', types.Integer, ForeignKey(u'book.id'), index=True),
    Column(u'chapter', types.Integer, index=True),
    Column(u'verse', types.Integer, index=True),
    Column(u'text', types.UnicodeText, index=True),
)
mapper(BibleMeta, meta_table)
mapper(Testament, testament_table,
    properties={'books': relation(Book, backref='testament')})
mapper(Book, book_table,
    properties={'verses': relation(Verse, backref='book')})
mapper(Verse, verse_table)
