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

from PyQt4 import QtCore, QtGui

class SplashScreen(object):
    def __init__(self, version):
        self.splash_screen = QtGui.QSplashScreen()
        self.setupUi()

    def setupUi(self):
        self.splash_screen.setObjectName(u'splash_screen')
        self.splash_screen.setWindowModality(QtCore.Qt.NonModal)
        self.splash_screen.setEnabled(True)
        self.splash_screen.resize(370, 370)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.splash_screen.sizePolicy().hasHeightForWidth())
        self.splash_screen.setSizePolicy(sizePolicy)
        self.splash_screen.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)
        splash_image = QtGui.QPixmap(u':/graphics/openlp-splash-screen.png')
        self.splash_screen.setPixmap(splash_image)
        self.splash_screen.setMask(splash_image.mask())
        self.splash_screen.setWindowFlags(
            QtCore.Qt.SplashScreen | QtCore.Qt.WindowStaysOnTopHint)
        QtCore.QMetaObject.connectSlotsByName(self.splash_screen)

    def show(self):
        self.splash_screen.show()

    def finish(self, widget):
        self.splash_screen.finish(widget)
