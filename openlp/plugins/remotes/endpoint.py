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
import logging

import os

from openlp.core.api.http.endpoint import Endpoint
from openlp.core.api.endpoint.core import TRANSLATED_STRINGS
from openlp.core.common import AppLocation


static_dir = os.path.join(AppLocation.get_section_data_path('remotes'))

log = logging.getLogger(__name__)

remote_endpoint = Endpoint('remote', template_dir=static_dir, static_dir=static_dir)


@remote_endpoint.route('{view}')
def index(request, view):
    """
    Handles requests for /remotes url

    :param request: The http request object.
    :param view: The view name to be servered.
    """
    return remote_endpoint.render_template('{view}.mako'.format(view=view), **TRANSLATED_STRINGS)
