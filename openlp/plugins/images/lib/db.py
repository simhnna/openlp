# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2014 Raoul Snyman                                        #
# Portions copyright (c) 2008-2014 Tim Bentley, Gerald Britton, Jonathan      #
# Corwin, Samuel Findlay, Michael Gorven, Scott Guerrieri, Matthias Hub,      #
# Meinert Jordan, Armin Köhler, Erik Lundin, Edwin Lunando, Brian T. Meyer.   #
# Joshua Miller, Stevan Pettit, Andreas Preikschat, Mattias Põldaru,          #
# Christian Richter, Philip Ridout, Simon Scudder, Jeffrey Smith,             #
# Maikel Stuivenberg, Martin Thompson, Jon Tibble, Dave Warnock,              #
# Frode Woldsund, Martin Zibricky, Patrick Zimmermann                         #
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
The :mod:`db` module provides the database and schema that is the backend for the Images plugin.
"""

from sqlalchemy import Column, ForeignKey, Table, types
from sqlalchemy.orm import mapper, relation, reconstructor

from openlp.core.lib.db import BaseModel, init_db


class ImageGroups(BaseModel):
    """
    ImageGroups model.
    """
    pass


class ImageFilenames(BaseModel):
    """
    ImageFilenames model.
    """
    pass


def init_schema(url):
    """
    Setup the images database connection and initialise the database schema.

    ``url``
        The database to setup

    The images database contains the following tables:

        * image_groups
        * image_filenames

    **image_groups Table**
        This table holds the names of the images groups. It has the following columns:

        * id
        * parent_id
        * group_name

    **image_filenames Table**
        This table holds the filenames of the images and the group they belong to. It has the following columns:

        * id
        * group_id
        * filename
    """
    session, metadata = init_db(url)

    # Definition of the "image_groups" table
    image_groups_table = Table('image_groups', metadata,
                               Column('id', types.Integer(), primary_key=True),
                               Column('parent_id', types.Integer()),
                               Column('group_name', types.Unicode(128))
                               )

    # Definition of the "image_filenames" table
    image_filenames_table = Table('image_filenames', metadata,
                                  Column('id', types.Integer(), primary_key=True),
                                  Column('group_id', types.Integer(), ForeignKey('image_groups.id'), default=None),
                                  Column('filename', types.Unicode(255), nullable=False)
                                  )

    mapper(ImageGroups, image_groups_table)
    mapper(ImageFilenames, image_filenames_table)

    metadata.create_all(checkfirst=True)
    return session
