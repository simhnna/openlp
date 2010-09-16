# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2010 Raoul Snyman                                        #
# Portions copyright (c) 2008-2010 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Meinert Jordan, Andreas Preikschat, Christian      #
# Richter, Philip Ridout, Maikel Stuivenberg, Martin Thompson, Jon Tibble,    #
# Carsten Tinggaard, Frode Woldsund                                           #
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

from openlp.core.lib import Plugin, StringContent, translate, build_icon
from openlp.plugins.remotes.lib import RemoteTab, HttpServer

log = logging.getLogger(__name__)

class RemotesPlugin(Plugin):
    log.info(u'Remote Plugin loaded')

    def __init__(self, plugin_helpers):
        """
        remotes constructor
        """
        Plugin.__init__(self, u'Remotes', u'1.9.2', plugin_helpers)
        self.icon = build_icon(u':/plugins/plugin_remote.png')
        self.weight = -1
        self.server = None

    def initialise(self):
        """
        Initialise the remotes plugin, and start the http server
        """
        log.debug(u'initialise')
        Plugin.initialise(self)
        self.insertToolboxItem()
        self.server = HttpServer(self)

    def finalise(self):
        """
        Tidy up and close down the http server
        """
        log.debug(u'finalise')
        Plugin.finalise(self)
        if self.server:
            self.server.close()

    def getSettingsTab(self):
        """
        Create the settings Tab
        """
        visible_name = self.getString(StringContent.VisibleName)
        return RemoteTab(self.name, visible_name[u'title'])

    def about(self):
        """
        Information about this plugin
        """
        about_text = translate('RemotePlugin', '<strong>Remote Plugin</strong>'
            '<br />The remote plugin provides the ability to send messages to '
            'a running version of OpenLP on a different computer via a web '
            'browser or through the remote API.')
        return about_text
    
    def setPluginStrings(self):
        """
        Called to define all translatable texts of the plugin
        """
        ## Name PluginList ##
        self.strings[StringContent.Name] = {
            u'singular': translate('RemotePlugin', 'Remote'),
            u'plural': translate('RemotePlugin', 'Remotes')
        }
        ## Name for MediaDockManager, SettingsManager ##
        self.strings[StringContent.VisibleName] = {
            u'title': translate('RemotePlugin', 'Remotes')
        }