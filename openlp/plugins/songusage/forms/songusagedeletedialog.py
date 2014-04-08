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
# Christian Richter, Philip Ridout, Simon Scudder, Jeffrey Smith,             #
# Maikel Stuivenberg, Martin Thompson, Jon Tibble, Dave Warnock,              #
# Frode Woldsund, Martin Zibricky, Patrick Zimmermann                         #
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

from PyQt4 import QtCore, QtGui

from openlp.core.common import translate
from openlp.core.lib.ui import create_button_box


class Ui_SongUsageDeleteDialog(object):
    """
    The Song Usage delete dialog
    """
    def setupUi(self, song_usage_delete_dialog):
        """
        Setup the UI

        :param song_usage_delete_dialog:
        """
        song_usage_delete_dialog.setObjectName('song_usage_delete_dialog')
        song_usage_delete_dialog.resize(291, 243)
        self.vertical_layout = QtGui.QVBoxLayout(song_usage_delete_dialog)
        self.vertical_layout.setSpacing(8)
        self.vertical_layout.setContentsMargins(8, 8, 8, 8)
        self.vertical_layout.setObjectName('vertical_layout')
        self.delete_label = QtGui.QLabel(song_usage_delete_dialog)
        self.delete_label.setObjectName('delete_label')
        self.vertical_layout.addWidget(self.delete_label)
        self.delete_calendar = QtGui.QCalendarWidget(song_usage_delete_dialog)
        self.delete_calendar.setFirstDayOfWeek(QtCore.Qt.Sunday)
        self.delete_calendar.setGridVisible(True)
        self.delete_calendar.setVerticalHeaderFormat(QtGui.QCalendarWidget.NoVerticalHeader)
        self.delete_calendar.setObjectName('delete_calendar')
        self.vertical_layout.addWidget(self.delete_calendar)
        self.button_box = create_button_box(song_usage_delete_dialog, 'button_box', ['cancel', 'ok'])
        self.vertical_layout.addWidget(self.button_box)
        self.retranslateUi(song_usage_delete_dialog)

    def retranslateUi(self, song_usage_delete_dialog):
        """
        Retranslate the strings
        :param song_usage_delete_dialog:
        """
        song_usage_delete_dialog.setWindowTitle(
            translate('SongUsagePlugin.SongUsageDeleteForm', 'Delete Song Usage Data'))
        self.delete_label.setText(
            translate('SongUsagePlugin.SongUsageDeleteForm', 'Select the date up to which the song usage data '
                      'should be deleted. \nAll data recorded before this date will be permanently deleted.'))
