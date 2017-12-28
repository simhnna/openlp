# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2017 OpenLP Developers                                   #
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

from PyQt5 import QtCore, QtWidgets

from .mediafilesdialog import Ui_MediaFilesDialog

log = logging.getLogger(__name__)


class MediaFilesForm(QtWidgets.QDialog, Ui_MediaFilesDialog):
    """
    Class to show a list of files from the
    """
    log.info('{name} MediaFilesForm loaded'.format(name=__name__))

    def __init__(self, parent):
        super(MediaFilesForm, self).__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint |
                                             QtCore.Qt.WindowCloseButtonHint)
        self.setupUi(self)

    def populate_files(self, file_paths):
        """
        :param list[openlp.core.common.path.Path] file_paths:
        :return:
        """
        self.file_list_widget.clear()
        for file_path in file_paths:
            item = QtWidgets.QListWidgetItem(file_path.name)
            item.setData(QtCore.Qt.UserRole, file_path)
            self.file_list_widget.addItem(item)

    def get_selected_files(self):
        """
        :rtype: list[openlp.core.common.path.Path]
        """
        return [item.data(QtCore.Qt.UserRole) for item in self.file_list_widget.selectedItems()]
