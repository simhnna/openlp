# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2016 OpenLP Developers                                   #
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

from PyQt5 import QtGui, QtWidgets

from openlp.core.common import Settings, UiStrings, translate
from openlp.core.lib import SettingsTab
from openlp.core.lib.ui import create_valign_selection_widgets
from openlp.core.ui.lib.colorbutton import ColorButton


class RemotesTab(SettingsTab):
    """
    Remotes is the alerts settings tab in the settings dialog.
    """
    def __init__(self, parent, name, visible_title, icon_path):
        super(RemotesTab, self).__init__(parent, name, visible_title, icon_path)

    def setupUi(self):
        self.setObjectName('Remotes')
        super(RemotesTab, self).setupUi()
        self.web_group_box = QtWidgets.QGroupBox(self.left_column)
        self.web_group_box.setObjectName('web_group_box')
        self.web_layout = QtWidgets.QFormLayout(self.web_group_box)
        self.web_layout.setObjectName('web_layout')

        self.web_color_label = QtWidgets.QLabel(self.web_group_box)
        self.web_color_label.setObjectName('font_color_label')
        self.color_layout = QtWidgets.QHBoxLayout()
        self.color_layout.setObjectName('color_layout')
        self.web_color_button = ColorButton(self.web_group_box)
        self.web_color_button.setObjectName('font_color_button')
        self.color_layout.addWidget(self.web_color_button)
        self.color_layout.addSpacing(20)

        self.left_layout.addWidget(self.web_group_box)
        self.left_layout.addStretch()
        # Signals and slots
        #self.background_color_button.colorChanged.connect(self.on_background_color_changed)
        #self.web_color_button.colorChanged.connect(self.on_font_color_changed)
        #self.web_combo_box.activated.connect(self.on_font_combo_box_clicked)

    def retranslateUi(self):
        self.web_group_box.setTitle(translate('RemotePlugin.Interface', 'Web Interface'))
        #self.web_label.setText(translate('RemotePlugin.Remotes', 'Font name:'))
        self.web_color_label.setText(translate('AlertsPlugin.Remotes', 'Font color:'))
        #self.background_color_label.setText(UiStrings().BackgroundColorColon)

    def load(self):
        """
        Load the settings into the UI.
        """
        pass

    def save(self):
        """
        Save the changes on exit of the Settings dialog.
        """
        settings = Settings()
        settings.beginGroup(self.settings_section)
        # Check value has changed as no event handles this field
        if settings.value('location') != self.vertical_combo_box.currentIndex():
            self.changed = True
        settings.setValue('background color', self.background_color)
        settings.setValue('font color', self.web_color)
        settings.setValue('font size', self.web_size)
        self.web_face = self.web_combo_box.currentFont().family()
        settings.setValue('font face', self.web_face)
        settings.setValue('timeout', self.timeout)
        self.location = self.vertical_combo_box.currentIndex()
        settings.setValue('location', self.location)
        settings.endGroup()
        if self.changed:
            self.settings_form.register_post_process('update_display_css')
            self.plugin_manager.get_plugin_by_name('remotes').reset_cache()
        self.changed = False

    def update_display(self):
        """
        Update the preview display after changes have been made,
        """
        font = QtGui.QFont()
        font.setFamily(self.web_combo_box.currentFont().family())
        font.setBold(True)
        font.setPointSize(self.web_size)
        self.web_preview.setFont(font)
        self.web_preview.setStyleSheet('background-color: {back}; color: {front}'.format(back=self.background_color,
                                                                                         front=self.web_color))
        self.changed = True
