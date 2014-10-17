# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2014 Raoul Snyman                                        #
# Portions copyright (c) 2008-2014 Tim Bentley, Gerald Britton, Jonathan      #
# Corwin, Samuel Findlay, Michael Gorven, Scott Guerrieri, Matthias Hub,      #
# Meinert Jordan, Armin Köhler, Erik Lundin, Edwin Lunando, Brian T. Meyer.   #
# Joshua Miller, Stevan Pettit, Andreas Preikschat, Mattias Põldaru,          #
# Christian Richter, Philip Ridout, Ken Roberts, Simon Scudder,               #
# Jeffrey Smith, Maikel Stuivenberg, Martin Thompson, Jon Tibble,             #
# Dave Warnock, Frode Woldsund, Martin Zibricky, Patrick Zimmermann           #
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
    :mod:`openlp.core.ui.projector.tab`

    Provides the settings tab in the settings dialog.
"""

import logging
log = logging.getLogger(__name__)
log.debug('projectortab module loaded')

from PyQt4 import QtCore, QtGui

from openlp.core.common import Settings, UiStrings, translate
from openlp.core.lib import SettingsTab


class ProjectorTab(SettingsTab):
    """
    Openlp Settings -> Projector settings
    """
    def __init__(self, parent):
        """
        ProjectorTab initialization

        :param parent: Parent widget
        """
        self.icon_path = ':/projector/projector_manager.png'
        projector_translated = translate('OpenLP.ProjectorTab', 'Projector')
        super(ProjectorTab, self).__init__(parent, 'Projector', projector_translated)

    def setupUi(self):
        """
        Setup the UI
        """
        self.setObjectName('ProjectorTab')
        super(ProjectorTab, self).setupUi()
        self.connect_box = QtGui.QGroupBox(self.left_column)
        self.connect_box.setObjectName('connect_box')
        self.connect_box_layout = QtGui.QFormLayout(self.connect_box)
        self.connect_box_layout.setObjectName('connect_box_layout')

        # Start comms with projectors on startup
        self.connect_on_startup = QtGui.QCheckBox(self.connect_box)
        self.connect_on_startup.setObjectName('connect_on_startup')
        self.connect_box_layout.addRow(self.connect_on_startup)
        # Socket timeout
        self.socket_timeout_label = QtGui.QLabel(self.connect_box)
        self.socket_timeout_label.setObjectName('socket_timeout_label')
        self.socket_timeout_spin_box = QtGui.QSpinBox(self.connect_box)
        self.socket_timeout_spin_box.setObjectName('socket_timeout_spin_box')
        self.socket_timeout_spin_box.setMinimum(2)
        self.socket_timeout_spin_box.setMaximum(10)
        self.connect_box_layout.addRow(self.socket_timeout_label, self.socket_timeout_spin_box)
        # Poll interval
        self.socket_poll_label = QtGui.QLabel(self.connect_box)
        self.socket_poll_label.setObjectName('socket_poll.label')
        self.socket_poll_spin_box = QtGui.QSpinBox(self.connect_box)
        self.socket_poll_spin_box.setObjectName('socket_timeout_spin_box')
        self.socket_poll_spin_box.setMinimum(5)
        self.socket_poll_spin_box.setMaximum(60)
        self.connect_box_layout.addRow(self.socket_poll_label, self.socket_poll_spin_box)

        self.left_layout.addWidget(self.connect_box)

        self.left_layout.addStretch()

    def retranslateUi(self):
        """
        Translate the UI on the fly
        """
        self.tab_title_visible = UiStrings().Projectors
        self.connect_box.setTitle(
            translate('OpenLP.ProjectorTab', 'Communication Options'))
        self.connect_on_startup.setText(
            translate('OpenLP.ProjectorTab', 'Connect to projectors on startup'))
        self.socket_timeout_label.setText(
            translate('OpenLP.ProjectorTab', 'Socket timeout (seconds)'))
        self.socket_poll_label.setText(
            translate('OpenLP.ProjectorTab', 'Poll time (seconds)'))

    def load(self):
        """
        Load the projetor settings on startup
        """
        settings = Settings()
        settings.beginGroup(self.settings_section)
        self.connect_on_startup.setChecked(settings.value('connect on start'))
        self.socket_timeout_spin_box.setValue(settings.value('socket timeout'))
        self.socket_poll_spin_box.setValue(settings.value('poll time'))
        settings.endGroup()

    def save(self):
        """
        Save the projector settings
        """
        settings = Settings()
        settings.beginGroup(self.settings_section)
        settings.setValue('connect on start', self.connect_on_startup.isChecked())
        settings.setValue('socket timeout', self.socket_timeout_spin_box.value())
        settings.setValue('poll time', self.socket_poll_spin_box.value())
        settings.endGroup
