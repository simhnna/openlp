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

from PyQt4 import QtCore, QtGui

from openlp.core.lib import PluginStatus, StringContent, translate
from plugindialog import Ui_PluginViewDialog

log = logging.getLogger(__name__)

class PluginForm(QtGui.QDialog, Ui_PluginViewDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.activePlugin = None
        self.programaticChange = False
        self.setupUi(self)
        self.load()
        self._clearDetails()
        # Right, now let's put some signals and slots together!
        QtCore.QObject.connect(
            self.pluginListWidget,
            QtCore.SIGNAL(u'itemSelectionChanged()'),
            self.onPluginListWidgetSelectionChanged)
        QtCore.QObject.connect(
            self.statusComboBox,
            QtCore.SIGNAL(u'currentIndexChanged(int)'),
            self.onStatusComboBoxChanged)

    def load(self):
        """
        Load the plugin details into the screen
        """
        self.pluginListWidget.clear()
        self.programaticChange = True
        self._clearDetails()
        self.programaticChange = True
        for plugin in self.parent.pluginManager.plugins:
            item = QtGui.QListWidgetItem(self.pluginListWidget)
            # We do this just to make 100% sure the status is an integer as
            # sometimes when it's loaded from the config, it isn't cast to int.
            plugin.status = int(plugin.status)
            # Set the little status text in brackets next to the plugin name.
            status_text = unicode(
                translate('OpenLP.PluginForm', '%s (Inactive)'))
            if plugin.status == PluginStatus.Active:
                status_text = unicode(
                    translate('OpenLP.PluginForm', '%s (Active)'))
            elif plugin.status == PluginStatus.Inactive:
                status_text = unicode(
                    translate('OpenLP.PluginForm', '%s (Inactive)'))
            elif plugin.status == PluginStatus.Disabled:
                status_text = unicode(
                    translate('OpenLP.PluginForm', '%s (Disabled)'))
            name_string = plugin.getString(StringContent.Name)
            item.setText(status_text % name_string[u'plural'])
            # If the plugin has an icon, set it!
            if plugin.icon:
                item.setIcon(plugin.icon)
            self.pluginListWidget.addItem(item)

    def _clearDetails(self):
        self.statusComboBox.setCurrentIndex(-1)
        self.versionNumberLabel.setText(u'')
        self.aboutTextBrowser.setHtml(u'')
        self.statusComboBox.setEnabled(False)

    def _setDetails(self):
        log.debug('PluginStatus: %s', str(self.activePlugin.status))
        self.versionNumberLabel.setText(self.activePlugin.version)
        self.aboutTextBrowser.setHtml(self.activePlugin.about())
        self.programaticChange = True
        status = 1
        if self.activePlugin.status == PluginStatus.Active:
            status = 0
        self.statusComboBox.setCurrentIndex(status)
        self.statusComboBox.setEnabled(True)
        self.programaticChange = False

    def onPluginListWidgetSelectionChanged(self):
        if self.pluginListWidget.currentItem() is None:
            self._clearDetails()
            return
        plugin_name_plural = \
            self.pluginListWidget.currentItem().text().split(u' ')[0]
        self.activePlugin = None
        for plugin in self.parent.pluginManager.plugins:
            name_string = plugin.getString(StringContent.Name)
            if name_string[u'plural'] == plugin_name_plural:
                self.activePlugin = plugin
                break
        if self.activePlugin:
            self._setDetails()
        else:
            self._clearDetails()

    def onStatusComboBoxChanged(self, status):
        if self.programaticChange:
            return
        if status == 0:
            self.activePlugin.toggleStatus(PluginStatus.Active)
        else:
            self.activePlugin.toggleStatus(PluginStatus.Inactive)
        status_text = unicode(
            translate('OpenLP.PluginForm', '%s (Inactive)'))
        if self.activePlugin.status == PluginStatus.Active:
            status_text = unicode(
                translate('OpenLP.PluginForm', '%s (Active)'))
        elif self.activePlugin.status == PluginStatus.Inactive:
            status_text = unicode(
                translate('OpenLP.PluginForm', '%s (Inactive)'))
        elif self.activePlugin.status == PluginStatus.Disabled:
            status_text = unicode(
                translate('OpenLP.PluginForm', '%s (Disabled)'))
        name_string = self.activePlugin.getString(StringContent.Name)
        self.pluginListWidget.currentItem().setText(
            status_text % name_string[u'plural'])
