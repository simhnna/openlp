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

import os
from openlp.core.common import AppLocation


def get_cert_file(file_type):
    """
    Helper method to get certificate files
    :param file_type: file suffix key, cert or pem
    :return: full path to file
    """
    local_data = AppLocation.get_directory(AppLocation.DataDir)
    return os.path.join(local_data, 'remotes', 'openlp.{type}'.format(type=file_type))


from .poll import OpenLPPoll
from .wsserver import OpenWSServer
from .remotecontroller import RemoteController

__all__ = ['OpenLPPoll', 'RemoteController', 'get_cert_file']
