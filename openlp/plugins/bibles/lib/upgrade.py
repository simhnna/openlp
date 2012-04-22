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
The :mod:`upgrade` module provides a way for the database and schema that is the
backend for the Bibles plugin
"""

from sqlalchemy import Table, select, update, insert, or_

__version__ = 1

def upgrade_setup(metadata):
    """
    Set up the latest revision all tables, with reflection, needed for the
    upgrade process. If you want to drop a table, you need to remove it from
    here, and add it to your upgrade function.
    """
    # Don't define the "metadata" table, as the upgrade mechanism already
    # defines it.
    tables = {
        u'book': Table(u'book', metadata, autoload=True),
        u'verse': Table(u'verse', metadata, autoload=True)
    }
    return tables


def upgrade_1(session, metadata, tables):
    """
    Version 1 upgrade.

    This upgrade renames a number of keys to a single naming convention..
    """
    metadata_table = metadata.tables[u'metadata']
    # Rename "Bookname language" to "book_name_language"
    session.execute(update(metadata_table)\
        .where(or_(metadata_table.c.key == u'bookname language',
        metadata_table.c.key == u'Bookname language'))\
        .values(key=u'book_name_language'))
    # Copy "Copyright" to "copyright"
    # TODO: Clean up in a subsequent release of OpenLP (like 2.0 final)
    session.execute(insert(metadata_table).values(
        key=u'copyright',
        value=select(metadata_table, metadata_table.c.key == u'Copyright')\
            .as_scalar()
    ))
    # Copy "Version" to "name" ("version" used by upgrade system)
    # TODO: Clean up in a subsequent release of OpenLP (like 2.0 final)
    session.execute(insert(metadata_table).values(
        key=u'name',
        value=select(metadata_table, metadata_table.c.key == u'Version')\
            .as_scalar()
    ))
    # Copy "Permissions" to "permissions"
    # TODO: Clean up in a subsequent release of OpenLP (like 2.0 final)
    session.execute(insert(metadata_table).values(
        key=u'permissions',
        value=select(metadata_table, metadata_table.c.key == u'Permissions')\
            .as_scalar()
    ))
    session.execute(update(metadata_table)\
        .where(metadata_table.c.key == u'download source')\
        .values(key=u'download_source'))
    session.execute(update(metadata_table)\
        .where(metadata_table.c.key == u'download name')\
        .values(key=u'download_name'))
    session.execute(update(metadata_table)\
        .where(metadata_table.c.key == u'proxy server')\
        .values(key=u'proxy_server'))
    session.execute(update(metadata_table)\
        .where(metadata_table.c.key == u'proxy username')\
        .values(key=u'proxy_username'))
    session.execute(update(metadata_table)\
        .where(metadata_table.c.key == u'proxy password')\
        .values(key=u'proxy_password'))
    # TODO: Clean up in a subsequent release of OpenLP (like 2.0 final)
    #session.execute(delete(metadata_table)\
    #    .where(metadata_table.c.key == u'dbversion'))
    session.commit()
