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
import logging

from PyQt5 import QtCore, QtGui, QtWidgets

from openlp.core.common.i18n import UiStrings, translate, get_natural_key
from openlp.core.common.path import path_to_str, str_to_path
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.lib import MediaManagerItem, ItemCapabilities, ServiceItemContext, \
    build_icon, check_item_selected, create_thumb, validate_thumb
from openlp.core.lib.ui import critical_error_message_box, create_horizontal_adjusting_combo_box
from openlp.core.ui.icons import UiIcons
from openlp.plugins.presentations.lib import MessageListener
from openlp.plugins.presentations.lib.pdfcontroller import PDF_CONTROLLER_FILETYPES

log = logging.getLogger(__name__)


class PresentationMediaItem(MediaManagerItem):
    """
    This is the Presentation media manager item for Presentation Items. It can present files using Openoffice and
    Powerpoint
    """
    presentations_go_live = QtCore.pyqtSignal(list)
    presentations_add_to_service = QtCore.pyqtSignal(list)
    log.info('Presentations Media Item loaded')

    def __init__(self, parent, plugin, controllers):
        """
        Constructor. Setup defaults
        """
        self.icon_path = 'presentations/presentation'
        self.controllers = controllers
        super(PresentationMediaItem, self).__init__(parent, plugin)

    def retranslateUi(self):
        """
        The name of the plugin media displayed in UI
        """
        self.on_new_prompt = translate('PresentationPlugin.MediaItem', 'Select Presentation(s)')
        self.automatic = translate('PresentationPlugin.MediaItem', 'Automatic')
        self.display_type_label.setText(translate('PresentationPlugin.MediaItem', 'Present using:'))

    def setup_item(self):
        """
        Do some additional setup.
        """
        self.presentations_go_live.connect(self.go_live_remote)
        self.presentations_add_to_service.connect(self.add_to_service_remote)
        self.message_listener = MessageListener(self)
        self.has_search = True
        self.single_service_item = False
        Registry().register_function('mediaitem_presentation_rebuild', self.populate_display_types)
        Registry().register_function('mediaitem_suffixes', self.build_file_mask_string)
        # Allow DnD from the desktop
        self.list_view.activateDnD()

    def build_file_mask_string(self):
        """
        Build the list of file extensions to be used in the Open file dialog.
        """
        file_type_string = ''
        for controller in self.controllers:
            if self.controllers[controller].enabled():
                file_types = self.controllers[controller].supports + self.controllers[controller].also_supports
                for file_type in file_types:
                    if file_type not in file_type_string:
                        file_type_string += '*.{text} '.format(text=file_type)
                        self.service_manager.supported_suffixes(file_type)
        self.on_new_file_masks = translate('PresentationPlugin.MediaItem',
                                           'Presentations ({text})').format(text=file_type_string)

    def required_icons(self):
        """
        Set which icons the media manager tab should show.
        """
        MediaManagerItem.required_icons(self)
        self.has_file_icon = True
        self.has_new_icon = False
        self.has_edit_icon = False

    def add_end_header_bar(self):
        """
        Display custom media manager items for presentations.
        """
        self.presentation_widget = QtWidgets.QWidget(self)
        self.presentation_widget.setObjectName('presentation_widget')
        self.display_layout = QtWidgets.QFormLayout(self.presentation_widget)
        self.display_layout.setContentsMargins(self.display_layout.spacing(), self.display_layout.spacing(),
                                               self.display_layout.spacing(), self.display_layout.spacing())
        self.display_layout.setObjectName('display_layout')
        self.display_type_label = QtWidgets.QLabel(self.presentation_widget)
        self.display_type_label.setObjectName('display_type_label')
        self.display_type_combo_box = create_horizontal_adjusting_combo_box(self.presentation_widget,
                                                                            'display_type_combo_box')
        self.display_type_label.setBuddy(self.display_type_combo_box)
        self.display_layout.addRow(self.display_type_label, self.display_type_combo_box)
        # Add the Presentation widget to the page layout.
        self.page_layout.addWidget(self.presentation_widget)

    def initialise(self):
        """
        Populate the media manager tab
        """
        self.list_view.setIconSize(QtCore.QSize(88, 50))
        file_paths = Settings().value(self.settings_section + '/presentations files')
        self.load_list([path_to_str(path) for path in file_paths], initial_load=True)
        self.populate_display_types()

    def populate_display_types(self):
        """
        Load the combobox with the enabled presentation controllers, allowing user to select a specific app if settings
        allow.
        """
        self.display_type_combo_box.clear()
        for item in self.controllers:
            # For PDF reload backend, since it can have changed
            if self.controllers[item].name == 'Pdf':
                self.controllers[item].check_available()
            # load the drop down selection
            if self.controllers[item].enabled():
                self.display_type_combo_box.addItem(item)
        if self.display_type_combo_box.count() > 1:
            self.display_type_combo_box.insertItem(0, self.automatic, userData='automatic')
            self.display_type_combo_box.setCurrentIndex(0)
        if Settings().value(self.settings_section + '/override app') == QtCore.Qt.Checked:
            self.presentation_widget.show()
        else:
            self.presentation_widget.hide()

    def load_list(self, file_paths, target_group=None, initial_load=False):
        """
        Add presentations into the media manager. This is called both on initial load of the plugin to populate with
        existing files, and when the user adds new files via the media manager.

        :param list[openlp.core.common.path.Path] file_paths: List of file paths to add to the media manager.
        """
        file_paths = [str_to_path(filename) for filename in file_paths]
        current_paths = self.get_file_list()
        titles = [file_path.name for file_path in current_paths]
        self.application.set_busy_cursor()
        if not initial_load:
            self.main_window.display_progress_bar(len(file_paths))
        # Sort the presentations by its filename considering language specific characters.
        file_paths.sort(key=lambda file_path: get_natural_key(file_path.name))
        for file_path in file_paths:
            if not initial_load:
                self.main_window.increment_progress_bar()
            if current_paths.count(file_path) > 0:
                continue
            file_name = file_path.name
            if not file_path.exists():
                item_name = QtWidgets.QListWidgetItem(file_name)
                item_name.setIcon(UiIcons().delete)
                item_name.setData(QtCore.Qt.UserRole, path_to_str(file_path))
                item_name.setToolTip(str(file_path))
                self.list_view.addItem(item_name)
            else:
                if titles.count(file_name) > 0:
                    if not initial_load:
                        critical_error_message_box(translate('PresentationPlugin.MediaItem', 'File Exists'),
                                                   translate('PresentationPlugin.MediaItem',
                                                             'A presentation with that filename already exists.'))
                    continue
                controller_name = self.find_controller_by_type(file_path)
                if controller_name:
                    controller = self.controllers[controller_name]
                    doc = controller.add_document(file_path)
                    thumbnail_path = doc.get_thumbnail_folder() / 'icon.png'
                    preview_path = doc.get_thumbnail_path(1, True)
                    if not preview_path and not initial_load:
                        doc.load_presentation()
                        preview_path = doc.get_thumbnail_path(1, True)
                    doc.close_presentation()
                    if not (preview_path and preview_path.exists()):
                        icon = UiIcons().delete
                    else:
                        if validate_thumb(preview_path, thumbnail_path):
                            icon = build_icon(thumbnail_path)
                        else:
                            icon = create_thumb(preview_path, thumbnail_path)
                else:
                    if initial_load:
                        icon = UiIcons().delete
                    else:
                        critical_error_message_box(UiStrings().UnsupportedFile,
                                                   translate('PresentationPlugin.MediaItem',
                                                             'This type of presentation is not supported.'))
                        continue
                item_name = QtWidgets.QListWidgetItem(file_name)
                item_name.setData(QtCore.Qt.UserRole, path_to_str(file_path))
                item_name.setIcon(icon)
                item_name.setToolTip(str(file_path))
                self.list_view.addItem(item_name)
        if not initial_load:
            self.main_window.finished_progress_bar()
        self.application.set_normal_cursor()

    def on_delete_click(self):
        """
        Remove a presentation item from the list.
        """
        if check_item_selected(self.list_view, UiStrings().SelectDelete):
            items = self.list_view.selectedIndexes()
            row_list = [item.row() for item in items]
            row_list.sort(reverse=True)
            self.application.set_busy_cursor()
            self.main_window.display_progress_bar(len(row_list))
            for item in items:
                file_path = str_to_path(item.data(QtCore.Qt.UserRole))
                self.clean_up_thumbnails(file_path)
                self.main_window.increment_progress_bar()
            self.main_window.finished_progress_bar()
            for row in row_list:
                self.list_view.takeItem(row)
            Settings().setValue(self.settings_section + '/presentations files', self.get_file_list())
            self.application.set_normal_cursor()

    def clean_up_thumbnails(self, file_path, clean_for_update=False):
        """
        Clean up the files created such as thumbnails

        :param openlp.core.common.path.Path file_path: File path of the presentation to clean up after
        :param bool clean_for_update: Only clean thumbnails if update is needed
        :rtype: None
        """
        for cidx in self.controllers:
            file_ext = file_path.suffix[1:]
            if file_ext in self.controllers[cidx].supports or file_ext in self.controllers[cidx].also_supports:
                doc = self.controllers[cidx].add_document(file_path)
                if clean_for_update:
                    thumb_path = doc.get_thumbnail_path(1, True)
                    if not thumb_path or not file_path.exists() or \
                            thumb_path.stat().st_mtime < file_path.stat().st_mtime:
                        doc.presentation_deleted()
                else:
                    doc.presentation_deleted()
                doc.close_presentation()

    def generate_slide_data(self, service_item, item=None, xml_version=False, remote=False,
                            context=ServiceItemContext.Service, file_path=None):
        """
        Generate the slide data. Needs to be implemented by the plugin.

        :param service_item: The service item to be built on
        :param item: The Song item to be used
        :param xml_version: The xml version (not used)
        :param remote: Triggered from remote
        :param context: Why is it being generated
        """
        if item:
            items = [item]
        else:
            items = self.list_view.selectedItems()
            if len(items) > 1:
                return False
        if file_path is None:
            file_path = str_to_path(items[0].data(QtCore.Qt.UserRole))
        file_type = file_path.suffix.lower()[1:]
        if not self.display_type_combo_box.currentText():
            return False
        service_item.add_capability(ItemCapabilities.CanEditTitle)
        if file_type in PDF_CONTROLLER_FILETYPES and context != ServiceItemContext.Service:
            service_item.add_capability(ItemCapabilities.CanMaintain)
            service_item.add_capability(ItemCapabilities.CanPreview)
            service_item.add_capability(ItemCapabilities.CanLoop)
            service_item.add_capability(ItemCapabilities.CanAppend)
            service_item.name = 'images'
            # force a nonexistent theme
            service_item.theme = -1
            for bitem in items:
                if file_path is None:
                    file_path = str_to_path(bitem.data(QtCore.Qt.UserRole))
                path, file_name = file_path.parent, file_path.name
                service_item.title = file_name
                if file_path.exists():
                    processor = self.find_controller_by_type(file_path)
                    if not processor:
                        return False
                    controller = self.controllers[processor]
                    service_item.processor = None
                    doc = controller.add_document(file_path)
                    if doc.get_thumbnail_path(1, True) is None or \
                            not (doc.get_temp_folder() / 'mainslide001.png').is_file():
                        doc.load_presentation()
                    i = 1
                    image_path = doc.get_temp_folder() / 'mainslide{number:0>3d}.png'.format(number=i)
                    thumbnail_path = doc.get_thumbnail_folder() / 'slide{number:d}.png'.format(number=i)
                    while image_path.is_file():
                        service_item.add_from_image(str(image_path), file_name, thumbnail=str(thumbnail_path))
                        i += 1
                        image_path = doc.get_temp_folder() / 'mainslide{number:0>3d}.png'.format(number=i)
                        thumbnail_path = doc.get_thumbnail_folder() / 'slide{number:d}.png'.format(number=i)
                    service_item.add_capability(ItemCapabilities.HasThumbnails)
                    doc.close_presentation()
                    return True
                else:
                    # File is no longer present
                    if not remote:
                        critical_error_message_box(translate('PresentationPlugin.MediaItem', 'Missing Presentation'),
                                                   translate('PresentationPlugin.MediaItem',
                                                             'The presentation {name} no longer exists.'
                                                             ).format(name=file_path))
                    return False
        else:
            service_item.processor = self.display_type_combo_box.currentText()
            service_item.add_capability(ItemCapabilities.ProvidesOwnDisplay)
            for bitem in items:
                file_path = str_to_path(bitem.data(QtCore.Qt.UserRole))
                path, file_name = file_path.parent, file_path.name
                service_item.title = file_name
                if file_path.exists():
                    if self.display_type_combo_box.itemData(self.display_type_combo_box.currentIndex()) == 'automatic':
                        service_item.processor = self.find_controller_by_type(file_path)
                        if not service_item.processor:
                            return False
                    controller = self.controllers[service_item.processor]
                    doc = controller.add_document(file_path)
                    if doc.get_thumbnail_path(1, True) is None:
                        doc.load_presentation()
                    i = 1
                    thumbnail_path = doc.get_thumbnail_path(i, True)
                    if thumbnail_path:
                        # Get titles and notes
                        titles, notes = doc.get_titles_and_notes()
                        service_item.add_capability(ItemCapabilities.HasDisplayTitle)
                        if notes.count('') != len(notes):
                            service_item.add_capability(ItemCapabilities.HasNotes)
                        service_item.add_capability(ItemCapabilities.HasThumbnails)
                        while thumbnail_path:
                            # Use title and note if available
                            title = ''
                            if titles and len(titles) >= i:
                                title = titles[i - 1]
                            note = ''
                            if notes and len(notes) >= i:
                                note = notes[i - 1]
                            service_item.add_from_command(str(path), file_name, str(thumbnail_path), title, note)
                            i += 1
                            thumbnail_path = doc.get_thumbnail_path(i, True)
                        doc.close_presentation()
                        return True
                    else:
                        # File is no longer present
                        if not remote:
                            critical_error_message_box(translate('PresentationPlugin.MediaItem',
                                                                 'Missing Presentation'),
                                                       translate('PresentationPlugin.MediaItem',
                                                                 'The presentation {name} is incomplete, '
                                                                 'please reload.').format(name=file_path))
                        return False
                else:
                    # File is no longer present
                    if not remote:
                        critical_error_message_box(translate('PresentationPlugin.MediaItem', 'Missing Presentation'),
                                                   translate('PresentationPlugin.MediaItem',
                                                             'The presentation {name} no longer exists.'
                                                             ).format(name=file_path))
                    return False

    def find_controller_by_type(self, file_path):
        """
        Determine the default application controller to use for the selected file type. This is used if "Automatic" is
        set as the preferred controller. Find the first (alphabetic) enabled controller which "supports" the extension.
        If none found, then look for a controller which "also supports" it instead.

        :param openlp.core.common.path.Path file_path: The file path
        :return: The default application controller for this file type, or None if not supported
        :rtype: PresentationController
        """
        file_type = file_path.suffix[1:]
        if not file_type:
            return None
        for controller in self.controllers:
            if self.controllers[controller].enabled():
                if file_type in self.controllers[controller].supports:
                    return controller
        for controller in self.controllers:
            if self.controllers[controller].enabled():
                if file_type in self.controllers[controller].also_supports:
                    return controller
        return None

    def search(self, string, show_error):
        """
        Search in files

        :param string: name to be found
        :param show_error: not used
        :return:
        """
        file_paths = Settings().value(self.settings_section + '/presentations files')
        results = []
        string = string.lower()
        for file_path in file_paths:
            file_name = file_path.name
            if file_name.lower().find(string) > -1:
                results.append([path_to_str(file_path), file_name])
        return results
