# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2010 Raoul Snyman                                        #
# Portions copyright (c) 2008-2010 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Christian Richter, Maikel Stuivenberg, Martin      #
# Thompson, Jon Tibble, Carsten Tinggaard                                     #
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

import os
import logging
import cPickle
import zipfile

log = logging.getLogger(__name__)

from PyQt4 import QtCore, QtGui

from openlp.core.lib import OpenLPToolbar, ServiceItem, contextMenuAction, \
    Receiver, build_icon, ItemCapabilities, SettingsManager
from openlp.core.ui import ServiceNoteForm, ServiceItemEditForm
from openlp.core.utils import AppLocation

class ServiceManagerList(QtGui.QTreeWidget):

    def __init__(self, parent=None, name=None):
        QtGui.QTreeWidget.__init__(self, parent)
        self.parent = parent

    def keyPressEvent(self, event):
        if type(event) == QtGui.QKeyEvent:
            #here accept the event and do something
            if event.key() == QtCore.Qt.Key_Enter:
                self.parent.makeLive()
                event.accept()
            elif event.key() == QtCore.Qt.Key_Home:
                self.parent.onServiceTop()
                event.accept()
            elif event.key() == QtCore.Qt.Key_End:
                self.parent.onServiceEnd()
                event.accept()
            elif event.key() == QtCore.Qt.Key_PageUp:
                self.parent.onServiceUp()
                event.accept()
            elif event.key() == QtCore.Qt.Key_PageDown:
                self.parent.onServiceDown()
                event.accept()
            elif event.key() == QtCore.Qt.Key_Up:
                self.parent.onMoveSelectionUp()
                event.accept()
            elif event.key() == QtCore.Qt.Key_Down:
                self.parent.onMoveSelectionDown()
                event.accept()
            event.ignore()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        """
        Drag and drop event does not care what data is selected
        as the recipient will use events to request the data move
        just tell it what plugin to call
        """
        if event.buttons() != QtCore.Qt.LeftButton:
            event.ignore()
            return
        drag = QtGui.QDrag(self)
        mimeData = QtCore.QMimeData()
        drag.setMimeData(mimeData)
        mimeData.setText(u'ServiceManager')
        drag.start(QtCore.Qt.CopyAction)

class ServiceManager(QtGui.QWidget):
    """
    Manages the services.  This involves taking text strings from plugins and
    adding them to the service.  This service can then be zipped up with all
    the resources used into one OSZ file for use on any OpenLP v2 installation.
    Also handles the UI tasks of moving things up and down etc.
    """
    def __init__(self, parent):
        """
        Sets up the service manager, toolbars, list view, et al.
        """
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.serviceItems = []
        self.serviceName = u''
        self.suffixes = u''
        self.viewers = u''
        self.droppos = 0
        #is a new service and has not been saved
        self.isNew = True
        self.serviceNoteForm = ServiceNoteForm()
        self.serviceItemEditForm = ServiceItemEditForm()
        #start with the layout
        self.Layout = QtGui.QVBoxLayout(self)
        self.Layout.setSpacing(0)
        self.Layout.setMargin(0)
        # Create the top toolbar
        self.Toolbar = OpenLPToolbar(self)
        self.Toolbar.addToolbarButton(
            self.trUtf8('New Service'), u':/general/general_new.png',
            self.trUtf8('Create a new service'), self.onNewService)
        self.Toolbar.addToolbarButton(
            self.trUtf8('Open Service'), u':/general/general_open.png',
            self.trUtf8('Load an existing service'), self.onLoadService)
        self.Toolbar.addToolbarButton(
            self.trUtf8('Save Service'), u':/general/general_save.png',
            self.trUtf8('Save this service'), self.onSaveService)
        self.Toolbar.addSeparator()
        self.ThemeLabel = QtGui.QLabel(self.trUtf8('Theme:'),
            self)
        self.ThemeLabel.setMargin(3)
        self.Toolbar.addWidget(self.ThemeLabel)
        self.ThemeComboBox = QtGui.QComboBox(self.Toolbar)
        self.ThemeComboBox.setToolTip(self.trUtf8(
            u'Select a theme for the service'))
        self.ThemeComboBox.setSizeAdjustPolicy(
            QtGui.QComboBox.AdjustToContents)
        self.ThemeWidget = QtGui.QWidgetAction(self.Toolbar)
        self.ThemeWidget.setDefaultWidget(self.ThemeComboBox)
        self.Toolbar.addAction(self.ThemeWidget)
        self.Layout.addWidget(self.Toolbar)
        # Create the service manager list
        self.ServiceManagerList = ServiceManagerList(self)
        self.ServiceManagerList.setEditTriggers(
            QtGui.QAbstractItemView.CurrentChanged |
            QtGui.QAbstractItemView.DoubleClicked |
            QtGui.QAbstractItemView.EditKeyPressed)
        self.ServiceManagerList.setDragDropMode(
            QtGui.QAbstractItemView.DragDrop)
        self.ServiceManagerList.setAlternatingRowColors(True)
        self.ServiceManagerList.setHeaderHidden(True)
        self.ServiceManagerList.setExpandsOnDoubleClick(False)
        self.ServiceManagerList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        QtCore.QObject.connect(self.ServiceManagerList,
            QtCore.SIGNAL('customContextMenuRequested(QPoint)'), self.contextMenu)
        self.ServiceManagerList.setObjectName(u'ServiceManagerList')
        # enable drop
        self.ServiceManagerList.__class__.dragEnterEvent = self.dragEnterEvent
        self.ServiceManagerList.__class__.dragMoveEvent = self.dragEnterEvent
        self.ServiceManagerList.__class__.dropEvent = self.dropEvent
        self.Layout.addWidget(self.ServiceManagerList)
        # Add the bottom toolbar
        self.OrderToolbar = OpenLPToolbar(self)
        self.OrderToolbar.addToolbarButton(
            self.trUtf8('Move to &top'), u':/services/service_top.png',
            self.trUtf8('Move to top'), self.onServiceTop)
        self.OrderToolbar.addToolbarButton(
            self.trUtf8('Move &up'), u':/services/service_up.png',
            self.trUtf8('Move up order'), self.onServiceUp)
        self.OrderToolbar.addToolbarButton(
            self.trUtf8('Move &down'), u':/services/service_down.png',
            self.trUtf8('Move down order'), self.onServiceDown)
        self.OrderToolbar.addToolbarButton(
            self.trUtf8('Move to &bottom'), u':/services/service_bottom.png',
            self.trUtf8('Move to end'), self.onServiceEnd)
        self.OrderToolbar.addSeparator()
        self.OrderToolbar.addToolbarButton(
            self.trUtf8('&Delete From Service'), u':/general/general_delete.png',
            self.trUtf8('Delete From Service'), self.onDeleteFromService)
        self.Layout.addWidget(self.OrderToolbar)
        # Connect up our signals and slots
        QtCore.QObject.connect(self.ThemeComboBox,
            QtCore.SIGNAL(u'activated(int)'), self.onThemeComboBoxSelected)
        QtCore.QObject.connect(self.ServiceManagerList,
            QtCore.SIGNAL(u'doubleClicked(QModelIndex)'), self.makeLive)
        QtCore.QObject.connect(self.ServiceManagerList,
           QtCore.SIGNAL(u'itemCollapsed(QTreeWidgetItem*)'), self.collapsed)
        QtCore.QObject.connect(self.ServiceManagerList,
           QtCore.SIGNAL(u'itemExpanded(QTreeWidgetItem*)'), self.expanded)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'theme_update_list'), self.updateThemeList)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'servicemanager_next_item'), self.nextItem)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'servicemanager_previous_item'), self.previousItem)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'servicemanager_set_item'), self.onSetItem)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'servicemanager_list_request'), self.listRequest)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'config_updated'), self.regenerateServiceItems)
        # Last little bits of setting up
        self.service_theme = unicode(QtCore.QSettings().value(
            self.parent.serviceSettingsSection + u'/service theme',
            QtCore.QVariant(u'')).toString())
        self.servicePath = AppLocation.get_section_data_path(u'servicemanager')
        #build the drag and drop context menu
        self.dndMenu = QtGui.QMenu()
        self.newAction = self.dndMenu.addAction(self.trUtf8('&Add New Item'))
        self.newAction.setIcon(build_icon(u':/general/general_edit.png'))
        self.addToAction = self.dndMenu.addAction(self.trUtf8('&Add to Selected Item'))
        self.addToAction.setIcon(build_icon(u':/general/general_edit.png'))
        #build the context menu
        self.menu = QtGui.QMenu()
        self.editAction = self.menu.addAction(self.trUtf8('&Edit Item'))
        self.editAction.setIcon(build_icon(u':/general/general_edit.png'))
        self.maintainAction = self.menu.addAction(self.trUtf8('&Maintain Item'))
        self.maintainAction.setIcon(build_icon(u':/general/general_edit.png'))
        self.notesAction = self.menu.addAction(self.trUtf8('&Notes'))
        self.notesAction.setIcon(build_icon(u':/services/service_notes.png'))
        self.deleteAction = self.menu.addAction(
            self.trUtf8('&Delete From Service'))
        self.deleteAction.setIcon(build_icon(u':/general/general_delete.png'))
        self.sep1 = self.menu.addAction(u'')
        self.sep1.setSeparator(True)
        self.previewAction = self.menu.addAction(self.trUtf8('&Preview Verse'))
        self.previewAction.setIcon(build_icon(u':/general/general_preview.png'))
        self.liveAction = self.menu.addAction(self.trUtf8('&Live Verse'))
        self.liveAction.setIcon(build_icon(u':/general/general_live.png'))
        self.sep2 = self.menu.addAction(u'')
        self.sep2.setSeparator(True)
        self.themeMenu = QtGui.QMenu(self.trUtf8(u'&Change Item Theme'))
        self.menu.addMenu(self.themeMenu)

    def supportedSuffixes(self, suffix):
        self.suffixes = u'%s %s' % (self.suffixes, suffix)

    def supportedViewers(self, viewer):
        self.viewers = u'%s %s' % (self.viewers, viewer)

    def contextMenu(self, point):
        item = self.ServiceManagerList.itemAt(point)
        if item is None:
            return
        if item.parent() is None:
            pos = item.data(0, QtCore.Qt.UserRole).toInt()[0]
        else:
            pos = item.parent().data(0, QtCore.Qt.UserRole).toInt()[0]
        serviceItem = self.serviceItems[pos - 1]
        self.editAction.setVisible(False)
        self.maintainAction.setVisible(False)
        self.notesAction.setVisible(False)
        if serviceItem[u'service_item'].is_capable(ItemCapabilities.AllowsEdit):
            self.editAction.setVisible(True)
        if serviceItem[u'service_item']\
            .is_capable(ItemCapabilities.AllowsMaintain):
            self.maintainAction.setVisible(True)
        if item.parent() is None:
            self.notesAction.setVisible(True)
        self.themeMenu.menuAction().setVisible(False)
        if serviceItem[u'service_item'].is_text():
            self.themeMenu.menuAction().setVisible(True)
        action = self.menu.exec_(self.ServiceManagerList.mapToGlobal(point))
        if action == self.editAction:
            self.remoteEdit()
        if action == self.maintainAction:
            self.onServiceItemEditForm()
        if action == self.deleteAction:
            self.onDeleteFromService()
        if action == self.notesAction:
            self.onServiceItemNoteForm()
        if action == self.previewAction:
            self.makePreview()
        if action == self.liveAction:
            self.makeLive()

    def onServiceItemNoteForm(self):
        item, count = self.findServiceItem()
        self.serviceNoteForm.textEdit.setPlainText(
            self.serviceItems[item][u'service_item'].notes)
        if self.serviceNoteForm.exec_():
            self.serviceItems[item][u'service_item'].notes = \
                self.serviceNoteForm.textEdit.toPlainText()
            self.repaintServiceList(item, 0)

    def onServiceItemEditForm(self):
        item, count = self.findServiceItem()
        self.serviceItemEditForm.setServiceItem(
            self.serviceItems[item][u'service_item'])
        if self.serviceItemEditForm.exec_():
            self.serviceItems[item][u'service_item'] = \
                self.serviceItemEditForm.getServiceItem()
            self.repaintServiceList(item, 0)

    def nextItem(self):
        """
        Called by the SlideController to select the
        next service item
        """
        if len(self.ServiceManagerList.selectedItems()) == 0:
            return
        selected = self.ServiceManagerList.selectedItems()[0]
        lookFor = 0
        serviceIterator = QtGui.QTreeWidgetItemIterator(self.ServiceManagerList)
        while serviceIterator.value():
            if lookFor == 1 and serviceIterator.value().parent() is None:
                self.ServiceManagerList.setCurrentItem(serviceIterator.value())
                self.makeLive()
                return
            if serviceIterator.value() == selected:
                lookFor = 1
            serviceIterator += 1

    def previousItem(self):
        """
        Called by the SlideController to select the
        previous service item
        """
        if len(self.ServiceManagerList.selectedItems()) == 0:
            return
        selected = self.ServiceManagerList.selectedItems()[0]
        prevItem = None
        serviceIterator = QtGui.QTreeWidgetItemIterator(self.ServiceManagerList)
        while serviceIterator.value():
            if serviceIterator.value() == selected:
                if prevItem:
                    self.ServiceManagerList.setCurrentItem(prevItem)
                    self.makeLive()
                return
            if serviceIterator.value().parent() is None:
                prevItem = serviceIterator.value()
            serviceIterator += 1

    def onSetItem(self, message):
        """
        Called by a signal to select a specific item
        """
        self.setItem(int(message[0]))

    def setItem(self, index):
        """
        Makes a specific item in the service live
        """
        if index >= 0 and index < self.ServiceManagerList.topLevelItemCount:
            item = self.ServiceManagerList.topLevelItem(index)
            self.ServiceManagerList.setCurrentItem(item)
            self.makeLive()

    def onMoveSelectionUp(self):
        """
        Moves the selection up the window
        Called by the up arrow
        """
        serviceIterator = QtGui.QTreeWidgetItemIterator(self.ServiceManagerList)
        tempItem = None
        setLastItem = False
        while serviceIterator:
            if serviceIterator.isSelected() and tempItem is None:
                setLastItem = True
                serviceIterator.setSelected(False)
            if serviceIterator.isSelected():
                #We are on the first record
                if tempItem:
                    tempItem.setSelected(True)
                    serviceIterator.setSelected(False)
            else:
                tempItem = serviceIterator
            lastItem = serviceIterator
            ++serviceIterator
        #Top Item was selected so set the last one
        if setLastItem:
            lastItem.setSelected(True)

    def onMoveSelectionDown(self):
        """
        Moves the selection down the window
        Called by the down arrow
        """
        serviceIterator = QtGui.QTreeWidgetItemIterator(self.ServiceManagerList)
        firstItem = serviceIterator
        setSelected = False
        while serviceIterator:
            if setSelected:
                setSelected = False
                serviceIterator.setSelected(True)
            elif serviceIterator.isSelected():
                serviceIterator.setSelected(False)
                setSelected = True
            ++serviceIterator
        if setSelected:
            firstItem.setSelected(True)

    def collapsed(self, item):
        """
        Record if an item is collapsed
        Used when repainting the list to get the correct state
        """
        pos = item.data(0, QtCore.Qt.UserRole).toInt()[0]
        self.serviceItems[pos -1 ][u'expanded'] = False

    def expanded(self, item):
        """
        Record if an item is collapsed
        Used when repainting the list to get the correct state
        """
        pos = item.data(0, QtCore.Qt.UserRole).toInt()[0]
        self.serviceItems[pos -1 ][u'expanded'] = True

    def onServiceTop(self):
        """
        Move the current ServiceItem to the top of the list
        """
        item, count = self.findServiceItem()
        if item < len(self.serviceItems) and item is not -1:
            temp = self.serviceItems[item]
            self.serviceItems.remove(self.serviceItems[item])
            self.serviceItems.insert(0, temp)
            self.repaintServiceList(0, count)
        self.parent.serviceChanged(False, self.serviceName)

    def onServiceUp(self):
        """
        Move the current ServiceItem up in the list
        Note move up means move to top of area ie 0.
        """
        item, count = self.findServiceItem()
        if item > 0:
            temp = self.serviceItems[item]
            self.serviceItems.remove(self.serviceItems[item])
            self.serviceItems.insert(item - 1, temp)
            self.repaintServiceList(item - 1, count)
        self.parent.serviceChanged(False, self.serviceName)

    def onServiceDown(self):
        """
        Move the current ServiceItem down in the list
        Note move down means move to bottom of area i.e len().
        """
        item, count = self.findServiceItem()
        if item < len(self.serviceItems) and item is not -1:
            temp = self.serviceItems[item]
            self.serviceItems.remove(self.serviceItems[item])
            self.serviceItems.insert(item + 1, temp)
            self.repaintServiceList(item + 1, count)
        self.parent.serviceChanged(False, self.serviceName)

    def onServiceEnd(self):
        """
        Move the current ServiceItem to the bottom of the list
        """
        item, count = self.findServiceItem()
        if item < len(self.serviceItems) and item is not -1:
            temp = self.serviceItems[item]
            self.serviceItems.remove(self.serviceItems[item])
            self.serviceItems.insert(len(self.serviceItems), temp)
            self.repaintServiceList(len(self.serviceItems) - 1, count)
        self.parent.serviceChanged(False, self.serviceName)

    def onNewService(self):
        """
        Clear the list to create a new service
        """
        if self.parent.serviceNotSaved and QtCore.QSettings().value(
            self.parent.generalSettingsSection + u'/save prompt',
            QtCore.QVariant(False)).toBool():
            ret = QtGui.QMessageBox.question(self,
                self.trUtf8('Save Changes to Service?'),
                self.trUtf8('Your service is unsaved, do you want to save '
                            'those changes before creating a new one?'),
                QtGui.QMessageBox.StandardButtons(
                    QtGui.QMessageBox.Cancel |
                    QtGui.QMessageBox.Save),
                QtGui.QMessageBox.Save)
            if ret == QtGui.QMessageBox.Save:
                self.onSaveService()
        self.ServiceManagerList.clear()
        self.serviceItems = []
        self.serviceName = u''
        self.isNew = True
        self.parent.serviceChanged(True, self.serviceName)

    def onDeleteFromService(self):
        """
        Remove the current ServiceItem from the list
        """
        item, count = self.findServiceItem()
        if item is not -1:
            self.serviceItems.remove(self.serviceItems[item])
            self.repaintServiceList(0, 0)
        self.parent.serviceChanged(False, self.serviceName)

    def repaintServiceList(self, serviceItem, serviceItemCount):
        """
        Clear the existing service list and prepaint all the items
        Used when moving items as the move takes place in supporting array,
        and when regenerating all the items due to theme changes
        """
        #Correct order of items in array
        count = 1
        for item in self.serviceItems:
            item[u'order'] = count
            count += 1
        #Repaint the screen
        self.ServiceManagerList.clear()
        for itemcount, item in enumerate(self.serviceItems):
            serviceitem = item[u'service_item']
            treewidgetitem = QtGui.QTreeWidgetItem(self.ServiceManagerList)
            if serviceitem.isValid:
                if serviceitem.notes:
                    icon = QtGui.QImage(serviceitem.icon)
                    icon = icon.scaled(80, 80, QtCore.Qt.KeepAspectRatio,
                                        QtCore.Qt.SmoothTransformation)
                    overlay = QtGui.QImage(':/services/service_item_notes.png')
                    overlay = overlay.scaled(80, 80, QtCore.Qt.KeepAspectRatio,
                                              QtCore.Qt.SmoothTransformation)
                    painter = QtGui.QPainter(icon)
                    painter.drawImage(0, 0, overlay)
                    painter.end()
                    treewidgetitem.setIcon(0, build_icon(icon))
                else:
                    treewidgetitem.setIcon(0, serviceitem.iconic_representation)
            else:
                treewidgetitem.setIcon(0, build_icon(u':/general/general_delete.png'))
            treewidgetitem.setText(0, serviceitem.title)
            treewidgetitem.setToolTip(0, serviceitem.notes)
            treewidgetitem.setData(0, QtCore.Qt.UserRole,
                QtCore.QVariant(item[u'order']))
            for count, frame in enumerate(serviceitem.get_frames()):
                treewidgetitem1 = QtGui.QTreeWidgetItem(treewidgetitem)
                text = frame[u'title']
                treewidgetitem1.setText(0, text[:40])
                treewidgetitem1.setData(0, QtCore.Qt.UserRole,
                    QtCore.QVariant(count))
                if serviceItem == itemcount and serviceItemCount == count:
                    #preserve expanding status as setCurrentItem sets it to True
                    temp = item[u'expanded']
                    self.ServiceManagerList.setCurrentItem(treewidgetitem1)
                    item[u'expanded'] = temp
            treewidgetitem.setExpanded(item[u'expanded'])

    def onSaveService(self, quick=False):
        """
        Save the current service in a zip (OSZ) file
        This file contains
        * An osd which is a pickle of the service items
        * All image, presentation and video files needed to run the service.
        """
        log.debug(u'onSaveService')
        if not quick or self.isNew:
            filename = QtGui.QFileDialog.getSaveFileName(self,
            self.trUtf8(u'Save Service'),
            SettingsManager.get_last_dir(self.parent.serviceSettingsSection),
            self.trUtf8(u'OpenLP Service Files (*.osz)'))
        else:
            filename = SettingsManager.get_last_dir(
                self.parent.serviceSettingsSection)
        if filename:
            splittedFile = filename.split(u'.')
            if splittedFile[-1] != u'osz':
                filename = filename + u'.osz'
            filename = unicode(filename)
            self.isNew = False
            SettingsManager.set_last_dir(
                self.parent.serviceSettingsSection,
                os.path.split(filename)[0])
            service = []
            servicefile = filename + u'.osd'
            zip = None
            file = None
            try:
                zip = zipfile.ZipFile(unicode(filename), 'w')
                for item in self.serviceItems:
                    service.append({u'serviceitem':item[u'service_item']
                        .get_service_repr()})
                    if item[u'service_item'].uses_file():
                        for frame in item[u'service_item'].get_frames():
                            path_from = unicode(os.path.join(
                                frame[u'path'],
                                frame[u'title']))
                            zip.write(path_from)
                file = open(servicefile, u'wb')
                cPickle.dump(service, file)
                file.close()
                zip.write(servicefile)
            except:
                log.exception(u'Failed to save service to disk')
            finally:
                if file:
                    file.close()
                if zip:
                    zip.close()
            try:
                os.remove(servicefile)
            except:
                pass #if not present do not worry
            name = filename.split(os.path.sep)
            self.serviceName = name[-1]
            self.parent.addRecentFile(filename)
            self.parent.serviceChanged(True, self.serviceName)

    def onQuickSaveService(self):
        self.onSaveService(True)

    def onLoadService(self, lastService=False):
        if lastService:
            filename = SettingsManager.get_last_dir(
                self.parent.serviceSettingsSection)
        else:
            filename = QtGui.QFileDialog.getOpenFileName(
                self, self.trUtf8('Open Service'),
                SettingsManager.get_last_dir(
                self.parent.serviceSettingsSection), u'Services (*.osz)')
        self.loadService(filename)

    def loadService(self, filename=None):
        """
        Load an existing service from disk and rebuild the serviceitems.  All
        files retrieved from the zip file are placed in a temporary directory
        and will only be used for this service.
        """
        if self.parent.serviceNotSaved:
            ret = QtGui.QMessageBox.question(self,
                self.trUtf8('Save Changes to Service?'),
                self.trUtf8('Your current service is unsaved, do you want to '
                            'save the changes before opening a new one?'),
                QtGui.QMessageBox.StandardButtons(
                    QtGui.QMessageBox.Discard |
                    QtGui.QMessageBox.Save),
                QtGui.QMessageBox.Save)
            if ret == QtGui.QMessageBox.Save:
                self.onSaveService()
        if filename is None:
            action = self.sender()
            if isinstance(action, QtGui.QAction):
                filename = action.data().toString()
            else:
                return
        filename = unicode(filename)
        name = filename.split(os.path.sep)
        if filename:
            SettingsManager.set_last_dir(
                self.parent.serviceSettingsSection,
                os.path.split(filename)[0])
            zip = None
            f = None
            try:
                zip = zipfile.ZipFile(unicode(filename))
                for file in zip.namelist():
                    osfile = unicode(QtCore.QDir.toNativeSeparators(file))
                    names = osfile.split(os.path.sep)
                    file_to = os.path.join(self.servicePath,
                        names[len(names) - 1])
                    f = open(file_to, u'wb')
                    f.write(zip.read(file))
                    f.flush()
                    f.close()
                    if file_to.endswith(u'osd'):
                        p_file = file_to
                f = open(p_file, u'r')
                items = cPickle.load(f)
                f.close()
                self.onNewService()
                for item in items:
                    serviceitem = ServiceItem()
                    serviceitem.RenderManager = self.parent.RenderManager
                    serviceitem.set_from_service(item, self.servicePath)
                    self.validateItem(serviceitem)
                    self.addServiceItem(serviceitem)
                try:
                    if os.path.isfile(p_file):
                        os.remove(p_file)
                except:
                    log.exception(u'Failed to remove osd file')
            except:
                log.exception(u'Problem loading a service file')
            finally:
                if f:
                    f.close()
                if zip:
                    zip.close()
        self.isNew = False
        self.serviceName = name[len(name) - 1]
        self.parent.addRecentFile(filename)
        self.parent.serviceChanged(True, self.serviceName)

    def validateItem(self, serviceItem):
        """
        Validates the service item and if the suffix matches an accepted
        one it allows the item to be displayed
        """
        if serviceItem.is_command():
            type = serviceItem._raw_frames[0][u'title'].split(u'.')[1]
            if type not in self.suffixes:
                serviceItem.isValid = False
            if serviceItem.title not in self.viewers:
                serviceItem.isValid = False

    def cleanUp(self):
        """
        Empties the servicePath of temporary files
        """
        for file in os.listdir(self.servicePath):
            file_path = os.path.join(self.servicePath, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except:
                log.exception(u'Failed to clean up servicePath')

    def onThemeComboBoxSelected(self, currentIndex):
        """
        Set the theme for the current service
        """
        self.service_theme = unicode(self.ThemeComboBox.currentText())
        self.parent.RenderManager.set_service_theme(self.service_theme)
        QtCore.QSettings().setValue(
            self.parent.serviceSettingsSection + u'/service theme',
            QtCore.QVariant(self.service_theme))
        self.regenerateServiceItems()

    def regenerateServiceItems(self):
        #force reset of renderer as theme data has changed
        self.parent.RenderManager.themedata = None
        if self.serviceItems:
            tempServiceItems = self.serviceItems
            self.ServiceManagerList.clear()
            self.serviceItems = []
            self.isNew = True
            for item in tempServiceItems:
                self.addServiceItem(
                    item[u'service_item'], False, item[u'expanded'])
            #Set to False as items may have changed rendering
            #does not impact the saved song so True may also be valid
            self.parent.serviceChanged(False, self.serviceName)

    def addServiceItem(self, item, rebuild=False, expand=True, replace=False):
        """
        Add a Service item to the list

        ``item``
            Service Item to be added

        """
        sitem, count = self.findServiceItem()
        item.render()
        if replace:
            item.merge(self.serviceItems[sitem][u'service_item'])
            self.serviceItems[sitem][u'service_item'] = item
            self.repaintServiceList(sitem + 1, 0)
            self.parent.LiveController.replaceServiceManagerItem(item)
        else:
            #nothing selected for dnd
            if self.droppos == 0:
                if isinstance(item, list):
                    for inditem in item:
                        self.serviceItems.append({u'service_item': inditem,
                            u'order': len(self.serviceItems) + 1,
                            u'expanded':expand})
                else:
                    self.serviceItems.append({u'service_item': item,
                        u'order': len(self.serviceItems) + 1,
                        u'expanded':expand})
                self.repaintServiceList(len(self.serviceItems) + 1, 0)
            else:
                self.serviceItems.insert(self.droppos, {u'service_item': item,
                    u'order': self.droppos,
                    u'expanded':expand})
                self.repaintServiceList(self.droppos, 0)
            #if rebuilding list make sure live is fixed.
            if rebuild:
                self.parent.LiveController.replaceServiceManagerItem(item)
        self.droppos = 0
        self.parent.serviceChanged(False, self.serviceName)

    def makePreview(self):
        """
        Send the current item to the Preview slide controller
        """
        item, count = self.findServiceItem()
        self.parent.PreviewController.addServiceManagerItem(
            self.serviceItems[item][u'service_item'], count)

    def getServiceItem(self):
        """
        Send the current item to the Preview slide controller
        """
        item, count = self.findServiceItem()
        if item == -1:
            return False
        else:
            return self.serviceItems[item][u'service_item']

    def makeLive(self):
        """
        Send the current item to the Live slide controller
        """
        item, count = self.findServiceItem()
        if self.serviceItems[item][u'service_item'].isValid:
            self.parent.LiveController.addServiceManagerItem(
                self.serviceItems[item][u'service_item'], count)
            if QtCore.QSettings().value(
                self.parent.generalSettingsSection + u'/auto preview',
                QtCore.QVariant(False)).toBool():
                item += 1
                if self.serviceItems and item < len(self.serviceItems) and \
                    self.serviceItems[item][u'service_item'].is_capable(
                    ItemCapabilities.AllowsPreview):
                        self.parent.PreviewController.addServiceManagerItem(
                            self.serviceItems[item][u'service_item'], 0)
        else:
            QtGui.QMessageBox.critical(self,
                self.trUtf8('Missing Display Handler?'),
                self.trUtf8('Your item cannot be display as '
                            'there is no handler to display it?'),
                QtGui.QMessageBox.StandardButtons(
                    QtGui.QMessageBox.Ok),
                QtGui.QMessageBox.Ok)

    def remoteEdit(self):
        """
        Posts a remote edit message to a plugin to allow item to be edited.
        """
        item, count = self.findServiceItem()
        if self.serviceItems[item][u'service_item']\
            .is_capable(ItemCapabilities.AllowsEdit):
            Receiver.send_message(u'%s_edit' %
                self.serviceItems[item][u'service_item'].name.lower(), u'L:%s' %
                self.serviceItems[item][u'service_item'].editId )

    def findServiceItem(self):
        """
        Finds a ServiceItem in the list
        """
        items = self.ServiceManagerList.selectedItems()
        pos = 0
        count = 0
        for item in items:
            parentitem = item.parent()
            if parentitem is None:
                pos = item.data(0, QtCore.Qt.UserRole).toInt()[0]
            else:
                pos = parentitem.data(0, QtCore.Qt.UserRole).toInt()[0]
                count = item.data(0, QtCore.Qt.UserRole).toInt()[0]
        #adjust for zero based arrays
        pos = pos - 1
        return pos, count

    def dragEnterEvent(self, event):
        """
        Accept Drag events

        ``event``
            Handle of the event pint passed

        """
        event.accept()

    def dropEvent(self, event):
        """
        Receive drop event and trigger an internal event to get the
        plugins to build and push the correct service item
        The drag event payload carries the plugin name

        ``event``
            Handle of the event pint passed
        """
        link = event.mimeData()
        if link.hasText():
            plugin = event.mimeData().text()
            item = self.ServiceManagerList.itemAt(event.pos())
            #ServiceManager started the drag and drop
            if plugin == u'ServiceManager':
                startpos, startCount = self.findServiceItem()
                if item is None:
                    endpos = len(self.serviceItems)
                else:
                    endpos = self._getParentItemData(item) - 1
                if endpos < startpos:
                    newpos = endpos
                else:
                    newpos = endpos + 1
                serviceItem = self.serviceItems[startpos]
                self.serviceItems.remove(serviceItem)
                self.serviceItems.insert(newpos, serviceItem)
                self.repaintServiceList(endpos, startCount)
            else:
                #we are not over anything so drop
                replace = False
                if item == None:
                    self.droppos = len(self.serviceItems)
                else:
                    #we are over somthing so lets investigate
                    pos = self._getParentItemData(item) - 1
                    serviceItem = self.serviceItems[pos]
                    if plugin == serviceItem[u'service_item'].name \
                        and serviceItem[u'service_item'].is_capable(ItemCapabilities.AllowsAdditions):
                            action = self.dndMenu.exec_(QtGui.QCursor.pos())
                            #New action required
                            if action == self.newAction:
                                self.droppos = self._getParentItemData(item)
                            #Append to existing action
                            if action == self.addToAction:
                                self.droppos = self._getParentItemData(item)
                                item.setSelected(True)
                                replace = True
                    else:
                        self.droppos = self._getParentItemData(item)
                Receiver.send_message(u'%s_add_service_item' % plugin, replace)

    def updateThemeList(self, theme_list):
        """
        Called from ThemeManager when the Themes have changed

        ``theme_list``
            A list of current themes to be displayed
        """
        self.ThemeComboBox.clear()
        self.themeMenu.clear()
        self.ThemeComboBox.addItem(u'')
        for theme in theme_list:
            self.ThemeComboBox.addItem(theme)
            action = contextMenuAction(
                self.ServiceManagerList,
                None,
                theme , self.onThemeChangeAction)
            self.themeMenu.addAction(action)
        id = self.ThemeComboBox.findText(self.service_theme,
            QtCore.Qt.MatchExactly)
        # Not Found
        if id == -1:
            id = 0
            self.service_theme = u''
        self.ThemeComboBox.setCurrentIndex(id)
        self.parent.RenderManager.set_service_theme(self.service_theme)
        self.regenerateServiceItems()

    def onThemeChangeAction(self):
        theme = unicode(self.sender().text())
        item, count = self.findServiceItem()
        self.serviceItems[item][u'service_item'].theme = theme
        self.regenerateServiceItems()

    def _getParentItemData(self, item):
        parentitem = item.parent()
        if parentitem is None:
            return item.data(0, QtCore.Qt.UserRole).toInt()[0]
        else:
            return parentitem.data(0, QtCore.Qt.UserRole).toInt()[0]

    def listRequest(self, message=None):
        data = []
        curindex, count = self.findServiceItem()
        if curindex >= 0 and curindex < len(self.serviceItems):
            curitem = self.serviceItems[curindex]
        else:
            curitem = None
        for item in self.serviceItems:
            service_item = item[u'service_item']
            data_item = {}
            data_item[u'title'] = unicode(service_item.title)
            data_item[u'plugin'] = unicode(service_item.name)
            data_item[u'notes'] = unicode(service_item.notes)
            data_item[u'selected'] = (item == curitem)
            data.append(data_item)
        Receiver.send_message(u'servicemanager_list_response', data)
