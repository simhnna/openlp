# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2013 Raoul Snyman                                        #
# Portions copyright (c) 2008-2013 Tim Bentley, Gerald Britton, Jonathan      #
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

import logging
from datetime import datetime

from PyQt4 import QtCore, QtGui

from openlp.core.lib import Plugin, Registry, Settings, StringContent, build_icon, translate
from openlp.core.lib.db import Manager
from openlp.core.lib.ui import create_action
from openlp.core.utils.actions import ActionList
from openlp.plugins.songusage.forms import SongUsageDetailForm, SongUsageDeleteForm
from openlp.plugins.songusage.lib import upgrade
from openlp.plugins.songusage.lib.db import init_schema, SongUsageItem

log = logging.getLogger(__name__)

YEAR = QtCore.QDate().currentDate().year()
if QtCore.QDate().currentDate().month() < 9:
    YEAR -= 1


__default_settings__ = {
    u'songusage/db type': u'sqlite',
    u'songusage/active': False,
    u'songusage/to date': QtCore.QDate(YEAR, 8, 31),
    u'songusage/from date': QtCore.QDate(YEAR - 1, 9, 1),
    u'songusage/last directory export': u''
}


class SongUsagePlugin(Plugin):
    log.info(u'SongUsage Plugin loaded')

    def __init__(self):
        super(SongUsagePlugin, self).__init__(u'songusage', __default_settings__)
        self.manager = Manager(u'songusage', init_schema, upgrade_mod=upgrade)
        self.weight = -4
        self.icon = build_icon(u':/plugins/plugin_songusage.png')
        self.active_icon = build_icon(u':/songusage/song_usage_active.png')
        self.inactive_icon = build_icon(u':/songusage/song_usage_inactive.png')
        self.song_usage_active = False

    def check_pre_conditions(self):
        """
        Check the plugin can run.
        """
        return self.manager.session is not None

    def add_tools_menu_item(self, tools_menu):
        """
        Give the SongUsage plugin the opportunity to add items to the **Tools** menu.

        ``tools_menu``
            The actual **Tools** menu item, so that your actions can use it as their parent.
        """
        log.info(u'add tools menu')
        self.toolsMenu = tools_menu
        self.song_usage_menu = QtGui.QMenu(tools_menu)
        self.song_usage_menu.setObjectName(u'song_usage_menu')
        self.song_usage_menu.setTitle(translate('SongUsagePlugin', '&Song Usage Tracking'))
        # SongUsage Delete
        self.song_usage_delete = create_action(tools_menu, u'songUsageDelete',
            text=translate('SongUsagePlugin', '&Delete Tracking Data'),
            statustip=translate('SongUsagePlugin', 'Delete song usage data up to a specified date.'),
            triggers=self.on_song_usage_delete)
        # SongUsage Report
        self.song_usage_report = create_action(tools_menu, u'songUsageReport',
            text=translate('SongUsagePlugin', '&Extract Tracking Data'),
            statustip=translate('SongUsagePlugin', 'Generate a report on song usage.'),
            triggers=self.on_song_usage_report)
        # SongUsage activation
        self.song_usage_status = create_action(tools_menu, u'songUsageStatus',
            text=translate('SongUsagePlugin', 'Toggle Tracking'),
            statustip=translate('SongUsagePlugin', 'Toggle the tracking of song usage.'), checked=False,
            can_shortcuts=True, triggers=self.toggle_song_usage_state)
        # Add Menus together
        self.toolsMenu.addAction(self.song_usage_menu.menuAction())
        self.song_usage_menu.addAction(self.song_usage_status)
        self.song_usage_menu.addSeparator()
        self.song_usage_menu.addAction(self.song_usage_report)
        self.song_usage_menu.addAction(self.song_usage_delete)
        self.song_usage_active_button = QtGui.QToolButton(self.main_window.status_bar)
        self.song_usage_active_button.setCheckable(True)
        self.song_usage_active_button.setAutoRaise(True)
        self.song_usage_active_button.setStatusTip(translate('SongUsagePlugin', 'Toggle the tracking of song usage.'))
        self.song_usage_active_button.setObjectName(u'song_usage_active_button')
        self.main_window.status_bar.insertPermanentWidget(1, self.song_usage_active_button)
        self.song_usage_active_button.hide()
        # Signals and slots
        QtCore.QObject.connect(self.song_usage_status, QtCore.SIGNAL(u'visibilityChanged(bool)'),
            self.song_usage_status.setChecked)
        self.song_usage_active_button.toggled.connect(self.toggle_song_usage_state)
        self.song_usage_menu.menuAction().setVisible(False)

    def initialise(self):
        log.info(u'SongUsage Initialising')
        Plugin.initialise(self)
        Registry().register_function(u'slidecontroller_live_started', self.display_song_usage)
        Registry().register_function(u'print_service_started', self.print_song_usage)
        self.song_usage_active = Settings().value(self.settings_section + u'/active')
        # Set the button and checkbox state
        self.set_button_state()
        action_list = ActionList.get_instance()
        action_list.add_action(self.song_usage_status, translate('SongUsagePlugin', 'Song Usage'))
        action_list.add_action(self.song_usage_delete, translate('SongUsagePlugin', 'Song Usage'))
        action_list.add_action(self.song_usage_report, translate('SongUsagePlugin', 'Song Usage'))
        self.song_usage_delete_form = SongUsageDeleteForm(self.manager, self.main_window)
        self.song_usage_detail_form = SongUsageDetailForm(self, self.main_window)
        self.song_usage_menu.menuAction().setVisible(True)
        self.song_usage_active_button.show()

    def finalise(self):
        """
        Tidy up on exit
        """
        log.info(u'Plugin Finalise')
        self.manager.finalise()
        Plugin.finalise(self)
        self.song_usage_menu.menuAction().setVisible(False)
        action_list = ActionList.get_instance()
        action_list.remove_action(self.song_usage_status, translate('SongUsagePlugin', 'Song Usage'))
        action_list.remove_action(self.song_usage_delete, translate('SongUsagePlugin', 'Song Usage'))
        action_list.remove_action(self.song_usage_report, translate('SongUsagePlugin', 'Song Usage'))
        self.song_usage_active_button.hide()
        # stop any events being processed
        self.song_usage_active = False

    def toggle_song_usage_state(self):
        """
        Manage the state of the audit collection and amend
        the UI when necessary,
        """
        self.song_usage_active = not self.song_usage_active
        Settings().setValue(self.settings_section + u'/active', self.song_usage_active)
        self.set_button_state()

    def set_button_state(self):
        """
        Keep buttons inline.  Turn of signals to stop dead loop but we need the
        button and check box set correctly.
        """
        self.song_usage_active_button.blockSignals(True)
        self.song_usage_status.blockSignals(True)
        if self.song_usage_active:
            self.song_usage_active_button.setIcon(self.active_icon)
            self.song_usage_status.setChecked(True)
            self.song_usage_active_button.setChecked(True)
            self.song_usage_active_button.setToolTip(translate('SongUsagePlugin', 'Song usage tracking is active.'))
        else:
            self.song_usage_active_button.setIcon(self.inactive_icon)
            self.song_usage_status.setChecked(False)
            self.song_usage_active_button.setChecked(False)
            self.song_usage_active_button.setToolTip(translate('SongUsagePlugin', 'Song usage tracking is inactive.'))
        self.song_usage_active_button.blockSignals(False)
        self.song_usage_status.blockSignals(False)

    def display_song_usage(self, item):
        """
        Song Usage for which has been displayed
        """
        self._add_song_usage(translate('SongUsagePlugin', 'display'), item)

    def print_song_usage(self, item):
        """
        Song Usage for which has been printed
        """
        self._add_song_usage(translate('SongUsagePlugin', 'printed'), item)

    def _add_song_usage(self, source, item):
        audit = item[0].audit
        if self.song_usage_active and audit:
            song_usage_item = SongUsageItem()
            song_usage_item.usagedate = datetime.today()
            song_usage_item.usagetime = datetime.now().time()
            song_usage_item.title = audit[0]
            song_usage_item.copyright = audit[2]
            song_usage_item.ccl_number = audit[3]
            song_usage_item.authors = u' '.join(audit[1])
            song_usage_item.plugin_name = item[0].name
            song_usage_item.source = source
            self.manager.save_object(song_usage_item)

    def on_song_usage_delete(self):
        self.song_usage_delete_form.exec_()

    def on_song_usage_report(self):
        self.song_usage_detail_form.initialise()
        self.song_usage_detail_form.exec_()

    def about(self):
        about_text = translate('SongUsagePlugin',
            '<strong>SongUsage Plugin</strong><br />This plugin tracks the usage of songs in services.')
        return about_text

    def set_plugin_text_strings(self):
        """
        Called to define all translatable texts of the plugin
        """
        ## Name PluginList ##
        self.text_strings[StringContent.Name] = {
            u'singular': translate('SongUsagePlugin', 'SongUsage', 'name singular'),
            u'plural': translate('SongUsagePlugin', 'SongUsage', 'name plural')
        }
        ## Name for MediaDockManager, SettingsManager ##
        self.text_strings[StringContent.VisibleName] = {
            u'title': translate('SongUsagePlugin', 'SongUsage', 'container title')
        }
