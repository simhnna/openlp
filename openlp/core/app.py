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
The :mod:`core` module provides all core application functions

All the core functions of the OpenLP application including the GUI, settings,
logging and a plugin framework are contained within the openlp.core module.
"""
import argparse
import logging
import sys
import time
from datetime import datetime
from traceback import format_exception

from PyQt5 import QtCore, QtWidgets

from openlp.core.common import is_macosx, is_win
from openlp.core.common.applocation import AppLocation
from openlp.core.common.i18n import LanguageManager, UiStrings, translate
from openlp.core.common.path import create_paths, copytree
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.display.screens import ScreenList
from openlp.core.resources import qInitResources
from openlp.core.ui import SplashScreen
from openlp.core.ui.exceptionform import ExceptionForm
from openlp.core.ui.firsttimeform import FirstTimeForm
from openlp.core.ui.firsttimelanguageform import FirstTimeLanguageForm
from openlp.core.ui.mainwindow import MainWindow
from openlp.core.ui.style import get_application_stylesheet
from openlp.core.server import Server
from openlp.core.version import check_for_update, get_version

__all__ = ['OpenLP', 'main']


log = logging.getLogger()


class OpenLP(QtWidgets.QApplication):
    """
    The core application class. This class inherits from Qt's QApplication
    class in order to provide the core of the application.
    """
    args = []
    worker_threads = {}

    def exec(self):
        """
        Override exec method to allow the shared memory to be released on exit
        """
        self.is_event_loop_active = True
        result = QtWidgets.QApplication.exec()
        self.server.close_server()
        return result

    def run(self, args):
        """
        Run the OpenLP application.

        :param args: Some Args
        """
        self.is_event_loop_active = False
        # On Windows, the args passed into the constructor are ignored. Not very handy, so set the ones we want to use.
        # On Linux and FreeBSD, in order to set the WM_CLASS property for X11, we pass "OpenLP" in as a command line
        # argument. This interferes with files being passed in as command line arguments, so we remove it from the list.
        if 'OpenLP' in args:
            args.remove('OpenLP')
        self.args.extend(args)
        # Decide how many screens we have and their size
        screens = ScreenList.create(self.desktop())
        # First time checks in settings
        has_run_wizard = Settings().value('core/has run wizard')
        if not has_run_wizard:
            ftw = FirstTimeForm()
            ftw.initialize(screens)
            if ftw.exec() == QtWidgets.QDialog.Accepted:
                Settings().setValue('core/has run wizard', True)
            elif ftw.was_cancelled:
                QtCore.QCoreApplication.exit()
                sys.exit()
        # Correct stylesheet bugs
        application_stylesheet = get_application_stylesheet()
        if application_stylesheet:
            self.setStyleSheet(application_stylesheet)
        can_show_splash = Settings().value('core/show splash')
        if can_show_splash:
            self.splash = SplashScreen()
            self.splash.show()
        # make sure Qt really display the splash screen
        self.processEvents()
        # Check if OpenLP has been upgrade and if a backup of data should be created
        self.backup_on_upgrade(has_run_wizard, can_show_splash)
        # start the main app window
        self.main_window = MainWindow()
        Registry().execute('bootstrap_initialise')
        Registry().execute('bootstrap_post_set_up')
        Registry().initialise = False
        self.main_window.show()
        if can_show_splash:
            # now kill the splashscreen
            log.debug('Splashscreen closing')
            self.splash.close()
            log.debug('Splashscreen closed')
        # make sure Qt really display the splash screen
        self.processEvents()
        self.main_window.repaint()
        self.processEvents()
        if not has_run_wizard:
            self.main_window.first_time()
        if Settings().value('core/update check'):
            check_for_update(self.main_window)
        self.main_window.is_display_blank()
        self.main_window.app_startup()
        return self.exec()

    @staticmethod
    def is_already_running():
        """
        Tell the user there is a 2nd instance running.
        """
        QtWidgets.QMessageBox.critical(None, UiStrings().Error, UiStrings().OpenLPStart,
                                       QtWidgets.QMessageBox.StandardButtons(QtWidgets.QMessageBox.Ok))

    @staticmethod
    def is_data_path_missing():
        """
        Check if the data folder path exists.
        """
        data_folder_path = AppLocation.get_data_path()
        if not data_folder_path.exists():
            log.critical('Database was not found in: %s', data_folder_path)
            status = QtWidgets.QMessageBox.critical(
                None, translate('OpenLP', 'Data Directory Error'),
                translate('OpenLP', 'OpenLP data folder was not found in:\n\n{path}\n\nThe location of the data folder '
                                    'was previously changed from the OpenLP\'s default location. If the data was '
                                    'stored on removable device, that device needs to be made available.\n\nYou may '
                                    'reset the data location back to the default location, or you can try to make the '
                                    'current location available.\n\nDo you want to reset to the default data location? '
                                    'If not, OpenLP will be closed so you can try to fix the the problem.')
                .format(path=data_folder_path),
                QtWidgets.QMessageBox.StandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No),
                QtWidgets.QMessageBox.No)
            if status == QtWidgets.QMessageBox.No:
                # If answer was "No", return "True", it will shutdown OpenLP in def main
                log.info('User requested termination')
                return True
            # If answer was "Yes", remove the custom data path thus resetting the default location.
            Settings().remove('advanced/data path')
            log.info('Database location has been reset to the default settings.')
            return False

    def hook_exception(self, exc_type, value, traceback):
        """
        Add an exception hook so that any uncaught exceptions are displayed in this window rather than somewhere where
        users cannot see it and cannot report when we encounter these problems.

        :param exc_type: The class of exception.
        :param value: The actual exception object.
        :param traceback: A traceback object with the details of where the exception occurred.
        """
        # We can't log.exception here because the last exception no longer exists, we're actually busy handling it.
        log.critical(''.join(format_exception(exc_type, value, traceback)))
        if not hasattr(self, 'exception_form'):
            self.exception_form = ExceptionForm()
        self.exception_form.exception_text_edit.setPlainText(''.join(format_exception(exc_type, value, traceback)))
        self.set_normal_cursor()
        is_splash_visible = False
        if hasattr(self, 'splash') and self.splash.isVisible():
            is_splash_visible = True
            self.splash.hide()
        self.exception_form.exec()
        if is_splash_visible:
            self.splash.show()

    def backup_on_upgrade(self, has_run_wizard, can_show_splash):
        """
        Check if OpenLP has been upgraded, and ask if a backup of data should be made

        :param has_run_wizard: OpenLP has been run before
        :param can_show_splash: Should OpenLP show the splash screen
        """
        data_version = Settings().value('core/application version')
        openlp_version = get_version()['version']
        # New installation, no need to create backup
        if not has_run_wizard:
            Settings().setValue('core/application version', openlp_version)
        # If data_version is different from the current version ask if we should backup the data folder
        elif data_version != openlp_version:
            if can_show_splash and self.splash.isVisible():
                self.splash.hide()
            if QtWidgets.QMessageBox.question(None, translate('OpenLP', 'Backup'),
                                              translate('OpenLP', 'OpenLP has been upgraded, do you want to create\n'
                                                                  'a backup of the old data folder?'),
                                              defaultButton=QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes:
                # Create copy of data folder
                data_folder_path = AppLocation.get_data_path()
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                data_folder_backup_path = data_folder_path.with_name(data_folder_path.name + '-' + timestamp)
                try:
                    copytree(data_folder_path, data_folder_backup_path)
                except OSError:
                    QtWidgets.QMessageBox.warning(None, translate('OpenLP', 'Backup'),
                                                  translate('OpenLP', 'Backup of the data folder failed!'))
                    return
                message = translate('OpenLP',
                                    'A backup of the data folder has been created at:\n\n'
                                    '{text}').format(text=data_folder_backup_path)
                QtWidgets.QMessageBox.information(None, translate('OpenLP', 'Backup'), message)

            # Update the version in the settings
            Settings().setValue('core/application version', openlp_version)
            if can_show_splash:
                self.splash.show()

    def process_events(self):
        """
        Wrapper to make ProcessEvents visible and named correctly
        """
        self.processEvents()

    def set_busy_cursor(self):
        """
        Sets the Busy Cursor for the Application
        """
        self.setOverrideCursor(QtCore.Qt.BusyCursor)
        self.processEvents()

    def set_normal_cursor(self):
        """
        Sets the Normal Cursor for the Application
        """
        self.restoreOverrideCursor()
        self.processEvents()

    def event(self, event):
        """
        Enables platform specific event handling i.e. direct file opening on OS X

        :param event: The event
        """
        if event.type() == QtCore.QEvent.FileOpen:
            file_name = event.file()
            log.debug('Got open file event for {name}!'.format(name=file_name))
            self.args.insert(0, file_name)
            return True
        # Mac OS X should restore app window when user clicked on the OpenLP icon
        # in the Dock bar. However, OpenLP consists of multiple windows and this
        # does not work. This workaround fixes that.
        # The main OpenLP window is restored when it was previously minimized.
        elif event.type() == QtCore.QEvent.ApplicationActivate:
            if is_macosx() and hasattr(self, 'main_window'):
                if self.main_window.isMinimized():
                    # Copied from QWidget.setWindowState() docs on how to restore and activate a minimized window
                    # while preserving its maximized and/or full-screen state.
                    self.main_window.setWindowState(self.main_window.windowState() & ~QtCore.Qt.WindowMinimized |
                                                    QtCore.Qt.WindowActive)
                    return True
        return QtWidgets.QApplication.event(self, event)


def parse_options(args=None):
    """
    Parse the command line arguments

    :param args: list of command line arguments
    :return: a tuple of parsed options of type optparse.Value and a list of remaining argsZ
    """
    # Set up command line options.
    parser = argparse.ArgumentParser(prog='openlp.py')
    parser.add_argument('-e', '--no-error-form', dest='no_error_form', action='store_true',
                        help='Disable the error notification form.')
    parser.add_argument('-l', '--log-level', dest='loglevel', default='warning', metavar='LEVEL',
                        help='Set logging to LEVEL level. Valid values are "debug", "info", "warning".')
    parser.add_argument('-p', '--portable', dest='portable', action='store_true',
                        help='Specify if this should be run as a portable app, ')
    parser.add_argument('-w', '--no-web-server', dest='no_web_server', action='store_true',
                        help='Turn off the Web and Socket Server ')
    parser.add_argument('rargs', nargs='?', default=[])
    # Parse command line options and deal with them. Use args supplied pragmatically if possible.
    return parser.parse_args(args) if args else parser.parse_args()


def set_up_logging(log_path):
    """
    Setup our logging using log_path

    :param openlp.core.common.path.Path log_path: The file to save the log to.
    :rtype: None
    """
    create_paths(log_path, do_not_log=True)
    file_path = log_path / 'openlp.log'
    # TODO: FileHandler accepts a Path object in Py3.6
    logfile = logging.FileHandler(str(file_path), 'w', encoding='UTF-8')
    logfile.setFormatter(logging.Formatter('%(asctime)s %(name)-55s %(levelname)-8s %(message)s'))
    log.addHandler(logfile)
    if log.isEnabledFor(logging.DEBUG):
        print('Logging to: {name}'.format(name=file_path))


def main(args=None):
    """
    The main function which parses command line options and then runs

    :param args: Some args
    """
    args = parse_options(args)
    qt_args = []
    if args and args.loglevel.lower() in ['d', 'debug']:
        log.setLevel(logging.DEBUG)
    elif args and args.loglevel.lower() in ['w', 'warning']:
        log.setLevel(logging.WARNING)
    else:
        log.setLevel(logging.INFO)
    # Throw the rest of the arguments at Qt, just in case.
    qt_args.extend(args.rargs)
    # Bug #1018855: Set the WM_CLASS property in X11
    if not is_win() and not is_macosx():
        qt_args.append('OpenLP')
    # Initialise the resources
    qInitResources()
    # Now create and actually run the application.
    application = OpenLP(qt_args)
    application.setOrganizationName('OpenLP')
    application.setOrganizationDomain('openlp.org')
    application.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    application.setAttribute(QtCore.Qt.AA_DontCreateNativeWidgetSiblings, True)
    if args.portable:
        application.setApplicationName('OpenLPPortable')
        Settings.setDefaultFormat(Settings.IniFormat)
        # Get location OpenLPPortable.ini
        portable_path = (AppLocation.get_directory(AppLocation.AppDir) / '..' / '..').resolve()
        data_path = portable_path / 'Data'
        set_up_logging(portable_path / 'Other')
        log.info('Running portable')
        portable_settings_path = data_path / 'OpenLP.ini'
        # Make this our settings file
        log.info('INI file: {name}'.format(name=portable_settings_path))
        Settings.set_filename(str(portable_settings_path))
        portable_settings = Settings()
        # Set our data path
        log.info('Data path: {name}'.format(name=data_path))
        # Point to our data path
        portable_settings.setValue('advanced/data path', data_path)
        portable_settings.setValue('advanced/is portable', True)
        portable_settings.sync()
    else:
        application.setApplicationName('OpenLP')
        set_up_logging(AppLocation.get_directory(AppLocation.CacheDir))
    Registry.create()
    Registry().register('application', application)
    Registry().set_flag('no_web_server', args.no_web_server)
    application.setApplicationVersion(get_version()['version'])
    # Check if an instance of OpenLP is already running. Quit if there is a running instance and the user only wants one
    server = Server()
    if server.is_another_instance_running():
        application.is_already_running()
        server.post_to_server(qt_args)
        sys.exit()
    else:
        server.start_server()
        application.server = server
    # If the custom data path is missing and the user wants to restore the data path, quit OpenLP.
    if application.is_data_path_missing():
        server.close_server()
        sys.exit()
    # Upgrade settings.
    settings = Settings()
    if settings.can_upgrade():
        now = datetime.now()
        # Only back up if OpenLP has previously run.
        if settings.value('core/has run wizard'):
            back_up_path = AppLocation.get_data_path() / (now.strftime('%Y-%m-%d %H-%M') + '.conf')
            log.info('Settings about to be upgraded. Existing settings are being backed up to {back_up_path}'
                     .format(back_up_path=back_up_path))
            QtWidgets.QMessageBox.information(
                None, translate('OpenLP', 'Settings Upgrade'),
                translate('OpenLP', 'Your settings are about to be upgraded. A backup will be created at '
                                    '{back_up_path}').format(back_up_path=back_up_path))
            settings.export(back_up_path)
        settings.upgrade_settings()
    # First time checks in settings
    if not Settings().value('core/has run wizard'):
        if not FirstTimeLanguageForm().exec():
            # if cancel then stop processing
            server.close_server()
            sys.exit()
    # i18n Set Language
    language = LanguageManager.get_language()
    translators = LanguageManager.get_translators(language)
    for translator in translators:
        if not translator.isEmpty():
            application.installTranslator(translator)
    if not translators:
        log.debug('Could not find translators.')
    if args and not args.no_error_form:
        sys.excepthook = application.hook_exception
    sys.exit(application.run(qt_args))
