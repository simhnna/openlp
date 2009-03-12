# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4
"""
OpenLP - Open Source Lyrics Projection
Copyright (c) 2008 Raoul Snyman
Portions copyright (c) 2008 Martin Thompson, Tim Bentley,

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc., 59 Temple
Place, Suite 330, Boston, MA 02111-1307 USA
"""

import os
import sys
import logging

from openlp.core.lib import Plugin

class PluginManager(object):
    """
    This is the Plugin manager, which loads all the plugins,
    and executes all the hooks, as and when necessary.
    """
    global log
    log=logging.getLogger("PluginMgr")
    log.info("Plugin manager loaded")

    def __init__(self, dir):
        """
        The constructor for the plugin manager.
        Passes the controllers on to the plugins for them to interact with via their ServiceItems
        """
        log.info("Plugin manager initing")
        if not dir in sys.path:
            log.debug("Inserting %s into sys.path", dir)
            sys.path.insert(0, dir)
        self.basepath = os.path.abspath(dir)
        log.debug("Base path %s ", self.basepath)
        self.plugins = []
        # this has to happen after the UI is sorted self.find_plugins(dir)
        log.info("Plugin manager done init")

    def find_plugins(self, dir, preview_controller, live_controller): # xxx shouldn't dir come from self.basepath
        """
        Scan the directory dir for objects inheriting from openlp.plugin
        """
        self.preview_controller=preview_controller
        self.live_controller=live_controller
        startdepth=len(os.path.abspath(dir).split(os.sep))
        log.debug("find plugins %s at depth %d" %( str(dir), startdepth))

        for root, dirs, files in os.walk(dir):
            for name in files:
                if name.endswith(".py") and not name.startswith("__"):
                    path = os.path.abspath(os.path.join(root, name))
                    thisdepth=len(path.split(os.sep))
                    if thisdepth-startdepth > 2: # skip anything lower down
                        continue
                    modulename, pyext = os.path.splitext(path)
                    prefix = os.path.commonprefix([self.basepath, path])
                    # hack off the plugin base path
                    modulename = modulename[len(prefix) + 1:]
                    modulename = modulename.replace(os.path.sep, '.')
                    # import the modules
                    log.debug("Importing %s from %s. Depth %d" % (modulename, path, thisdepth))
                    try:
                        __import__(modulename, globals(), locals(), [])
                    except ImportError, e:
                        log.error("Failed to import module %s on path %s for reason %s", modulename, path, e.message)
        self.plugin_classes = Plugin.__subclasses__()
        self.plugins = []
        plugin_objects = []
        for p in self.plugin_classes:
            try:
                plugin = p(self.preview_controller, self.live_controller)
                log.debug('loaded plugin' + str(p) + ' with controllers'+str(self.preview_controller)+str(self.live_controller))
            except TypeError:
                # TODO: need to get rid of this once all plugins are up to date
                plugin = p()
                log.debug('loaded plugin' + str(p) + ' with no controllers')
            log.debug("Plugin="+str(p))
            if plugin.check_pre_conditions():
                log.debug("Appending "+str(p))
                plugin_objects.append(plugin)
        self.plugins = sorted(plugin_objects, self.order_by_weight)

    def order_by_weight(self, x, y):
        return cmp(x.weight, y.weight)

    def hook_media_manager(self, mediatoolbox):
        """
        Loop through all the plugins. If a plugin has a valid media manager item,
        add it to the media manager.
        """
        for plugin in self.plugins:
            media_manager_item = plugin.get_media_manager_item()
            if media_manager_item is not None:
                log.debug('Inserting media manager item from %s' % plugin.name)
                mediatoolbox.addItem(media_manager_item, plugin.icon, media_manager_item.title)
                # TODO: These shouldn't be called here...
                plugin.initialise()

    def hook_settings_tabs(self, settingsform=None):
        """
        Loop through all the plugins. If a plugin has a valid settings tab item,
        add it to the settings tab.
        """
        for plugin in self.plugins:
            settings_tab = plugin.get_settings_tab()
            if settings_tab is not None:
                log.debug('Inserting settings tab item from %s' % plugin.name)
                settingsform.addTab(settings_tab)
            else:
                log.debug('No settings in %s' % plugin.name)

    def hook_import_menu(self, import_menu):
        """
        Loop through all the plugins and give them an opportunity to add an item
        to the import menu.
        """
        for plugin in self.plugins:
            plugin.add_import_menu_item(import_menu)

    def hook_export_menu(self, export_menu):
        """
        Loop through all the plugins and give them an opportunity to add an item
        to the export menu.
        """
        for plugin in self.plugins:
            plugin.add_export_menu_item(export_menu)

    def hook_handle_event(self, event):
        pass
