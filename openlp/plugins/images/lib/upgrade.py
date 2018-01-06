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
The :mod:`upgrade` module provides the migration path for the OLP Paths database
"""
import json
import logging

from sqlalchemy import Column, Table

from openlp.core.common.applocation import AppLocation
from openlp.core.common.db import drop_columns
from openlp.core.common.json import OpenLPJsonEncoder
from openlp.core.common.path import Path
from openlp.core.lib.db import PathType, get_upgrade_op

log = logging.getLogger(__name__)
__version__ = 2


def upgrade_1(session, metadata):
    """
    Version 1 upgrade - old db might/might not be versioned.
    """
    log.debug('Skipping upgrade_1 of files DB - not used')


def upgrade_2(session, metadata):
    """
    Version 2 upgrade - Move file path from old db to JSON encoded path to new db. Added during 2.5 dev
    """
    log.debug('Starting upgrade_2 for file_path to JSON')
    old_table = Table('image_filenames', metadata, autoload=True)
    if 'file_path' not in [col.name for col in old_table.c.values()]:
        op = get_upgrade_op(session)
        op.add_column('image_filenames', Column('file_path', PathType()))
        conn = op.get_bind()
        results = conn.execute('SELECT * FROM image_filenames')
        data_path = AppLocation.get_data_path()
        for row in results.fetchall():
            file_path_json = json.dumps(Path(row.filename), cls=OpenLPJsonEncoder, base_path=data_path)
            sql = 'UPDATE image_filenames SET file_path = \'{file_path_json}\' WHERE id = {id}'.format(
                file_path_json=file_path_json, id=row.id)
            conn.execute(sql)
        # Drop old columns
        if metadata.bind.url.get_dialect().name == 'sqlite':
            drop_columns(op, 'image_filenames', ['filename', ])
        else:
            op.drop_constraint('image_filenames', 'foreignkey')
            op.drop_column('image_filenames', 'filenames')
