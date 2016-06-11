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

from openlp.core.api import OpenWSServer, OpenLPPoll, OpenLPHttpServer
from openlp.core.common import OpenLPMixin, Registry, RegistryMixin, RegistryProperties

# These are here to load the endpoints
from openlp.core.api.coreendpoints import stage_endpoint
from openlp.core.api.controllerendpoints import controller_endpoint

log = logging.getLogger(__name__)


class ApiController(RegistryMixin, OpenLPMixin, RegistryProperties):
    """
    The implementation of the Media Controller. The Media Controller adds an own class for every Player.
    Currently these are QtWebkit, Phonon and Vlc. display_controllers are an array of controllers keyed on the
    slidecontroller or plugin which built them.

    ControllerType is the class containing the key values.

    media_players are an array of media players keyed on player name.

    current_media_players is an array of player instances keyed on ControllerType.

    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(ApiController, self).__init__(parent)
        print("apic")

    def bootstrap_post_set_up(self):
        """
        process the bootstrap post setup request
        """
        self.poll = OpenLPPoll()
        Registry().register('OpenLPPoll', self.poll)
        self.wsserver = OpenWSServer()
        self.httpserver = OpenLPHttpServer()
