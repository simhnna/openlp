# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2011 Raoul Snyman                                        #
# Portions copyright (c) 2008-2011 Tim Bentley, Jonathan Corwin, Michael      #
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
The :mod:``wizard`` module provides generic wizard tools for OpenLP.
"""
import logging

from PyQt4 import QtCore, QtGui

from openlp.core.lib import build_icon, Receiver

log = logging.getLogger(__name__)

class OpenLPWizard(QtGui.QWizard):
    """
    Generic OpenLP wizard to provide generic functionality and a unified look
    and feel.
    """
    def __init__(self, parent, plugin, name, image):
        QtGui.QWizard.__init__(self, parent)
        self.setObjectName(name)
        self.openIcon = build_icon(u':/general/general_open.png')
        self.deleteIcon = build_icon(u':/general/general_delete.png')
        self.finishButton = self.button(QtGui.QWizard.FinishButton)
        self.cancelButton = self.button(QtGui.QWizard.CancelButton)
        self.setupUi(image)
        self.registerFields()
        self.plugin = plugin
        self.customInit()
        self.customSignals()
        QtCore.QObject.connect(self, QtCore.SIGNAL(u'currentIdChanged(int)'),
            self.onCurrentIdChanged)

    def setupUi(self, image):
        """
        Set up the wizard UI
        """
        self.setModal(True)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setOptions(QtGui.QWizard.IndependentPages |
            QtGui.QWizard.NoBackButtonOnStartPage |
            QtGui.QWizard.NoBackButtonOnLastPage)
        self.addWelcomePage(image)
        self.addCustomPages()
        self.addProgressPage()
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def addWelcomePage(self, image):
        """
        Add the opening welcome page to the wizard.

        ``image``
            A splash image for the wizard
        """
        self.welcomePage = QtGui.QWizardPage()
        self.welcomePage.setPixmap(QtGui.QWizard.WatermarkPixmap,
            QtGui.QPixmap(image))
        self.welcomePage.setObjectName(u'WelcomePage')
        self.welcomeLayout = QtGui.QVBoxLayout(self.welcomePage)
        self.welcomeLayout.setObjectName(u'WelcomeLayout')
        self.titleLabel = QtGui.QLabel(self.welcomePage)
        self.titleLabel.setObjectName(u'TitleLabel')
        self.welcomeLayout.addWidget(self.titleLabel)
        self.welcomeLayout.addSpacing(40)
        self.informationLabel = QtGui.QLabel(self.welcomePage)
        self.informationLabel.setWordWrap(True)
        self.informationLabel.setObjectName(u'InformationLabel')
        self.welcomeLayout.addWidget(self.informationLabel)
        self.welcomeLayout.addStretch()
        self.addPage(self.welcomePage)

    def addProgressPage(self):
        """
        Add the progress page for the wizard. This page informs the user how
        the wizard is progressing with its task.
        """
        self.progressPage = QtGui.QWizardPage()
        self.progressPage.setObjectName(u'progressPage')
        self.progressLayout = QtGui.QVBoxLayout(self.progressPage)
        self.progressLayout.setMargin(48)
        self.progressLayout.setObjectName(u'progressLayout')
        self.progressLabel = QtGui.QLabel(self.progressPage)
        self.progressLabel.setObjectName(u'progressLabel')
        self.progressLayout.addWidget(self.progressLabel)
        self.progressBar = QtGui.QProgressBar(self.progressPage)
        self.progressBar.setObjectName(u'progressBar')
        self.progressLayout.addWidget(self.progressBar)
        self.addPage(self.progressPage)

    def exec_(self):
        """
        Run the wizard.
        """
        self.setDefaults()
        return QtGui.QWizard.exec_(self)

    def reject(self):
        """
        Stop the wizard on cancel button, close button or ESC key.
        """
        log.debug(u'Wizard cancelled by user.')
        if self.currentPage() == self.progressPage:
            Receiver.send_message(u'openlp_stop_wizard')
        self.done(QtGui.QDialog.Rejected)

    def onCurrentIdChanged(self, pageId):
        """
        Perform necessary functions depending on which wizard page is active.
        """
        if self.page(pageId) == self.progressPage:
            self.preWizard()
            self.performWizard()
            self.postWizard()

    def incrementProgressBar(self, status_text, increment=1):
        """
        Update the wizard progress page.

        ``status_text``
            Current status information to display.

        ``increment``
            The value to increment the progress bar by.
        """
        log.debug(u'IncrementBar %s', status_text)
        self.progressLabel.setText(status_text)
        if increment > 0:
            self.progressBar.setValue(self.progressBar.value() + increment)
        Receiver.send_message(u'openlp_process_events')

    def preWizard(self):
        """
        Prepare the UI for the import.
        """
        self.finishButton.setVisible(False)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1188)
        self.progressBar.setValue(0)

    def postWizard(self):
        """
        Clean up the UI after the import has finished.
        """
        self.progressBar.setValue(self.progressBar.maximum())
        self.finishButton.setVisible(True)
        self.cancelButton.setVisible(False)
        Receiver.send_message(u'openlp_process_events')
