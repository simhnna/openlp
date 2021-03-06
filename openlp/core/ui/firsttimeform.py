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
"""
This module contains the first time wizard.
"""
import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from configparser import ConfigParser, MissingSectionHeaderError, NoOptionError, NoSectionError
from tempfile import gettempdir

from PyQt5 import QtCore, QtWidgets

from openlp.core.common import clean_button_text, trace_error_handler
from openlp.core.common.applocation import AppLocation
from openlp.core.common.httputils import get_web_page, get_url_file_size, download_file
from openlp.core.common.i18n import translate
from openlp.core.common.mixins import RegistryProperties
from openlp.core.common.path import Path, create_paths
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.lib import PluginStatus, build_icon
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.threading import ThreadWorker, run_thread, get_thread_worker, is_thread_finished
from openlp.core.ui.firsttimewizard import UiFirstTimeWizard, FirstTimePage

log = logging.getLogger(__name__)


class ThemeScreenshotWorker(ThreadWorker):
    """
    This thread downloads a theme's screenshot
    """
    screenshot_downloaded = QtCore.pyqtSignal(str, str, str)

    def __init__(self, themes_url, title, filename, sha256, screenshot):
        """
        Set up the worker object
        """
        self.was_cancelled = False
        self.themes_url = themes_url
        self.title = title
        self.filename = filename
        self.sha256 = sha256
        self.screenshot = screenshot
        super().__init__()

    def start(self):
        """
        Run the worker
        """
        if self.was_cancelled:
            return
        try:
            download_path = Path(gettempdir()) / 'openlp' / self.screenshot
            is_success = download_file(self, '{host}{name}'.format(host=self.themes_url, name=self.screenshot),
                                       download_path)
            if is_success and not self.was_cancelled:
                # Signal that the screenshot has been downloaded
                self.screenshot_downloaded.emit(self.title, self.filename, self.sha256)
        except:                                                                 # noqa
            log.exception('Unable to download screenshot')
        finally:
            self.quit.emit()

    @QtCore.pyqtSlot(bool)
    def set_download_canceled(self, toggle):
        """
        Externally set if the download was canceled

        :param toggle: Set if the download was canceled or not
        """
        self.was_download_cancelled = toggle


class FirstTimeForm(QtWidgets.QWizard, UiFirstTimeWizard, RegistryProperties):
    """
    This is the Theme Import Wizard, which allows easy creation and editing of OpenLP themes.
    """
    log.info('ThemeWizardForm loaded')

    def __init__(self, parent=None):
        """
        Create and set up the first time wizard.
        """
        super(FirstTimeForm, self).__init__(parent)
        self.web_access = True
        self.web = ''
        self.setup_ui(self)

    def get_next_page_id(self):
        """
        Returns the id of the next FirstTimePage to go to based on enabled plugins
        """
        if FirstTimePage.Welcome < self.currentId() < FirstTimePage.Songs and self.songs_check_box.isChecked():
            # If the songs plugin is enabled then go to the songs page
            return FirstTimePage.Songs
        elif FirstTimePage.Welcome < self.currentId() < FirstTimePage.Bibles and self.bible_check_box.isChecked():
            # Otherwise, if the Bibles plugin is enabled then go to the Bibles page
            return FirstTimePage.Bibles
        elif FirstTimePage.Welcome < self.currentId() < FirstTimePage.Themes:
            # Otherwise, if the current page is somewhere between the Welcome and the Themes pages, go to the themes
            return FirstTimePage.Themes
        else:
            # If all else fails, go to the next page
            return self.currentId() + 1

    def nextId(self):
        """
        Determine the next page in the Wizard to go to.
        """
        self.application.process_events()
        if self.currentId() == FirstTimePage.Download:
            if not self.web_access:
                return FirstTimePage.NoInternet
            else:
                return FirstTimePage.Plugins
        elif self.currentId() == FirstTimePage.Plugins:
            return self.get_next_page_id()
        elif self.currentId() == FirstTimePage.Progress:
            return -1
        elif self.currentId() == FirstTimePage.NoInternet:
            return FirstTimePage.Progress
        elif self.currentId() == FirstTimePage.Themes:
            self.application.set_busy_cursor()
            while not all([is_thread_finished(thread_name) for thread_name in self.theme_screenshot_threads]):
                time.sleep(0.1)
                self.application.process_events()
            # Build the screenshot icons, as this can not be done in the thread.
            self._build_theme_screenshots()
            self.application.set_normal_cursor()
            self.theme_screenshot_threads = []
            return FirstTimePage.Defaults
        else:
            return self.get_next_page_id()

    def exec(self):
        """
        Run the wizard.
        """
        self.set_defaults()
        return QtWidgets.QWizard.exec(self)

    def initialize(self, screens):
        """
        Set up the First Time Wizard

        :param screens: The screens detected by OpenLP
        """
        self.screens = screens
        self.was_cancelled = False
        self.theme_screenshot_threads = []
        self.has_run_wizard = False

    def _download_index(self):
        """
        Download the configuration file and kick off the theme screenshot download threads
        """
        # check to see if we have web access
        self.web_access = False
        self.config = ConfigParser()
        user_agent = 'OpenLP/' + Registry().get('application').applicationVersion()
        self.application.process_events()
        try:
            web_config = get_web_page('{host}{name}'.format(host=self.web, name='download.cfg'),
                                      headers={'User-Agent': user_agent})
        except ConnectionError:
            QtWidgets.QMessageBox.critical(self, translate('OpenLP.FirstTimeWizard', 'Network Error'),
                                           translate('OpenLP.FirstTimeWizard', 'There was a network error attempting '
                                                     'to connect to retrieve initial configuration information'),
                                           QtWidgets.QMessageBox.Ok)
            web_config = False
        if web_config:
            try:
                self.config.read_string(web_config)
                self.web = self.config.get('general', 'base url')
                self.songs_url = self.web + self.config.get('songs', 'directory') + '/'
                self.bibles_url = self.web + self.config.get('bibles', 'directory') + '/'
                self.themes_url = self.web + self.config.get('themes', 'directory') + '/'
                self.web_access = True
            except (NoSectionError, NoOptionError, MissingSectionHeaderError):
                log.debug('A problem occurred while parsing the downloaded config file')
                trace_error_handler(log)
        self.update_screen_list_combo()
        self.application.process_events()
        self.downloading = translate('OpenLP.FirstTimeWizard', 'Downloading {name}...')
        if self.has_run_wizard:
            self.songs_check_box.setChecked(self.plugin_manager.get_plugin_by_name('songs').is_active())
            self.bible_check_box.setChecked(self.plugin_manager.get_plugin_by_name('bibles').is_active())
            self.presentation_check_box.setChecked(self.plugin_manager.get_plugin_by_name('presentations').is_active())
            self.image_check_box.setChecked(self.plugin_manager.get_plugin_by_name('images').is_active())
            self.media_check_box.setChecked(self.plugin_manager.get_plugin_by_name('media').is_active())
            self.custom_check_box.setChecked(self.plugin_manager.get_plugin_by_name('custom').is_active())
            self.song_usage_check_box.setChecked(self.plugin_manager.get_plugin_by_name('songusage').is_active())
            self.alert_check_box.setChecked(self.plugin_manager.get_plugin_by_name('alerts').is_active())
        self.application.set_normal_cursor()
        # Sort out internet access for downloads
        if self.web_access:
            songs = self.config.get('songs', 'languages')
            songs = songs.split(',')
            for song in songs:
                self.application.process_events()
                title = self.config.get('songs_{song}'.format(song=song), 'title')
                filename = self.config.get('songs_{song}'.format(song=song), 'filename')
                sha256 = self.config.get('songs_{song}'.format(song=song), 'sha256', fallback='')
                item = QtWidgets.QListWidgetItem(title, self.songs_list_widget)
                item.setData(QtCore.Qt.UserRole, (filename, sha256))
                item.setCheckState(QtCore.Qt.Unchecked)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            bible_languages = self.config.get('bibles', 'languages')
            bible_languages = bible_languages.split(',')
            for lang in bible_languages:
                self.application.process_events()
                language = self.config.get('bibles_{lang}'.format(lang=lang), 'title')
                lang_item = QtWidgets.QTreeWidgetItem(self.bibles_tree_widget, [language])
                bibles = self.config.get('bibles_{lang}'.format(lang=lang), 'translations')
                bibles = bibles.split(',')
                for bible in bibles:
                    self.application.process_events()
                    title = self.config.get('bible_{bible}'.format(bible=bible), 'title')
                    filename = self.config.get('bible_{bible}'.format(bible=bible), 'filename')
                    sha256 = self.config.get('bible_{bible}'.format(bible=bible), 'sha256', fallback='')
                    item = QtWidgets.QTreeWidgetItem(lang_item, [title])
                    item.setData(0, QtCore.Qt.UserRole, (filename, sha256))
                    item.setCheckState(0, QtCore.Qt.Unchecked)
                    item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            self.bibles_tree_widget.expandAll()
            self.application.process_events()
            # Download the theme screenshots
            themes = self.config.get('themes', 'files').split(',')
            for theme in themes:
                title = self.config.get('theme_{theme}'.format(theme=theme), 'title')
                filename = self.config.get('theme_{theme}'.format(theme=theme), 'filename')
                sha256 = self.config.get('theme_{theme}'.format(theme=theme), 'sha256', fallback='')
                screenshot = self.config.get('theme_{theme}'.format(theme=theme), 'screenshot')
                worker = ThemeScreenshotWorker(self.themes_url, title, filename, sha256, screenshot)
                worker.screenshot_downloaded.connect(self.on_screenshot_downloaded)
                thread_name = 'theme_screenshot_{title}'.format(title=title)
                run_thread(worker, thread_name)
                self.theme_screenshot_threads.append(thread_name)
            self.application.process_events()

    def set_defaults(self):
        """
        Set up display at start of theme edit.
        """
        self.restart()
        self.web = 'http://openlp.org/files/frw/'
        self.cancel_button.clicked.connect(self.on_cancel_button_clicked)
        self.no_internet_finish_button.clicked.connect(self.on_no_internet_finish_button_clicked)
        self.no_internet_cancel_button.clicked.connect(self.on_no_internet_cancel_button_clicked)
        self.currentIdChanged.connect(self.on_current_id_changed)
        Registry().register_function('config_screen_changed', self.update_screen_list_combo)
        self.no_internet_finish_button.setVisible(False)
        self.no_internet_cancel_button.setVisible(False)
        # Check if this is a re-run of the wizard.
        self.has_run_wizard = Settings().value('core/has run wizard')
        create_paths(Path(gettempdir(), 'openlp'))

    def update_screen_list_combo(self):
        """
        The user changed screen resolution or enabled/disabled more screens, so
        we need to update the combo box.
        """
        self.display_combo_box.clear()
        self.display_combo_box.addItems(self.screens.get_screen_list())
        self.display_combo_box.setCurrentIndex(self.display_combo_box.count() - 1)

    def on_current_id_changed(self, page_id):
        """
        Detects Page changes and updates as appropriate.
        """
        # Keep track of the page we are at.  Triggering "Cancel" causes page_id to be a -1.
        self.application.process_events()
        if page_id != -1:
            self.last_id = page_id
        if page_id == FirstTimePage.Download:
            self.back_button.setVisible(False)
            self.next_button.setVisible(False)
            # Set the no internet page text.
            if self.has_run_wizard:
                self.no_internet_label.setText(self.no_internet_text)
            else:
                self.no_internet_label.setText(self.no_internet_text + self.cancel_wizard_text)
            self.application.set_busy_cursor()
            self._download_index()
            self.application.set_normal_cursor()
            self.back_button.setVisible(False)
            self.next_button.setVisible(True)
            self.next()
        elif page_id == FirstTimePage.Defaults:
            self.theme_combo_box.clear()
            for index in range(self.themes_list_widget.count()):
                item = self.themes_list_widget.item(index)
                if item.checkState() == QtCore.Qt.Checked:
                    self.theme_combo_box.addItem(item.text())
            if self.has_run_wizard:
                # Add any existing themes to list.
                for theme in self.theme_manager.get_themes():
                    index = self.theme_combo_box.findText(theme)
                    if index == -1:
                        self.theme_combo_box.addItem(theme)
                default_theme = Settings().value('themes/global theme')
                # Pre-select the current default theme.
                index = self.theme_combo_box.findText(default_theme)
                self.theme_combo_box.setCurrentIndex(index)
        elif page_id == FirstTimePage.NoInternet:
            self.back_button.setVisible(False)
            self.next_button.setVisible(False)
            self.cancel_button.setVisible(False)
            self.no_internet_finish_button.setVisible(True)
            if self.has_run_wizard:
                self.no_internet_cancel_button.setVisible(False)
            else:
                self.no_internet_cancel_button.setVisible(True)
        elif page_id == FirstTimePage.Plugins:
            self.back_button.setVisible(False)
        elif page_id == FirstTimePage.Progress:
            self.application.set_busy_cursor()
            self._pre_wizard()
            self._perform_wizard()
            self._post_wizard()
            self.application.set_normal_cursor()

    def on_cancel_button_clicked(self):
        """
        Process the triggering of the cancel button.
        """
        self.was_cancelled = True
        if self.theme_screenshot_threads:
            for thread_name in self.theme_screenshot_threads:
                worker = get_thread_worker(thread_name)
                if worker:
                    worker.set_download_canceled(True)
        # Was the thread created.
        if self.theme_screenshot_threads:
            while any([not is_thread_finished(thread_name) for thread_name in self.theme_screenshot_threads]):
                time.sleep(0.1)
        self.application.set_normal_cursor()

    def on_screenshot_downloaded(self, title, filename, sha256):
        """
        Add an item to the list when a theme has been downloaded

        :param title: The title of the theme
        :param filename: The filename of the theme
        """
        item = QtWidgets.QListWidgetItem(title, self.themes_list_widget)
        item.setData(QtCore.Qt.UserRole, (filename, sha256))
        item.setCheckState(QtCore.Qt.Unchecked)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)

    def on_no_internet_finish_button_clicked(self):
        """
        Process the triggering of the "Finish" button on the No Internet page.
        """
        self.application.set_busy_cursor()
        self._perform_wizard()
        self.application.set_normal_cursor()
        Settings().setValue('core/has run wizard', True)
        self.close()

    def on_no_internet_cancel_button_clicked(self):
        """
        Process the triggering of the "Cancel" button on the No Internet page.
        """
        self.was_cancelled = True
        self.close()

    def _build_theme_screenshots(self):
        """
        This method builds the theme screenshots' icons for all items in the ``self.themes_list_widget``.
        """
        themes = self.config.get('themes', 'files')
        themes = themes.split(',')
        for index, theme in enumerate(themes):
            screenshot = self.config.get('theme_{theme}'.format(theme=theme), 'screenshot')
            item = self.themes_list_widget.item(index)
            if item:
                item.setIcon(build_icon(Path(gettempdir(), 'openlp', screenshot)))

    def update_progress(self, count, block_size):
        """
        Calculate and display the download progress. This method is called by download_file().
        """
        increment = (count * block_size) - self.previous_size
        self._increment_progress_bar(None, increment)
        self.previous_size = count * block_size

    def _increment_progress_bar(self, status_text, increment=1):
        """
        Update the wizard progress page.

        :param status_text: Current status information to display.
        :param increment: The value to increment the progress bar by.
        """
        if status_text:
            self.progress_label.setText(status_text)
        if increment > 0:
            self.progress_bar.setValue(self.progress_bar.value() + increment)
        self.application.process_events()

    def _pre_wizard(self):
        """
        Prepare the UI for the process.
        """
        self.max_progress = 0
        self.finish_button.setVisible(False)
        self.application.process_events()
        try:
            # Loop through the songs list and increase for each selected item
            for i in range(self.songs_list_widget.count()):
                self.application.process_events()
                item = self.songs_list_widget.item(i)
                if item.checkState() == QtCore.Qt.Checked:
                    filename, sha256 = item.data(QtCore.Qt.UserRole)
                    size = get_url_file_size('{path}{name}'.format(path=self.songs_url, name=filename))
                    self.max_progress += size
            # Loop through the Bibles list and increase for each selected item
            iterator = QtWidgets.QTreeWidgetItemIterator(self.bibles_tree_widget)
            while iterator.value():
                self.application.process_events()
                item = iterator.value()
                if item.parent() and item.checkState(0) == QtCore.Qt.Checked:
                    filename, sha256 = item.data(0, QtCore.Qt.UserRole)
                    size = get_url_file_size('{path}{name}'.format(path=self.bibles_url, name=filename))
                    self.max_progress += size
                iterator += 1
            # Loop through the themes list and increase for each selected item
            for i in range(self.themes_list_widget.count()):
                self.application.process_events()
                item = self.themes_list_widget.item(i)
                if item.checkState() == QtCore.Qt.Checked:
                    filename, sha256 = item.data(QtCore.Qt.UserRole)
                    size = get_url_file_size('{path}{name}'.format(path=self.themes_url, name=filename))
                    self.max_progress += size
        except urllib.error.URLError:
            trace_error_handler(log)
            critical_error_message_box(translate('OpenLP.FirstTimeWizard', 'Download Error'),
                                       translate('OpenLP.FirstTimeWizard', 'There was a connection problem during '
                                                 'download, so further downloads will be skipped. Try to re-run the '
                                                 'First Time Wizard later.'))
            self.max_progress = 0
            self.web_access = None
        if self.max_progress:
            # Add on 2 for plugins status setting plus a "finished" point.
            self.max_progress += 2
            self.progress_bar.setValue(0)
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(self.max_progress)
            self.progress_page.setTitle(translate('OpenLP.FirstTimeWizard', 'Setting Up And Downloading'))
            self.progress_page.setSubTitle(
                translate('OpenLP.FirstTimeWizard', 'Please wait while OpenLP is set up and your data is downloaded.'))
        else:
            self.progress_bar.setVisible(False)
            self.progress_page.setTitle(translate('OpenLP.FirstTimeWizard', 'Setting Up'))
            self.progress_page.setSubTitle('Setup complete.')
        self.repaint()
        self.application.process_events()
        # Try to give the wizard a chance to repaint itself
        time.sleep(0.1)

    def _post_wizard(self):
        """
        Clean up the UI after the process has finished.
        """
        if self.max_progress:
            self.progress_bar.setValue(self.progress_bar.maximum())
            if self.has_run_wizard:
                text = translate('OpenLP.FirstTimeWizard',
                                 'Download complete. Click the {button} button to return to OpenLP.'
                                 ).format(button=clean_button_text(self.buttonText(QtWidgets.QWizard.FinishButton)))
                self.progress_label.setText(text)
            else:
                text = translate('OpenLP.FirstTimeWizard',
                                 'Download complete. Click the {button} button to start OpenLP.'
                                 ).format(button=clean_button_text(self.buttonText(QtWidgets.QWizard.FinishButton)))
                self.progress_label.setText(text)
        else:
            if self.has_run_wizard:
                text = translate('OpenLP.FirstTimeWizard',
                                 'Click the {button} button to return to OpenLP.'
                                 ).format(button=clean_button_text(self.buttonText(QtWidgets.QWizard.FinishButton)))
                self.progress_label.setText(text)
            else:
                text = translate('OpenLP.FirstTimeWizard',
                                 'Click the {button} button to start OpenLP.'
                                 ).format(button=clean_button_text(self.buttonText(QtWidgets.QWizard.FinishButton)))
                self.progress_label.setText(text)
        self.finish_button.setVisible(True)
        self.finish_button.setEnabled(True)
        self.cancel_button.setVisible(False)
        self.next_button.setVisible(False)
        self.application.process_events()

    def _perform_wizard(self):
        """
        Run the tasks in the wizard.
        """
        # Set plugin states
        self._increment_progress_bar(translate('OpenLP.FirstTimeWizard', 'Enabling selected plugins...'))
        self._set_plugin_status(self.songs_check_box, 'songs/status')
        self._set_plugin_status(self.bible_check_box, 'bibles/status')
        self._set_plugin_status(self.presentation_check_box, 'presentations/status')
        self._set_plugin_status(self.image_check_box, 'images/status')
        self._set_plugin_status(self.media_check_box, 'media/status')
        self._set_plugin_status(self.custom_check_box, 'custom/status')
        self._set_plugin_status(self.song_usage_check_box, 'songusage/status')
        self._set_plugin_status(self.alert_check_box, 'alerts/status')
        if self.web_access:
            if not self._download_selected():
                critical_error_message_box(translate('OpenLP.FirstTimeWizard', 'Download Error'),
                                           translate('OpenLP.FirstTimeWizard', 'There was a connection problem while '
                                                     'downloading, so further downloads will be skipped. Try to re-run '
                                                     'the First Time Wizard later.'))
        # Set Default Display
        if self.display_combo_box.currentIndex() != -1:
            Settings().setValue('core/monitor', self.display_combo_box.currentIndex())
            self.screens.set_current_display(self.display_combo_box.currentIndex())
        # Set Global Theme
        if self.theme_combo_box.currentIndex() != -1:
            Settings().setValue('themes/global theme', self.theme_combo_box.currentText())

    def _download_selected(self):
        """
        Download selected songs, bibles and themes. Returns False on download error
        """
        # Build directories for downloads
        songs_destination_path = Path(gettempdir(), 'openlp')
        bibles_destination_path = AppLocation.get_section_data_path('bibles')
        themes_destination_path = AppLocation.get_section_data_path('themes')
        missed_files = []
        # Download songs
        for i in range(self.songs_list_widget.count()):
            item = self.songs_list_widget.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                filename, sha256 = item.data(QtCore.Qt.UserRole)
                self._increment_progress_bar(self.downloading.format(name=filename), 0)
                self.previous_size = 0
                destination = songs_destination_path / str(filename)
                if not download_file(self, '{path}{name}'.format(path=self.songs_url, name=filename),
                                     destination, sha256):
                    missed_files.append('Song: {name}'.format(name=filename))
        # Download Bibles
        bibles_iterator = QtWidgets.QTreeWidgetItemIterator(self.bibles_tree_widget)
        while bibles_iterator.value():
            item = bibles_iterator.value()
            if item.parent() and item.checkState(0) == QtCore.Qt.Checked:
                bible, sha256 = item.data(0, QtCore.Qt.UserRole)
                self._increment_progress_bar(self.downloading.format(name=bible), 0)
                self.previous_size = 0
                if not download_file(self, '{path}{name}'.format(path=self.bibles_url, name=bible),
                                     bibles_destination_path / bible, sha256):
                    missed_files.append('Bible: {name}'.format(name=bible))
            bibles_iterator += 1
        # Download themes
        for i in range(self.themes_list_widget.count()):
            item = self.themes_list_widget.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                theme, sha256 = item.data(QtCore.Qt.UserRole)
                self._increment_progress_bar(self.downloading.format(name=theme), 0)
                self.previous_size = 0
                if not download_file(self, '{path}{name}'.format(path=self.themes_url, name=theme),
                                     themes_destination_path / theme, sha256):
                    missed_files.append('Theme: {name}'.format(name=theme))
        if missed_files:
            file_list = ''
            for entry in missed_files:
                file_list += '{text}<br \\>'.format(text=entry)
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle(translate('OpenLP.FirstTimeWizard', 'Network Error'))
            msg.setText(translate('OpenLP.FirstTimeWizard', 'Unable to download some files'))
            msg.setInformativeText(translate('OpenLP.FirstTimeWizard',
                                             'The following files were not able to be '
                                             'downloaded:<br \\>{text}'.format(text=file_list)))
            msg.setStandardButtons(msg.Ok)
            msg.exec()
        return True

    def _set_plugin_status(self, field, tag):
        """
        Set the status of a plugin.
        """
        status = PluginStatus.Active if field.checkState() == QtCore.Qt.Checked else PluginStatus.Inactive
        Settings().setValue(tag, status)
