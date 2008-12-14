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

from PyQt4 import QtCore, QtGui

from openlp.core.resources import *
from openlp.core.lib import Plugin, MediaManagerItem

class PresentationPlugin(Plugin):
    def __init__(self):
        # Call the parent constructor
        Plugin.__init__(self, 'Presentations', '1.9.0')
        self.weight = -8
        # Create the plugin icon
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap(':/media/media_presentation.png'),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)


    def get_media_manager_item(self):
        # Create the MediaManagerItem object
        self.MediaManagerItem = MediaManagerItem(self.icon, 'Presentations')
        # Add a toolbar
        self.MediaManagerItem.addToolbar()
        # Create buttons for the toolbar
        ## Load Presentation Button ##
        self.MediaManagerItem.addToolbarButton('Load', 'Load presentations into openlp.org',
            ':/presentations/presentation_load.png', self.onPresentationLoadClick, 'PresentationLoadItem')
        ## Delete Presentation Button ##
        self.MediaManagerItem.addToolbarButton('Delete Presentation', 'Delete the selected presentation',
            ':/presentations/presentation_delete.png', self.onPresentationDeleteClick, 'PresentationDeleteItem')
        ## Separator Line ##
        self.MediaManagerItem.addToolbarSeparator()
        ## Preview Song Button ##
        self.MediaManagerItem.addToolbarButton('Preview Song', 'Preview the selected presentation',
            ':/system/system_preview.png', self.onPresentationPreviewClick, 'PresentationPreviewItem')
        ## Live Song Button ##
        self.MediaManagerItem.addToolbarButton('Go Live', 'Send the selected presentation live',
            ':/system/system_live.png', self.onPresentationLiveClick, 'PresentationLiveItem')
        ## Add Song Button ##
        self.MediaManagerItem.addToolbarButton('Add Presentation To Service',
            'Add the selected presentation(s) to the service', ':/system/system_add.png',
            self.onPresentationAddClick, 'PresentationAddItem')
        ## Add the songlist widget ##

        self.listView = QtGui.QListWidget()
        self.listView.setGeometry(QtCore.QRect(10, 100, 256, 591))
        self.listView.setObjectName("listView")
        self.MediaManagerItem.PageLayout.addWidget(self.listView)

        return self.MediaManagerItem

    def initalise(self):
        self.onPresentationLoadClick()

    def onPresentationLoadClick(self):
        files =  self.config.get_files()
        self.listView.clear()
        for f in files:
            self.listView.addItem(f)

    def onPresentationDeleteClick(self):
        pass

    def onPresentationPreviewClick(self):
        pass

    def onPresentationLiveClick(self):
        pass

    def onPresentationAddClick(self):
        pass
