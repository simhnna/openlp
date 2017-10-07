# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2017 OpenLP Developers                                   #
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
The Theme Manager manages adding, deleteing and modifying of themes.
"""
import os
import zipfile
from xml.etree.ElementTree import ElementTree, XML

from PyQt5 import QtCore, QtGui, QtWidgets

from openlp.core.common import delete_file
from openlp.core.common.applocation import AppLocation
from openlp.core.common.i18n import UiStrings, translate, get_locale_key
from openlp.core.common.mixins import OpenLPMixin, RegistryMixin
from openlp.core.common.path import Path, copyfile, create_paths, path_to_str, rmtree
from openlp.core.common.registry import Registry, RegistryProperties
from openlp.core.common.settings import Settings
from openlp.core.lib import ImageSource, ValidationError, get_text_file_string, build_icon, \
    check_item_selected, create_thumb, validate_thumb
from openlp.core.lib.theme import Theme, BackgroundType
from openlp.core.lib.ui import critical_error_message_box, create_widget_action
from openlp.core.ui import FileRenameForm, ThemeForm
from openlp.core.ui.lib import OpenLPToolbar
from openlp.core.ui.lib.filedialog import FileDialog


class Ui_ThemeManager(object):
    """
    UI part of the Theme Manager
    """
    def setup_ui(self, widget):
        """
        Define the UI
        :param widget: The screen object the the dialog is to be attached to.
        """
        # start with the layout
        self.layout = QtWidgets.QVBoxLayout(widget)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setObjectName('layout')
        self.toolbar = OpenLPToolbar(widget)
        self.toolbar.setObjectName('toolbar')
        self.toolbar.add_toolbar_action('newTheme',
                                        text=UiStrings().NewTheme, icon=':/themes/theme_new.png',
                                        tooltip=translate('OpenLP.ThemeManager', 'Create a new theme.'),
                                        triggers=self.on_add_theme)
        self.toolbar.add_toolbar_action('editTheme',
                                        text=translate('OpenLP.ThemeManager', 'Edit Theme'),
                                        icon=':/themes/theme_edit.png',
                                        tooltip=translate('OpenLP.ThemeManager', 'Edit a theme.'),
                                        triggers=self.on_edit_theme)
        self.delete_toolbar_action = self.toolbar.add_toolbar_action('delete_theme',
                                                                     text=translate('OpenLP.ThemeManager',
                                                                                    'Delete Theme'),
                                                                     icon=':/general/general_delete.png',
                                                                     tooltip=translate('OpenLP.ThemeManager',
                                                                                       'Delete a theme.'),
                                                                     triggers=self.on_delete_theme)
        self.toolbar.addSeparator()
        self.toolbar.add_toolbar_action('importTheme',
                                        text=translate('OpenLP.ThemeManager', 'Import Theme'),
                                        icon=':/general/general_import.png',
                                        tooltip=translate('OpenLP.ThemeManager', 'Import a theme.'),
                                        triggers=self.on_import_theme)
        self.toolbar.add_toolbar_action('exportTheme',
                                        text=translate('OpenLP.ThemeManager', 'Export Theme'),
                                        icon=':/general/general_export.png',
                                        tooltip=translate('OpenLP.ThemeManager', 'Export a theme.'),
                                        triggers=self.on_export_theme)
        self.layout.addWidget(self.toolbar)
        self.theme_widget = QtWidgets.QWidgetAction(self.toolbar)
        self.theme_widget.setObjectName('theme_widget')
        # create theme manager list
        self.theme_list_widget = QtWidgets.QListWidget(widget)
        self.theme_list_widget.setAlternatingRowColors(True)
        self.theme_list_widget.setIconSize(QtCore.QSize(88, 50))
        self.theme_list_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.theme_list_widget.setObjectName('theme_list_widget')
        self.layout.addWidget(self.theme_list_widget)
        self.theme_list_widget.customContextMenuRequested.connect(self.context_menu)
        # build the context menu
        self.menu = QtWidgets.QMenu()
        self.edit_action = create_widget_action(self.menu,
                                                text=translate('OpenLP.ThemeManager', '&Edit Theme'),
                                                icon=':/themes/theme_edit.png', triggers=self.on_edit_theme)
        self.copy_action = create_widget_action(self.menu,
                                                text=translate('OpenLP.ThemeManager', '&Copy Theme'),
                                                icon=':/themes/theme_edit.png', triggers=self.on_copy_theme)
        self.rename_action = create_widget_action(self.menu,
                                                  text=translate('OpenLP.ThemeManager', '&Rename Theme'),
                                                  icon=':/themes/theme_edit.png', triggers=self.on_rename_theme)
        self.delete_action = create_widget_action(self.menu,
                                                  text=translate('OpenLP.ThemeManager', '&Delete Theme'),
                                                  icon=':/general/general_delete.png', triggers=self.on_delete_theme)
        self.menu.addSeparator()
        self.global_action = create_widget_action(self.menu,
                                                  text=translate('OpenLP.ThemeManager', 'Set As &Global Default'),
                                                  icon=':/general/general_export.png',
                                                  triggers=self.change_global_from_screen)
        self.export_action = create_widget_action(self.menu,
                                                  text=translate('OpenLP.ThemeManager', '&Export Theme'),
                                                  icon=':/general/general_export.png', triggers=self.on_export_theme)
        # Signals
        self.theme_list_widget.doubleClicked.connect(self.change_global_from_screen)
        self.theme_list_widget.currentItemChanged.connect(self.check_list_state)


class ThemeManager(OpenLPMixin, RegistryMixin, QtWidgets.QWidget, Ui_ThemeManager, RegistryProperties):
    """
    Manages the orders of Theme.
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(ThemeManager, self).__init__(parent)
        self.settings_section = 'themes'
        # Variables
        self.theme_list = []
        self.old_background_image_path = None

    def bootstrap_initialise(self):
        """
        process the bootstrap initialise setup request
        """
        self.setup_ui(self)
        self.global_theme = Settings().value(self.settings_section + '/global theme')
        self.build_theme_path()
        self.load_first_time_themes()
        self.upgrade_themes()

    def bootstrap_post_set_up(self):
        """
        process the bootstrap post setup request
        """
        self.theme_form = ThemeForm(self)
        self.theme_form.path = self.theme_path
        self.file_rename_form = FileRenameForm()
        Registry().register_function('theme_update_global', self.change_global_from_tab)
        self.load_themes()

    def upgrade_themes(self):
        """
        Upgrade the xml files to json.

        :rtype: None
        """
        xml_file_paths = AppLocation.get_section_data_path('themes').glob('*/*.xml')
        for xml_file_path in xml_file_paths:
            theme_data = get_text_file_string(xml_file_path)
            theme = self._create_theme_from_xml(theme_data, self.theme_path)
            self._write_theme(theme)
            xml_file_path.unlink()

    def build_theme_path(self):
        """
        Set up the theme path variables

        :rtype: None
        """
        self.theme_path = AppLocation.get_section_data_path(self.settings_section)
        self.thumb_path = self.theme_path / 'thumbnails'
        create_paths(self.theme_path, self.thumb_path)

    def check_list_state(self, item, field=None):
        """
        If Default theme selected remove delete button.
        Note for some reason a dummy field is required.  Nothing is passed!

        :param field:
        :param item: Service Item to process
        """
        if item is None:
            return
        real_theme_name = item.data(QtCore.Qt.UserRole)
        theme_name = item.text()
        # If default theme restrict actions
        if real_theme_name == theme_name:
            self.delete_toolbar_action.setVisible(True)
        else:
            self.delete_toolbar_action.setVisible(False)

    def context_menu(self, point):
        """
        Build the Right Click Context menu and set state depending on the type of theme.

        :param point: The position of the mouse so the correct item can be found.
        """
        item = self.theme_list_widget.itemAt(point)
        if item is None:
            return
        real_theme_name = item.data(QtCore.Qt.UserRole)
        theme_name = str(item.text())
        visible = real_theme_name == theme_name
        self.delete_action.setVisible(visible)
        self.rename_action.setVisible(visible)
        self.global_action.setVisible(visible)
        self.menu.exec(self.theme_list_widget.mapToGlobal(point))

    def change_global_from_tab(self):
        """
        Change the global theme when it is changed through the Themes settings tab
        """
        self.global_theme = Settings().value(self.settings_section + '/global theme')
        self.log_debug('change_global_from_tab {text}'.format(text=self.global_theme))
        for count in range(0, self.theme_list_widget.count()):
            # reset the old name
            item = self.theme_list_widget.item(count)
            old_name = item.text()
            new_name = item.data(QtCore.Qt.UserRole)
            if old_name != new_name:
                self.theme_list_widget.item(count).setText(new_name)
            # Set the new name
            if self.global_theme == new_name:
                name = translate('OpenLP.ThemeManager', '{text} (default)').format(text=new_name)
                self.theme_list_widget.item(count).setText(name)
                self.delete_toolbar_action.setVisible(item not in self.theme_list_widget.selectedItems())

    def change_global_from_screen(self, index=-1):
        """
        Change the global theme when a theme is double clicked upon in the Theme Manager list.

        :param index:
        """
        selected_row = self.theme_list_widget.currentRow()
        for count in range(0, self.theme_list_widget.count()):
            item = self.theme_list_widget.item(count)
            old_name = item.text()
            # reset the old name
            if old_name != item.data(QtCore.Qt.UserRole):
                self.theme_list_widget.item(count).setText(item.data(QtCore.Qt.UserRole))
            # Set the new name
            if count == selected_row:
                self.global_theme = self.theme_list_widget.item(count).text()
                name = translate('OpenLP.ThemeManager', '{text} (default)').format(text=self.global_theme)
                self.theme_list_widget.item(count).setText(name)
                Settings().setValue(self.settings_section + '/global theme', self.global_theme)
                Registry().execute('theme_update_global')
                self._push_themes()

    def on_add_theme(self, field=None):
        """
        Loads a new theme with the default settings and then launches the theme editing form for the user to make
        their customisations.
        :param field:
        """
        theme = Theme()
        theme.set_default_header_footer()
        self.theme_form.theme = theme
        self.theme_form.exec()
        self.load_themes()

    def on_rename_theme(self, field=None):
        """
        Renames an existing theme to a new name
        :param field:
        """
        if self._validate_theme_action(translate('OpenLP.ThemeManager', 'You must select a theme to rename.'),
                                       translate('OpenLP.ThemeManager', 'Rename Confirmation'),
                                       translate('OpenLP.ThemeManager', 'Rename {theme_name} theme?'), False, False):
            item = self.theme_list_widget.currentItem()
            old_theme_name = item.data(QtCore.Qt.UserRole)
            self.file_rename_form.file_name_edit.setText(old_theme_name)
            if self.file_rename_form.exec():
                new_theme_name = self.file_rename_form.file_name_edit.text()
                if old_theme_name == new_theme_name:
                    return
                if self.check_if_theme_exists(new_theme_name):
                    old_theme_data = self.get_theme_data(old_theme_name)
                    self.clone_theme_data(old_theme_data, new_theme_name)
                    self.delete_theme(old_theme_name)
                    for plugin in self.plugin_manager.plugins:
                        if plugin.uses_theme(old_theme_name):
                            plugin.rename_theme(old_theme_name, new_theme_name)
                    self.renderer.update_theme(new_theme_name, old_theme_name)
                    self.load_themes()

    def on_copy_theme(self, field=None):
        """
        Copies an existing theme to a new name
        :param field:
        """
        item = self.theme_list_widget.currentItem()
        old_theme_name = item.data(QtCore.Qt.UserRole)
        self.file_rename_form.file_name_edit.setText(translate('OpenLP.ThemeManager',
                                                               'Copy of {name}',
                                                               'Copy of <theme name>').format(name=old_theme_name))
        if self.file_rename_form.exec(True):
            new_theme_name = self.file_rename_form.file_name_edit.text()
            if self.check_if_theme_exists(new_theme_name):
                theme_data = self.get_theme_data(old_theme_name)
                self.clone_theme_data(theme_data, new_theme_name)

    def clone_theme_data(self, theme_data, new_theme_name):
        """
        Takes a theme and makes a new copy of it as well as saving it.

        :param Theme theme_data: The theme to be used
        :param str new_theme_name: The new theme name of the theme
        :rtype: None
        """
        destination_path = None
        source_path = None
        if theme_data.background_type == 'image' or theme_data.background_type == 'video':
            destination_path = self.theme_path / new_theme_name / theme_data.background_filename.name
            source_path = theme_data.background_filename
        theme_data.theme_name = new_theme_name
        theme_data.extend_image_filename(self.theme_path)
        self.save_theme(theme_data, source_path, destination_path)
        self.load_themes()

    def on_edit_theme(self, field=None):
        """
        Loads the settings for the theme that is to be edited and launches the
        theme editing form so the user can make their changes.
        :param field:
        """
        if check_item_selected(self.theme_list_widget,
                               translate('OpenLP.ThemeManager', 'You must select a theme to edit.')):
            item = self.theme_list_widget.currentItem()
            theme = self.get_theme_data(item.data(QtCore.Qt.UserRole))
            if theme.background_type == 'image' or theme.background_type == 'video':
                self.old_background_image_path = theme.background_filename
            self.theme_form.theme = theme
            self.theme_form.exec(True)
            self.old_background_image_path = None
            self.renderer.update_theme(theme.theme_name)
            self.load_themes()

    def on_delete_theme(self, field=None):
        """
        Delete a theme triggered by the UI.
        :param field:
        """
        if self._validate_theme_action(translate('OpenLP.ThemeManager', 'You must select a theme to delete.'),
                                       translate('OpenLP.ThemeManager', 'Delete Confirmation'),
                                       translate('OpenLP.ThemeManager', 'Delete {theme_name} theme?')):
            item = self.theme_list_widget.currentItem()
            theme = item.text()
            row = self.theme_list_widget.row(item)
            self.theme_list_widget.takeItem(row)
            self.delete_theme(theme)
            self.renderer.update_theme(theme, only_delete=True)
            # As we do not reload the themes, push out the change. Reload the
            # list as the internal lists and events need to be triggered.
            self._push_themes()

    def delete_theme(self, theme):
        """
        Delete a theme.

        :param theme: The theme to delete.
        """
        self.theme_list.remove(theme)
        thumb = '{name}.png'.format(name=theme)
        delete_file(self.theme_path / thumb)
        delete_file(self.thumb_path / thumb)
        try:
            rmtree(self.theme_path / theme)
        except OSError:
            self.log_exception('Error deleting theme {name}'.format(name=theme))

    def on_export_theme(self, checked=None):
        """
        Export the theme to a zip file

        :param bool checked: Sent by the QAction.triggered signal. It's not used in this method.
        :rtype: None
        """
        item = self.theme_list_widget.currentItem()
        if item is None:
            critical_error_message_box(message=translate('OpenLP.ThemeManager', 'You have not selected a theme.'))
            return
        theme_name = item.data(QtCore.Qt.UserRole)
        export_path, filter_used = \
            FileDialog.getSaveFileName(self.main_window,
                                       translate('OpenLP.ThemeManager',
                                                 'Save Theme - ({name})').format(name=theme_name),
                                       Settings().value(self.settings_section + '/last directory export'),
                                       translate('OpenLP.ThemeManager', 'OpenLP Themes (*.otz)'),
                                       translate('OpenLP.ThemeManager', 'OpenLP Themes (*.otz)'))
        self.application.set_busy_cursor()
        if export_path:
            Settings().setValue(self.settings_section + '/last directory export', export_path.parent)
            if self._export_theme(export_path.with_suffix('.otz'), theme_name):
                QtWidgets.QMessageBox.information(self,
                                                  translate('OpenLP.ThemeManager', 'Theme Exported'),
                                                  translate('OpenLP.ThemeManager',
                                                            'Your theme has been successfully exported.'))
        self.application.set_normal_cursor()

    def _export_theme(self, theme_path, theme_name):
        """
        Create the zipfile with the theme contents.

        :param openlp.core.common.path.Path theme_path: Location where the zip file will be placed
        :param str theme_name: The name of the theme to be exported
        :return: The success of creating the zip file
        :rtype: bool
        """
        try:
            with zipfile.ZipFile(str(theme_path), 'w') as theme_zip:
                source_path = self.theme_path / theme_name
                for file_path in source_path.iterdir():
                    theme_zip.write(str(file_path), os.path.join(theme_name, file_path.name))
            return True
        except OSError as ose:
            self.log_exception('Export Theme Failed')
            critical_error_message_box(translate('OpenLP.ThemeManager', 'Theme Export Failed'),
                                       translate('OpenLP.ThemeManager',
                                                 'The theme_name export failed because this error occurred: {err}')
                                       .format(err=ose.strerror))
            if theme_path.exists():
                rmtree(theme_path, True)
            return False

    def on_import_theme(self, checked=None):
        """
        Opens a file dialog to select the theme file(s) to import before attempting to extract OpenLP themes from
        those files. This process will only load version 2 themes.

        :param bool checked: Sent by the QAction.triggered signal. It's not used in this method.
        :rtype: None
        """
        file_paths, filter_used = FileDialog.getOpenFileNames(
            self,
            translate('OpenLP.ThemeManager', 'Select Theme Import File'),
            Settings().value(self.settings_section + '/last directory import'),
            translate('OpenLP.ThemeManager', 'OpenLP Themes (*.otz)'))
        self.log_info('New Themes {file_paths}'.format(file_paths=file_paths))
        if not file_paths:
            return
        self.application.set_busy_cursor()
        for file_path in file_paths:
            self.unzip_theme(file_path, self.theme_path)
        Settings().setValue(self.settings_section + '/last directory import', file_path.parent)
        self.load_themes()
        self.application.set_normal_cursor()

    def load_first_time_themes(self):
        """
        Imports any themes on start up and makes sure there is at least one theme
        """
        self.application.set_busy_cursor()
        theme_paths = AppLocation.get_files(self.settings_section, '.otz')
        for theme_path in theme_paths:
            theme_path = self.theme_path / theme_path
            self.unzip_theme(theme_path, self.theme_path)
            delete_file(theme_path)
        theme_paths = AppLocation.get_files(self.settings_section, '.png')
        # No themes have been found so create one
        if not theme_paths:
            theme = Theme()
            theme.theme_name = UiStrings().Default
            self._write_theme(theme)
            Settings().setValue(self.settings_section + '/global theme', theme.theme_name)
        self.application.set_normal_cursor()

    def load_themes(self):
        """
        Loads the theme lists and triggers updates across the whole system using direct calls or core functions and
        events for the plugins.
        The plugins will call back in to get the real list if they want it.
        """
        self.theme_list = []
        self.theme_list_widget.clear()
        files = AppLocation.get_files(self.settings_section, '.png')
        # Sort the themes by its name considering language specific
        files.sort(key=lambda file_name: get_locale_key(str(file_name)))
        # now process the file list of png files
        for file in files:
            # check to see file is in theme root directory
            theme_path = self.theme_path / file
            if theme_path.exists():
                text_name = theme_path.stem
                if text_name == self.global_theme:
                    name = translate('OpenLP.ThemeManager', '{name} (default)').format(name=text_name)
                else:
                    name = text_name
                thumb = self.thumb_path / '{name}.png'.format(name=text_name)
                item_name = QtWidgets.QListWidgetItem(name)
                if validate_thumb(theme_path, thumb):
                    icon = build_icon(thumb)
                else:
                    icon = create_thumb(str(theme_path), str(thumb))
                item_name.setIcon(icon)
                item_name.setData(QtCore.Qt.UserRole, text_name)
                self.theme_list_widget.addItem(item_name)
                self.theme_list.append(text_name)
        self._push_themes()

    def _push_themes(self):
        """
        Notify listeners that the theme list has been updated
        """
        Registry().execute('theme_update_list', self.get_themes())

    def get_themes(self):
        """
        Return the list of loaded themes
        """
        return self.theme_list

    def get_theme_data(self, theme_name):
        """
        Returns a theme object from a JSON file

        :param str theme_name: Name of the theme to load from file
        :return:  The theme object.
        :rtype: Theme
        """
        theme_name = str(theme_name)
        theme_file_path = self.theme_path / theme_name / '{file_name}.json'.format(file_name=theme_name)
        theme_data = get_text_file_string(theme_file_path)
        if not theme_data:
            self.log_debug('No theme data - using default theme')
            return Theme()
        return self._create_theme_from_json(theme_data, self.theme_path)

    def over_write_message_box(self, theme_name):
        """
        Display a warning box to the user that a theme already exists

        :param theme_name: Name of the theme.
        :return: Confirm if the theme is to be overwritten.
        """
        ret = QtWidgets.QMessageBox.question(self, translate('OpenLP.ThemeManager', 'Theme Already Exists'),
                                             translate('OpenLP.ThemeManager',
                                                       'Theme {name} already exists. '
                                                       'Do you want to replace it?').format(name=theme_name),
                                             defaultButton=QtWidgets.QMessageBox.No)
        return ret == QtWidgets.QMessageBox.Yes

    def unzip_theme(self, file_path, directory_path):
        """
        Unzip the theme, remove the preview file if stored. Generate a new preview file. Check the XML theme version
        and upgrade if necessary.
        :param openlp.core.common.path.Path file_path:
        :param openlp.core.common.path.Path directory_path:
        """
        self.log_debug('Unzipping theme {name}'.format(name=file_path))
        file_xml = None
        abort_import = True
        json_theme = False
        theme_name = ""
        try:
            with zipfile.ZipFile(str(file_path)) as theme_zip:
                json_file = [name for name in theme_zip.namelist() if os.path.splitext(name)[1].lower() == '.json']
                if len(json_file) != 1:
                    # TODO: remove XML handling after the 2.6 release.
                    xml_file = [name for name in theme_zip.namelist() if os.path.splitext(name)[1].lower() == '.xml']
                    if len(xml_file) != 1:
                        self.log_error('Theme contains "{val:d}" theme files'.format(val=len(xml_file)))
                        raise ValidationError
                    xml_tree = ElementTree(element=XML(theme_zip.read(xml_file[0]))).getroot()
                    theme_version = xml_tree.get('version', default=None)
                    if not theme_version or float(theme_version) < 2.0:
                        self.log_error('Theme version is less than 2.0')
                        raise ValidationError
                    theme_name = xml_tree.find('name').text.strip()
                else:
                    new_theme = Theme()
                    new_theme.load_theme(theme_zip.read(json_file[0]).decode("utf-8"))
                    theme_name = new_theme.theme_name
                    json_theme = True
                theme_folder = directory_path / theme_name
                if theme_folder.exists() and not self.over_write_message_box(theme_name):
                    abort_import = True
                    return
                else:
                    abort_import = False
                for zipped_file in theme_zip.namelist():
                    zipped_file_rel_path = Path(zipped_file)
                    split_name = zipped_file_rel_path.parts
                    if split_name[-1] == '' or len(split_name) == 1:
                        # is directory or preview file
                        continue
                    full_name = directory_path / zipped_file_rel_path
                    create_paths(full_name.parent)
                    if zipped_file_rel_path.suffix.lower() == '.xml' or zipped_file_rel_path.suffix.lower() == '.json':
                        file_xml = str(theme_zip.read(zipped_file), 'utf-8')
                        with full_name.open('w', encoding='utf-8') as out_file:
                            out_file.write(file_xml)
                    else:
                        with full_name.open('wb') as out_file:
                            out_file.write(theme_zip.read(zipped_file))
        except (IOError, zipfile.BadZipfile):
            self.log_exception('Importing theme from zip failed {name}'.format(name=file_path))
            raise ValidationError
        except ValidationError:
            critical_error_message_box(translate('OpenLP.ThemeManager', 'Validation Error'),
                                       translate('OpenLP.ThemeManager', 'File is not a valid theme.'))
        finally:
            if not abort_import:
                # As all files are closed, we can create the Theme.
                if file_xml:
                    if json_theme:
                        theme = self._create_theme_from_json(file_xml, self.theme_path)
                    else:
                        theme = self._create_theme_from_xml(file_xml, self.theme_path)
                    self.generate_and_save_image(theme_name, theme)

    def check_if_theme_exists(self, theme_name):
        """
        Check if theme already exists and displays error message

        :param str theme_name:  Name of the Theme to test
        :return: True or False if theme exists
        :rtype: bool
        """
        if (self.theme_path / theme_name).exists():
            critical_error_message_box(
                translate('OpenLP.ThemeManager', 'Validation Error'),
                translate('OpenLP.ThemeManager', 'A theme with this name already exists.'))
            return False
        return True

    def save_theme(self, theme, image_source_path, image_destination_path):
        """
        Called by theme maintenance Dialog to save the theme and to trigger the reload of the theme list

        :param Theme theme: The theme data object.
        :param openlp.core.common.path.Path image_source_path: Where the theme image is currently located.
        :param openlp.core.common.path.Path image_destination_path: Where the Theme Image is to be saved to
        :rtype: None
        """
        self._write_theme(theme, image_source_path, image_destination_path)
        if theme.background_type == BackgroundType.to_string(BackgroundType.Image):
            self.image_manager.update_image_border(path_to_str(theme.background_filename),
                                                   ImageSource.Theme,
                                                   QtGui.QColor(theme.background_border_color))
            self.image_manager.process_updates()

    def _write_theme(self, theme, image_source_path=None, image_destination_path=None):
        """
        Writes the theme to the disk and handles the background image if necessary

        :param Theme theme: The theme data object.
        :param openlp.core.common.path.Path image_source_path: Where the theme image is currently located.
        :param openlp.core.common.path.Path image_destination_path: Where the Theme Image is to be saved to
        :rtype: None
        """
        name = theme.theme_name
        theme_pretty = theme.export_theme(self.theme_path)
        theme_dir = self.theme_path / name
        create_paths(theme_dir)
        theme_path = theme_dir / '{file_name}.json'.format(file_name=name)
        try:
                theme_path.write_text(theme_pretty)
        except IOError:
            self.log_exception('Saving theme to file failed')
        if image_source_path and image_destination_path:
            if self.old_background_image_path and image_destination_path != self.old_background_image_path:
                delete_file(self.old_background_image_path)
            if image_source_path != image_destination_path:
                try:
                    copyfile(image_source_path, image_destination_path)
                except IOError:
                    self.log_exception('Failed to save theme image')
        self.generate_and_save_image(name, theme)

    def generate_and_save_image(self, theme_name, theme):
        """
        Generate and save a preview image

        :param str theme_name: The name of the theme.
        :param theme: The theme data object.
        """
        frame = self.generate_image(theme)
        sample_path_name = self.theme_path / '{file_name}.png'.format(file_name=theme_name)
        if sample_path_name.exists():
            sample_path_name.unlink()
        frame.save(str(sample_path_name), 'png')
        thumb_path = self.thumb_path / '{name}.png'.format(name=theme_name)
        create_thumb(str(sample_path_name), str(thumb_path), False)

    def update_preview_images(self):
        """
        Called to update the themes' preview images.
        """
        self.main_window.display_progress_bar(len(self.theme_list))
        for theme in self.theme_list:
            self.main_window.increment_progress_bar()
            self.generate_and_save_image(theme, self.get_theme_data(theme))
        self.main_window.finished_progress_bar()
        self.load_themes()

    def generate_image(self, theme_data, force_page=False):
        """
        Call the renderer to build a Sample Image

        :param theme_data: The theme to generated a preview for.
        :param force_page: Flag to tell message lines per page need to be generated.
        """
        return self.renderer.generate_preview(theme_data, force_page)

    @staticmethod
    def _create_theme_from_xml(theme_xml, image_path):
        """
        Return a theme object using information parsed from XML

        :param theme_xml: The Theme data object.
        :param openlp.core.common.path.Path image_path: Where the theme image is stored
        :return: Theme data.
        :rtype: Theme
        """
        theme = Theme()
        theme.parse(theme_xml)
        theme.extend_image_filename(image_path)
        return theme

    def _create_theme_from_json(self, theme_json, image_path):
        """
        Return a theme object using information parsed from JSON

        :param theme_json: The Theme data object.
        :param openlp.core.common.path.Path image_path: Where the theme image is stored
        :return: Theme data.
        :rtype: Theme
        """
        theme = Theme()
        theme.load_theme(theme_json, self.theme_path)
        theme.extend_image_filename(image_path)
        return theme

    def _validate_theme_action(self, select_text, confirm_title, confirm_text, test_plugin=True, confirm=True):
        """
        Check to see if theme has been selected and the destructive action is allowed.

        :param select_text: Text for message box if no item selected.
        :param confirm_title: Confirm message title to be displayed.
        :param confirm_text: Confirm message text to be displayed.
        :param test_plugin: Do we check the plugins for theme usage.
        :param confirm: Do we display a confirm box before run checks.
        :return: True or False depending on the validity.
        """
        self.global_theme = Settings().value(self.settings_section + '/global theme')
        if check_item_selected(self.theme_list_widget, select_text):
            item = self.theme_list_widget.currentItem()
            theme = item.text()
            # confirm deletion
            if confirm:
                answer = QtWidgets.QMessageBox.question(
                    self, confirm_title, confirm_text.format(theme_name=theme),
                    defaultButton=QtWidgets.QMessageBox.No)
                if answer == QtWidgets.QMessageBox.No:
                    return False
            # should be the same unless default
            if theme != item.data(QtCore.Qt.UserRole):
                critical_error_message_box(
                    message=translate('OpenLP.ThemeManager', 'You are unable to delete the default theme.'))
                return False
            # check for use in the system else where.
            if test_plugin:
                plugin_usage = ""
                for plugin in self.plugin_manager.plugins:
                    used_count = plugin.uses_theme(theme)
                    if used_count:
                        plugin_usage = "{plug}{text}".format(plug=plugin_usage,
                                                             text=(translate('OpenLP.ThemeManager',
                                                                             '{count} time(s) by {plugin}'
                                                                             ).format(name=used_count,
                                                                                      plugin=plugin.name)))
                        plugin_usage = "{text}\n".format(text=plugin_usage)
                if plugin_usage:
                    critical_error_message_box(translate('OpenLP.ThemeManager', 'Unable to delete theme'),
                                               translate('OpenLP.ThemeManager',
                                                         'Theme is currently used \n\n{text}'
                                                         ).format(text=plugin_usage))

                    return False
            return True
        return False
