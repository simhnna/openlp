# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2011 Raoul Snyman                                        #
# Portions copyright (c) 2008-2011 Tim Bentley, Gerald Britton, Jonathan      #
# Corwin, Michael Gorven, Scott Guerrieri, Matthias Hub, Meinert Jordan,      #
# Armin Köhler, Joshua Millar, Stevan Pettit, Andreas Preikschat, Mattias     #
# Põldaru, Christian Richter, Philip Ridout, Jeffrey Smith, Maikel            #
# Stuivenberg, Martin Thompson, Jon Tibble, Frode Woldsund                    #
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
The :mod:`settingsform` provides a user interface for the OpenLP settings
"""
import logging

from PyQt4 import QtGui, QtCore

from openlp.core.lib import Receiver, build_icon, PluginStatus
from openlp.core.ui import AdvancedTab, GeneralTab, ThemesTab
from settingsdialog import Ui_SettingsDialog

log = logging.getLogger(__name__)

class SettingsForm(QtGui.QDialog, Ui_SettingsDialog):
    """
    Provide the form to manipulate the settings for OpenLP
    """
    def __init__(self, mainWindow, parent=None):
        """
        Initialise the settings form
        """
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        # General tab
        self.generalTab = GeneralTab(self)
        # Themes tab
        self.themesTab = ThemesTab(self, mainWindow)
        # Advanced tab
        self.advancedTab = AdvancedTab(self)

    def exec_(self):
        # load all the settings
        self.settingListWidget.clear()
        for tabIndex in range(0, self.stackedLayout.count() + 1):
            # take at 0 and the rest shuffell up.
            self.stackedLayout.takeAt(0)
        self.insertTab(self.generalTab, 0, PluginStatus.Active)
        self.insertTab(self.themesTab, 1, PluginStatus.Active)
        self.insertTab(self.advancedTab, 2, PluginStatus.Active)
        count = 3
        for plugin in self.plugins:
            if plugin.settings_tab:
                self.insertTab(plugin.settings_tab, count, plugin.status)
                count += 1
        self.settingListWidget.setCurrentRow(0)
        return QtGui.QDialog.exec_(self)

    def insertTab(self, tab, location, is_active):
        """
        Add a tab to the form at a specific location
        """
        log.debug(u'Inserting %s tab' % tab.tabTitle)
        # add the tab to get it to display in the correct part of the screen
        pos = self.stackedLayout.addWidget(tab)
        if is_active:
            item_name = QtGui.QListWidgetItem(tab.tabTitleVisible)
            icon = build_icon(tab.icon_path)
            item_name.setIcon(icon)
            self.settingListWidget.insertItem(location, item_name)
        else:
            # then remove tab to stop the UI displaying it even if
            # it is not required.
            self.stackedLayout.takeAt(pos)

    def accept(self):
        """
        Process the form saving the settings
        """
        for tabIndex in range(0, self.stackedLayout.count()):
            self.stackedLayout.widget(tabIndex).save()
        # Must go after all settings are save
        Receiver.send_message(u'config_updated')
        return QtGui.QDialog.accept(self)

    def reject(self):
        """
        Process the form saving the settings
        """
        for tabIndex in range(0, self.stackedLayout.count()):
            self.stackedLayout.widget(tabIndex).cancel()
        return QtGui.QDialog.reject(self)

    def postSetUp(self):
        """
        Run any post-setup code for the tabs on the form
        """
        self.generalTab.postSetUp()
        self.themesTab.postSetUp()
        self.advancedTab.postSetUp()
        for plugin in self.plugins:
            if plugin.settings_tab:
                plugin.settings_tab.postSetUp()
