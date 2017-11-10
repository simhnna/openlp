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
    :mod:`openlp.core.ui.projector`

    Initialization for the openlp.core.ui.projector modules.
"""

__all__ = ['PJLINK_PORT', 'ERROR_MSG', 'ERROR_STRING', 'DialogSourceStyle', 'PJLink', 'Projector',
           'ProjectorDB', 'ProjectorEditForm', 'ProjectorManager', 'ProjectorTab']


# Due to circular dependencies, put the imports after defines
class DialogSourceStyle(object):
    """
    An enumeration for projector dialog box type.
    """
    Tabbed = 0
    Single = 1


from .constants import PJLINK_PORT, ERROR_MSG, ERROR_STRING
from .db import Projector, ProjectorDB
from .editform import ProjectorEditForm
from .manager import ProjectorManager
from .pjlink import PJLink
from .tab import ProjectorTab
