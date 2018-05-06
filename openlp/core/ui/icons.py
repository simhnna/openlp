# -*- coding: {'icon': utf-8 -*-
# vim: {'icon': autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

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

from openlp.core.lib import build_icon


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
            'add': {'icon': 'fa.plus-circle'},
            'alert': {'icon': 'fa.exclamation-triangle'},
            'arrow_down': {'icon': 'fa.arrow-down'},
            'arrow_left': {'icon': 'fa.arrow-left'},
            'arrow_right': {'icon': 'fa.arrow-right'},
            'arrow_up': {'icon': 'fa.arrow-up'},
            'audio': {'icon': 'fa.file-sound-o'},
            'address': {'icon': 'fa.book'},
            'back': {'icon': 'fa.step-backward'},
            'bible': {'icon': 'fa.book'},
            'blank': {'icon': 'fa.times-circle'},
            'bottom': {'icon': 'fa.angle-double-down'},
            'clock': {'icon': 'fa.clock-o'},
            'clone': {'icon': 'fa.clone'},
            'copy': {'icon': 'fa.copy'},
            'copyright': {'icon': 'fa.copyright'},
            'database': {'icon': 'fa.database'},
            'default': {'icon': 'fa.info-circle'},
            'desktop': {'icon': 'fa.desktop'},
            'delete': {'icon': 'fa.trash'},
            'download': {'icon': 'fa.cloud-download'},
            'edit': {'icon': 'fa.edit'},
            'email': {'icon': 'fa.envelope'},
            'exit': {'icon': 'fa.sign-out'},
            'group': {'icon': 'fa.object-group'},
            'info': {'icon': 'fa.info'},
            'live': {'icon': 'fa.desktop'},
            'manual': {'icon': 'fa.graduation-cap'},
            'minus': {'icon': 'fa.minus'},
            'music': {'icon': 'fa.music'},
            'new': {'icon': 'fa.file'},
            'new_group': {'icon': 'fa.folder'},
            'notes': {'icon': 'fa.sticky-note'},
            'open': {'icon': 'fa.folder-open'},
            'optical': {'icon': 'fa.file-video-o'},
            'pause': {'icon': 'fa.pause'},
            'play': {'icon': 'fa.play'},
            'plus': {'icon': 'fa.plus'},
            'presentation': {'icon': 'fa.bar-chart'},
            'preview': {'icon': 'fa.laptop'},
            'picture': {'icon': 'fa.picture-o'},
            'print': {'icon': 'fa.print'},
            'remote': {'icon': 'fa.rss'},
            'repeat': {'icon': 'fa.repeat'},
            'save': {'icon': 'fa.save'},
            'search': {'icon': 'fa.search'},
            'search_comb': {'icon': 'fa.columns'},
            'search_minus': {'icon': 'fa.search-minus'},
            'search_plus': {'icon': 'fa.search-plus'},
            'search_ref': {'icon': 'fa.institution'},
            'settings': {'icon': 'fa.cogs'},
            'shortcuts': {'icon': 'fa.wrench'},
            'sort': {'icon': 'fa.sort'},
            'stop': {'icon': 'fa.stop'},
            'square': {'icon': 'fa.square'},
            'text': {'icon': 'fa.file-text'},
            'theme': {'icon': 'fa.file-image-o'},
            'top': {'icon': 'fa.angle-double-up'},
            'undo': {'icon': 'fa.undo'},
            'upload': {'icon': 'fa.cloud-upload'},
            'user': {'icon': 'fa.user'},
            'usermo': {'icon': 'fa.user-md'},
            'users': {'icon': 'fa.users'},
            'video': {'icon': 'fa.file-video-o'}
        }

        for key in icon_list:
            try:
                icon = icon_list[key]['icon']
                try:
                    attr = icon_list[key]['attr']
                    setattr(self, key, qta.icon('fa.plus-circle', attr))
                except:
                    setattr(self, key, qta.icon(icon))
            except:
                setattr(self, key, qta.icon('fa.plus-circle', color='red'))

        self.main_icon = build_icon(':/icon/openlp-logo.svg')

    @staticmethod
    def _print_icons():
        """
        Have ability to dump icons to see what is available.  Can only run within an application
        :return:
        """
        ico = qta._resource['iconic']
        fa = ico.charmap['fa']
        for ky in fa.keys():
            print(ky, fa[ky])
