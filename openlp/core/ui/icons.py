# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2018 OpenLP Developers                                   #
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
The :mod:`languages` module provides a list of icons.
"""
import qtawesome as qta

from PyQt5 import QtGui, QtWidgets


class UiIcons(object):
    """
    Provide standard icons for objects to use.
    """
    __instance__ = None

    def __new__(cls):
        """
        Override the default object creation method to return a single instance.
        """
        if not cls.__instance__:
            cls.__instance__ = object.__new__(cls)
        return cls.__instance__

    def __init__(self):
        """
        These are the font icons used in the code.
        """
        palette = QtWidgets.QApplication.palette()
        qta.set_defaults(color=palette.color(QtGui.QPalette.Active,
                                             QtGui.QPalette.ButtonText),
                         color_disabled=palette.color(QtGui.QPalette.Disabled,
                                                      QtGui.QPalette.ButtonText))
        self.add = qta.icon('fa.plus-circle')
        self.arrow_down = qta.icon('fa.arrow-down')
        self.arrow_up = qta.icon('fa.arrow-up')
        self.address = qta.icon('fa.book')
        self.bible = qta.icon('fa.book')
        self.bottom = qta.icon('fa.angle-double-down')
        self.clone = qta.icon('fa.clone')
        self.copy = qta.icon('fa.copy')
        self.copyright = qta.icon('fa.copyright')
        self.database = qta.icon('fa.database')
        self.default = qta.icon('fa.info-circle')
        self.delete = qta.icon('fa.trash')
        self.edit = qta.icon('fa.edit')
        self.exit = qta.icon('fa.sign-out')
        self.download = qta.icon('fa.cloud-download')
        self.live = qta.icon('fa.camera')
        self.minus = qta.icon('fa.minus')
        self.music = qta.icon('fa.music')
        self.new = qta.icon('fa.file')
        self.notes = qta.icon('fa.sticky-note')
        self.open = qta.icon('fa.map')
        self.plus = qta.icon('fa.plus')
        self.presentation = qta.icon("fa.bar-chart")
        self.preview = qta.icon('fa.laptop')
        self.picture = qta.icon("fa.picture-o")
        self.print = qta.icon('fa.print')
        #self.remote = qta.icon('fa.podcast')
        self.save = qta.icon('fa.save')
        self.settings = qta.icon('fa.cogs')
        self.top = qta.icon('fa.angle-double-up')
        self.upload = qta.icon('fa.cloud-upload')
        self.user = qta.icon('fa.user')
        self.video = qta.icon('fa.file-video-o')
