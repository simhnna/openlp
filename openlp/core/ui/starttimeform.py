# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2011 Raoul Snyman                                        #
# Portions copyright (c) 2008-2011 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Meinert Jordan, Armin Köhler, Andreas Preikschat,  #
# Christian Richter, Philip Ridout, Maikel Stuivenberg, Martin Thompson, Jon  #
# Tibble, Carsten Tinggaard, Frode Woldsund                                   #
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

from PyQt4 import QtGui

from starttimedialog import Ui_StartTimeDialog
from openlp.core.lib.ui import UiStrings

class StartTimeForm(QtGui.QDialog, Ui_StartTimeDialog):
    """
    The exception dialog
    """
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def exec_(self):
        """
        Run the Dialog with correct heading.
        """
        hour, minutes, seconds = self._time_split(
            self.item[u'service_item'].start_time)
        self.hourSpinBox.setValue(hour)
        self.minuteSpinBox.setValue(minutes)
        self.secondSpinBox.setValue(seconds)
        hours, minutes, seconds = self._time_split(
            self.item[u'service_item'].media_length)
        self.hourFinishSpinBox.setValue(hours)
        self.minuteFinishSpinBox.setValue(minutes)
        self.secondFinishSpinBox.setValue(seconds)
        self.hourFinishLabel.setText(u'%s%s' % (unicode(hour), UiStrings.H))
        self.minuteFinishLabel.setText(u'%s%s' %
            (unicode(minutes), UiStrings.M))
        self.secondFinishLabel.setText(u'%s%s' %
            (unicode(seconds), UiStrings.S))
        return QtGui.QDialog.exec_(self)

    def accept(self):
        return QtGui.QDialog.accept(self)

    def _time_split(self, seconds):
        hours = seconds / 3600
        seconds -= 3600 * hours
        minutes = seconds / 60
        seconds -= 60 * minutes
        return hours, minutes, seconds

