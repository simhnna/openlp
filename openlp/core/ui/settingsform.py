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
"""
The :mod:`settingsform` provides a user interface for the OpenLP settings
"""
import logging

from PyQt4 import QtGui

from openlp.core.lib import Receiver
from openlp.core.ui import AdvancedTab, GeneralTab, ThemesTab
from settingsdialog import Ui_SettingsDialog

log = logging.getLogger(__name__)

class SettingsForm(QtGui.QDialog, Ui_SettingsDialog):
    """
    Provide the form to manipulate the settings for OpenLP
    """
    def __init__(self, screens, mainWindow, parent=None):
        """
        Initialise the settings form
        """
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        # General tab
        self.generalTab = GeneralTab(screens)
        self.addTab(u'General', self.generalTab)
        # Themes tab
        self.themesTab = ThemesTab(mainWindow)
        self.addTab(u'Themes', self.themesTab)
        # Advanced tab
        self.advancedTab = AdvancedTab()
        self.addTab(u'Advanced', self.advancedTab)

    def addTab(self, name, tab):
        """
        Add a tab to the form
        """
        log.info(u'Adding %s tab' % tab.tabTitle)
        self.settingsTabWidget.addTab(tab, tab.tabTitleVisible)

    def insertTab(self, tab, location):
        """
        Add a tab to the form at a specific location
        """
        log.debug(u'Inserting %s tab' % tab.tabTitle)
        # 14 : There are 3 tables currently and locations starts at -10
        self.settingsTabWidget.insertTab(
            location + 14, tab, tab.tabTitleVisible)

    def removeTab(self, name):
        """
        Remove a tab from the form
        """
        log.debug(u'remove %s tab' % name)
        for tabIndex in range(0, self.settingsTabWidget.count()):
            if self.settingsTabWidget.widget(tabIndex):
                if self.settingsTabWidget.widget(tabIndex).tabTitle == name:
                    self.settingsTabWidget.removeTab(tabIndex)

    def accept(self):
        """
        Process the form saving the settings
        """
        for tabIndex in range(0, self.settingsTabWidget.count()):
            self.settingsTabWidget.widget(tabIndex).save()
        # Must go after all settings are save
        Receiver.send_message(u'config_updated')
        return QtGui.QDialog.accept(self)

    def postSetUp(self):
        """
        Run any post-setup code for the tabs on the form
        """
        for tabIndex in range(0, self.settingsTabWidget.count()):
            self.settingsTabWidget.widget(tabIndex).postSetUp()
