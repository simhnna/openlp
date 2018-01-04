# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2018 OpenLP Developers                                   #
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
backend for the SongsUsage plugin
"""
import logging

from sqlalchemy import Table, Column, types

from openlp.core.lib.db import get_upgrade_op

log = logging.getLogger(__name__)
__version__ = 2


def upgrade_1(session, metadata):
    """
    Version 1 upgrade

    Skip due to possible missed update from a 2.4-2.6 upgrade
    """
    pass


def upgrade_2(session, metadata):
    """
    Version 2 upgrade.

    This upgrade adds two new fields to the songusage database

    :param session: SQLAlchemy Session object
    :param metadata: SQLAlchemy MetaData object
    """
    op = get_upgrade_op(session)
    songusage_table = Table('songusage_data', metadata, autoload=True)
    if 'plugin_name' not in [col.name for col in songusage_table.c.values()]:
        op.add_column('songusage_data', Column('plugin_name', types.Unicode(20), server_default=''))
        op.add_column('songusage_data', Column('source', types.Unicode(10), server_default=''))
