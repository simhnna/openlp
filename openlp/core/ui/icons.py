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
            cls.load(cls)
        return cls.__instance__

    def load(self):
        """
        These are the font icons used in the code.
        """
        palette = QtWidgets.QApplication.palette()
        qta.set_defaults(color=palette.color(QtGui.QPalette.Active,
                                             QtGui.QPalette.ButtonText),
                         color_disabled=palette.color(QtGui.QPalette.Disabled,
                                                      QtGui.QPalette.ButtonText))
        icon_list = {
            'add': 'fa.plus-circle',
            'arrow_down': 'fa.arrow-down',
            'arrow_left': 'fa.arrow-left',
            'arrow_right': 'fa.arrow-right',
            'arrow_up': 'fa.arrow-up',
            'address': 'fa.book',
            'bible': 'fa.book',
            'blank': 'fa.times-circle',
            'bottom': 'fa.angle-double-down',
            'clock': 'fa.clock-o',
            'clone': 'fa.clone',
            'copy': 'fa.copy',
            'copyright': 'fa.copyright',
            'database': 'fa.database',
            'default': 'fa.info-circle',
            'desktop': 'fa.desktop',
            'delete': 'fa.trash',
            'edit': 'fa.edit',
            'exit': 'fa.sign-out',
            'download': 'fa.cloud-download',
            'live': 'fa.camera',
            'minus': 'fa.minus',
            'music': 'fa.music',
            'new': 'fa.file',
            'notes': 'fa.sticky-note',
            'open': 'fa.map',
            'pause': 'fa.pause',
            'play': 'fa.play',
            'plus': 'fa.plus',
            'presentation': 'fa.bar-chart',
            'preview': 'fa.laptop',
            'picture': 'fa.picture-o',
            'print': 'fa.print',
            'remote': 'fa.rss',
            'save': 'fa.save',
            'settings': 'fa.cogs',
            'stop': 'fa.stop',
            'theme': 'fa.file-image-o',
            'top': 'fa.angle-double-up',
            'upload': 'fa.cloud-upload',
            'user': 'fa.user',
            'video': 'fa.file-video-o'
        }

        for key in icon_list:
            try:
                setattr(self, key, qta.icon(icon_list[key]))
            except:
                setattr(self, key, qta.icon('fa.plus-circle', color='red'))

    @staticmethod
    def _print_icons():
        """
        Have ability to dump icons to see what is available
        :return:
        """
        ico = qta._resource['iconic']
        fa = ico.charmap['fa']
        for ky in fa.keys():
            print(ky, fa[ky])
