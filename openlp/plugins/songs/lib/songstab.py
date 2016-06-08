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

from PyQt5 import QtCore, QtWidgets

from openlp.core.common import Settings, translate
from openlp.core.lib import SettingsTab
from openlp.plugins.songs.lib.ui import SongStrings


class SongsTab(SettingsTab):
    """
    SongsTab is the Songs settings tab in the settings dialog.
    """
    def setupUi(self):
        """
        Set up the configuration tab UI.
        """
        self.setObjectName('SongsTab')
        super(SongsTab, self).setupUi()
        self.mode_group_box = QtWidgets.QGroupBox(self.left_column)
        self.mode_group_box.setObjectName('mode_group_box')
        self.mode_layout = QtWidgets.QVBoxLayout(self.mode_group_box)
        self.mode_layout.setObjectName('mode_layout')
        self.tool_bar_active_check_box = QtWidgets.QCheckBox(self.mode_group_box)
        self.tool_bar_active_check_box.setObjectName('tool_bar_active_check_box')
        self.mode_layout.addWidget(self.tool_bar_active_check_box)
        self.update_on_edit_check_box = QtWidgets.QCheckBox(self.mode_group_box)
        self.update_on_edit_check_box.setObjectName('update_on_edit_check_box')
        self.mode_layout.addWidget(self.update_on_edit_check_box)
        self.add_from_service_check_box = QtWidgets.QCheckBox(self.mode_group_box)
        self.add_from_service_check_box.setObjectName('add_from_service_check_box')
        self.mode_layout.addWidget(self.add_from_service_check_box)
        self.display_songbook_check_box = QtWidgets.QCheckBox(self.mode_group_box)
        self.display_songbook_check_box.setObjectName('songbook_check_box')
        self.mode_layout.addWidget(self.display_songbook_check_box)
        self.display_copyright_check_box = QtWidgets.QCheckBox(self.mode_group_box)
        self.display_copyright_check_box.setObjectName('copyright_check_box')
        self.mode_layout.addWidget(self.display_copyright_check_box)
        self.left_layout.addWidget(self.mode_group_box)

        self.chords_group_box = QtWidgets.QGroupBox(self.left_column)
        self.chords_group_box.setObjectName('chords_group_box')
        self.chords_layout = QtWidgets.QVBoxLayout(self.chords_group_box)
        self.chords_layout.setObjectName('chords_layout')
        self.mainview_chords_check_box = QtWidgets.QCheckBox(self.mode_group_box)
        self.mainview_chords_check_box.setObjectName('tool_bar_active_check_box')
        self.chords_layout.addWidget(self.mainview_chords_check_box)
        self.disable_chords_import_check_box = QtWidgets.QCheckBox(self.mode_group_box)
        self.disable_chords_import_check_box.setObjectName('tool_bar_active_check_box')
        self.chords_layout.addWidget(self.disable_chords_import_check_box)

        # Chords notation
        self.chord_notation_label = QtWidgets.QLabel(self.chords_group_box)
        self.chord_notation_label.setWordWrap(True)
        self.chords_layout.addWidget(self.chord_notation_label)
        self.english_notation_radio_button = QtWidgets.QRadioButton(self.chords_group_box)
        self.english_notation_radio_button.setObjectName('english_notation_radio_button')
        self.chords_layout.addWidget(self.english_notation_radio_button)
        self.german_notation_radio_button = QtWidgets.QRadioButton(self.chords_group_box)
        self.german_notation_radio_button.setObjectName('german_notation_radio_button')
        self.chords_layout.addWidget(self.german_notation_radio_button)
        self.neolatin_notation_radio_button = QtWidgets.QRadioButton(self.chords_group_box)
        self.neolatin_notation_radio_button.setObjectName('neolatin_notation_radio_button')
        self.chords_layout.addWidget(self.neolatin_notation_radio_button)

        self.left_layout.addWidget(self.chords_group_box)

        self.left_layout.addStretch()
        self.right_layout.addStretch()
        self.tool_bar_active_check_box.stateChanged.connect(self.on_tool_bar_active_check_box_changed)
        self.update_on_edit_check_box.stateChanged.connect(self.on_update_on_edit_check_box_changed)
        self.add_from_service_check_box.stateChanged.connect(self.on_add_from_service_check_box_changed)
        self.display_songbook_check_box.stateChanged.connect(self.on_songbook_check_box_changed)
        self.display_copyright_check_box.stateChanged.connect(self.on_copyright_check_box_changed)
        self.mainview_chords_check_box.stateChanged.connect(self.on_mainview_chords_check_box_changed)
        self.disable_chords_import_check_box.stateChanged.connect(self.on_disable_chords_import_check_box_changed)
        self.english_notation_radio_button.clicked.connect(self.on_english_notation_button_clicked)
        self.german_notation_radio_button.clicked.connect(self.on_german_notation_button_clicked)
        self.neolatin_notation_radio_button.clicked.connect(self.on_neolatin_notation_button_clicked)

    def retranslateUi(self):
        self.mode_group_box.setTitle(translate('SongsPlugin.SongsTab', 'Songs Mode'))
        self.tool_bar_active_check_box.setText(translate('SongsPlugin.SongsTab',
                                                         'Display verses on live tool bar'))
        self.update_on_edit_check_box.setText(translate('SongsPlugin.SongsTab', 'Update service from song edit'))
        self.add_from_service_check_box.setText(translate('SongsPlugin.SongsTab',
                                                          'Import missing songs from service files'))
        self.display_songbook_check_box.setText(translate('SongsPlugin.SongsTab', 'Display songbook in footer'))
        self.display_copyright_check_box.setText(translate('SongsPlugin.SongsTab',
                                                           'Display "{symbol}" symbol before copyright '
                                                           'info').format(symbol=SongStrings.CopyrightSymbol))
        self.chords_group_box.setTitle(translate('SongsPlugin.SongsTab', 'Chords'))
        self.mainview_chords_check_box.setText(translate('SongsPlugin.SongsTab', 'Display chords in the main view'))
        self.disable_chords_import_check_box.setText(translate('SongsPlugin.SongsTab',
                                                               'Ignore chords when importing songs'))
        self.chord_notation_label.setText(translate('SongsPlugin.SongsTab', 'Chord notation to use:'))
        self.english_notation_radio_button.setText(translate('SongsPlugin.SongsTab', 'English') + ' (C-D-E-F-G-A-B)')
        self.german_notation_radio_button.setText(translate('SongsPlugin.SongsTab', 'German') + ' (C-D-E-F-G-A-H)')
        self.neolatin_notation_radio_button.setText(
            translate('SongsPlugin.SongsTab', 'Neo-Latin') + ' (Do-Re-Mi-Fa-Sol-La-Si)')

    def on_search_as_type_check_box_changed(self, check_state):
        self.song_search = (check_state == QtCore.Qt.Checked)

    def on_tool_bar_active_check_box_changed(self, check_state):
        self.tool_bar = (check_state == QtCore.Qt.Checked)

    def on_update_on_edit_check_box_changed(self, check_state):
        self.update_edit = (check_state == QtCore.Qt.Checked)

    def on_add_from_service_check_box_changed(self, check_state):
        self.update_load = (check_state == QtCore.Qt.Checked)

    def on_songbook_check_box_changed(self, check_state):
        self.display_songbook = (check_state == QtCore.Qt.Checked)

    def on_copyright_check_box_changed(self, check_state):
        self.display_copyright_symbol = (check_state == QtCore.Qt.Checked)

    def on_mainview_chords_check_box_changed(self, check_state):
        self.mainview_chords = (check_state == QtCore.Qt.Checked)

    def on_disable_chords_import_check_box_changed(self, check_state):
        self.disable_chords_import = (check_state == QtCore.Qt.Checked)

    def on_english_notation_button_clicked(self):
        self.chord_notation = 'english'

    def on_german_notation_button_clicked(self):
        self.chord_notation = 'german'

    def on_neolatin_notation_button_clicked(self):
        self.chord_notation = 'neo-latin'

    def load(self):
        settings = Settings()
        settings.beginGroup(self.settings_section)
        self.tool_bar = settings.value('display songbar')
        self.update_edit = settings.value('update service on edit')
        self.update_load = settings.value('add song from service')
        self.display_songbook = settings.value('display songbook')
        self.display_copyright_symbol = settings.value('display copyright symbol')
        self.chord_notation = settings.value('chord notation')
        self.mainview_chords = settings.value('mainview chords')
        self.disable_chords_import = settings.value('disable chords import')
        self.tool_bar_active_check_box.setChecked(self.tool_bar)
        self.update_on_edit_check_box.setChecked(self.update_edit)
        self.add_from_service_check_box.setChecked(self.update_load)
        self.display_songbook_check_box.setChecked(self.display_songbook)
        self.display_copyright_check_box.setChecked(self.display_copyright_symbol)
        self.mainview_chords_check_box.setChecked(self.mainview_chords)
        self.disable_chords_import_check_box.setChecked(self.disable_chords_import)
        if self.chord_notation == 'german':
            self.german_notation_radio_button.setChecked(True)
        elif self.chord_notation == 'neo-latin':
            self.neolatin_notation_radio_button.setChecked(True)
        else:
            self.english_notation_radio_button.setChecked(True)
        settings.endGroup()

    def save(self):
        settings = Settings()
        settings.beginGroup(self.settings_section)
        settings.setValue('display songbar', self.tool_bar)
        settings.setValue('update service on edit', self.update_edit)
        settings.setValue('add song from service', self.update_load)
        settings.setValue('display songbook', self.display_songbook)
        settings.setValue('display copyright symbol', self.display_copyright_symbol)
        settings.setValue('mainview chords', self.mainview_chords)
        settings.setValue('disable chords import', self.disable_chords_import)
        settings.setValue('chord notation', self.chord_notation)
        settings.endGroup()
        if self.tab_visited:
            self.settings_form.register_post_process('songs_config_updated')
        self.tab_visited = False
