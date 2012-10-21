# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2012 Raoul Snyman                                        #
# Portions copyright (c) 2008-2012 Tim Bentley, Gerald Britton, Jonathan      #
# Corwin, Samuel Findlay, Michael Gorven, Scott Guerrieri, Matthias Hub,      #
# Christian Richter, Philip Ridout, Simon Scudder, Jeffrey Smith,             #
# Maikel Stuivenberg, Martin Thompson, Jon Tibble, Dave Warnock,              #
# Tibble, Dave Warnock, Frode Woldsund                                        #
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

from PyQt4 import QtCore, QtGui
from sqlalchemy.sql import or_, func

from openlp.core.lib import MediaManagerItem, Receiver, ItemCapabilities, \
    check_item_selected, translate
from openlp.core.lib.ui import UiStrings
from openlp.core.lib.settings import Settings
from openlp.plugins.custom.forms import EditCustomForm
from openlp.plugins.custom.lib import CustomXMLParser
from openlp.plugins.custom.lib.db import CustomSlide

log = logging.getLogger(__name__)

class CustomSearch(object):
    """
    An enumeration for custom search methods.
    """
    Titles = 1
    Themes = 2


class CustomMediaItem(MediaManagerItem):
    """
    This is the custom media manager item for Custom Slides.
    """
    log.info(u'Custom Media Item loaded')

    def __init__(self, parent, plugin, icon):
        self.IconPath = u'custom/custom'
        MediaManagerItem.__init__(self, parent, plugin, icon)
        self.edit_custom_form = EditCustomForm(self, self.plugin.formParent,
            self.plugin.manager)
        self.singleServiceItem = False
        self.quickPreviewAllowed = True
        self.hasSearch = True
        # Holds information about whether the edit is remotly triggered and
        # which Custom is required.
        self.remoteCustom = -1
        self.manager = plugin.manager

    def addEndHeaderBar(self):
        self.toolbar.addSeparator()
        self.addSearchToToolBar()
        # Signals and slots
        QtCore.QObject.connect(self.searchTextEdit,
            QtCore.SIGNAL(u'cleared()'), self.onClearTextButtonClick)
        QtCore.QObject.connect(self.searchTextEdit,
            QtCore.SIGNAL(u'searchTypeChanged(int)'),
            self.onSearchTextButtonClicked)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'custom_edit'), self.onRemoteEdit)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'custom_edit_clear'), self.onRemoteEditClear)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'custom_load_list'), self.loadList)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'custom_preview'), self.onPreviewClick)

    def retranslateUi(self):
        self.searchTextLabel.setText(u'%s:' % UiStrings().Search)
        self.searchTextButton.setText(UiStrings().Search)

    def initialise(self):
        self.searchTextEdit.setSearchTypes([
            (CustomSearch.Titles, u':/songs/song_search_title.png',
            translate('SongsPlugin.MediaItem', 'Titles'),
            translate('SongsPlugin.MediaItem', 'Search Titles...')),
            (CustomSearch.Themes, u':/slides/slide_theme.png',
            UiStrings().Themes, UiStrings().SearchThemes)
        ])
        self.loadList(self.manager.get_all_objects(
            CustomSlide, order_by_ref=CustomSlide.title))
        self.searchTextEdit.setCurrentSearchType(Settings().value(
            u'%s/last search type' % self.settingsSection,
            QtCore.QVariant(CustomSearch.Titles)).toInt()[0])

    def loadList(self, custom_slides):
        # Sort out what custom we want to select after loading the list.
        self.saveAutoSelectId()
        self.listView.clear()
        custom_slides.sort()
        for custom_slide in custom_slides:
            custom_name = QtGui.QListWidgetItem(custom_slide.title)
            custom_name.setData(
                QtCore.Qt.UserRole, QtCore.QVariant(custom_slide.id))
            self.listView.addItem(custom_name)
            # Auto-select the custom.
            if custom_slide.id == self.autoSelectId:
                self.listView.setCurrentItem(custom_name)
        self.autoSelectId = -1
        # Called to redisplay the custom list screen edith from a search
        # or from the exit of the Custom edit dialog. If remote editing is
        # active trigger it and clean up so it will not update again.
        if self.remoteTriggered == u'L':
            self.onAddClick()
        if self.remoteTriggered == u'P':
            self.onPreviewClick()
        self.onRemoteEditClear()

    def onNewClick(self):
        self.edit_custom_form.loadCustom(0)
        self.edit_custom_form.exec_()
        self.onClearTextButtonClick()
        self.onSelectionChange()

    def onRemoteEditClear(self):
        self.remoteTriggered = None
        self.remoteCustom = -1

    def onRemoteEdit(self, message):
        """
        Called by ServiceManager or SlideController by event passing
        the custom Id in the payload along with an indicator to say which
        type of display is required.
        """
        remote_type, custom_id = message.split(u':')
        custom_id = int(custom_id)
        valid = self.manager.get_object(CustomSlide, custom_id)
        if valid:
            self.remoteCustom = custom_id
            self.remoteTriggered = remote_type
            self.edit_custom_form.loadCustom(custom_id, (remote_type == u'P'))
            self.edit_custom_form.exec_()
            self.autoSelectId = -1
            self.onSearchTextButtonClicked()

    def onEditClick(self):
        """
        Edit a custom item
        """
        if check_item_selected(self.listView, UiStrings().SelectEdit):
            item = self.listView.currentItem()
            item_id = (item.data(QtCore.Qt.UserRole)).toInt()[0]
            self.edit_custom_form.loadCustom(item_id, False)
            self.edit_custom_form.exec_()
            self.autoSelectId = -1
            self.onSearchTextButtonClicked()

    def onDeleteClick(self):
        """
        Remove a custom item from the list and database
        """
        if check_item_selected(self.listView, UiStrings().SelectDelete):
            items = self.listView.selectedIndexes()
            if QtGui.QMessageBox.question(self,
                UiStrings().ConfirmDelete,
                translate('CustomPlugin.MediaItem',
                'Are you sure you want to delete the %n selected custom'
                ' slide(s)?', '',
                QtCore.QCoreApplication.CodecForTr, len(items)),
                QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Yes |
                QtGui.QMessageBox.No),
                QtGui.QMessageBox.Yes) == QtGui.QMessageBox.No:
                return
            row_list = [item.row() for item in self.listView.selectedIndexes()]
            row_list.sort(reverse=True)
            id_list = [(item.data(QtCore.Qt.UserRole)).toInt()[0]
                for item in self.listView.selectedIndexes()]
            for id in id_list:
                self.plugin.manager.delete_object(CustomSlide, id)
            self.onSearchTextButtonClicked()

    def onFocus(self):
        self.searchTextEdit.setFocus()

    def generateSlideData(self, service_item, item=None, xmlVersion=False,
        remote=False):
        item_id = self._getIdOfItemToGenerate(item, self.remoteCustom)
        service_item.add_capability(ItemCapabilities.CanEdit)
        service_item.add_capability(ItemCapabilities.CanPreview)
        service_item.add_capability(ItemCapabilities.CanLoop)
        service_item.add_capability(ItemCapabilities.CanSoftBreak)
        customSlide = self.plugin.manager.get_object(CustomSlide, item_id)
        title = customSlide.title
        credit = customSlide.credits
        service_item.edit_id = item_id
        theme = customSlide.theme_name
        if theme:
            service_item.theme = theme
        custom_xml = CustomXMLParser(customSlide.text)
        verse_list = custom_xml.get_verses()
        raw_slides = [verse[1] for verse in verse_list]
        service_item.title = title
        for slide in raw_slides:
            service_item.add_from_text(slide)
        if Settings().value(self.settingsSection + u'/display footer',
            QtCore.QVariant(True)).toBool() or credit:
            service_item.raw_footer.append(u' '.join([title, credit]))
        else:
            service_item.raw_footer.append(u'')
        return True

    def onSearchTextButtonClicked(self):
        # Save the current search type to the configuration.
        Settings().setValue(u'%s/last search type' %
            self.settingsSection,
            QtCore.QVariant(self.searchTextEdit.currentSearchType()))
        # Reload the list considering the new search type.
        search_keywords = unicode(self.searchTextEdit.displayText())
        search_results = []
        search_type = self.searchTextEdit.currentSearchType()
        if search_type == CustomSearch.Titles:
            log.debug(u'Titles Search')
            search_results = self.plugin.manager.get_all_objects(CustomSlide,
                CustomSlide.title.like(u'%' + self.whitespace.sub(u' ',
                search_keywords) + u'%'), order_by_ref=CustomSlide.title)
            self.loadList(search_results)
        elif search_type == CustomSearch.Themes:
            log.debug(u'Theme Search')
            search_results = self.plugin.manager.get_all_objects(CustomSlide,
                CustomSlide.theme_name.like(u'%' + self.whitespace.sub(u' ',
                search_keywords) + u'%'), order_by_ref=CustomSlide.title)
            self.loadList(search_results)
        self.checkSearchResult()

    def onSearchTextEditChanged(self, text):
        """
        If search as type enabled invoke the search on each key press.
        If the Title is being searched do not start until 2 characters
        have been entered.
        """
        search_length = 2
        if len(text) > search_length:
            self.onSearchTextButtonClicked()
        elif not text:
            self.onClearTextButtonClick()

    def onClearTextButtonClick(self):
        """
        Clear the search text.
        """
        self.searchTextEdit.clear()
        self.onSearchTextButtonClicked()

    def search(self, string, showError):
        search_results = self.manager.get_all_objects(CustomSlide,
            or_(func.lower(CustomSlide.title).like(u'%' +
            string.lower() + u'%'),
            func.lower(CustomSlide.text).like(u'%' +
            string.lower() + u'%')),
            order_by_ref=CustomSlide.title)
        return [[custom.id, custom.title] for custom in search_results]

