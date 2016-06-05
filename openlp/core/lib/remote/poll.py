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

import json

from openlp.core.common import RegistryProperties, Settings, OpenLPMixin


class OpenLPPoll(RegistryProperties):
    """
    Access by the web layer to get status type information from the application
    """
    def __init__(self):
        """
        Constructor for the poll builder class.
        """
        super(OpenLPPoll, self).__init__()

    def poll(self):
        """
        Poll OpenLP to determine the current slide number and item name.
        """
        result = {
            'service': self.service_manager.service_id,
            'slide': self.live_controller.selected_row or 0,
            'item': self.live_controller.service_item.unique_identifier if self.live_controller.service_item else '',
            'twelve': Settings().value('remotes/twelve hour'),
            'blank': self.live_controller.blank_screen.isChecked(),
            'theme': self.live_controller.theme_screen.isChecked(),
            'display': self.live_controller.desktop_screen.isChecked(),
            'version': 2,
            'isSecure': Settings().value('remotes/authentication enabled'),
            'isAuthorised': False
        }
        return json.dumps({'results': result}).encode()

    def main_poll(self):
        """
        Poll OpenLP to determine the current slide count.
        """
        result = {
            'slide_count': self.live_controller.slide_count
        }
        return json.dumps({'results': result}).encode()
