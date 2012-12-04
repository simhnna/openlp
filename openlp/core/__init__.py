# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2012 Raoul Snyman                                        #
# Portions copyright (c) 2008-2012 Tim Bentley, Gerald Britton, Jonathan      #
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

"""
The :mod:`core` module provides all core application functions

All the core functions of the OpenLP application including the GUI, settings,
logging and a plugin framework are contained within the openlp.core module.
"""

import os
import sys
import platform
import logging
from optparse import OptionParser
from traceback import format_exception

from PyQt4 import QtCore, QtGui

from openlp.core.lib import Receiver, Settings, check_directory_exists
from openlp.core.lib.ui import UiStrings
from openlp.core.resources import qInitResources
from openlp.core.ui.mainwindow import MainWindow
from openlp.core.ui.firsttimelanguageform import FirstTimeLanguageForm
from openlp.core.ui.firsttimeform import FirstTimeForm
from openlp.core.ui.exceptionform import ExceptionForm
from openlp.core.ui import SplashScreen, ScreenList
from openlp.core.utils import AppLocation, LanguageManager, VersionThread, \
    get_application_version


__all__ = [u'OpenLP', u'main']


log = logging.getLogger()
nt_repair_stylesheet = u"""
QMainWindow::separator
{
  border: none;
}

QDockWidget::title
{
  border: 1px solid palette(dark);
  padding-left: 5px;
  padding-top: 2px;
  margin: 1px 0;
}

QToolBar
{
  border: none;
  margin: 0;
  padding: 0;
}
"""


class OpenLP(QtGui.QApplication):
    """
    The core application class. This class inherits from Qt's QApplication
    class in order to provide the core of the application.
    """

    args = []

    def exec_(self):
        """
        Override exec method to allow the shared memory to be released on exit
        """
        self.eventLoopIsActive = True
        QtGui.QApplication.exec_()
        self.sharedMemory.detach()

    def run(self, args, testing=False):
        """
        Run the OpenLP application.
        """
        self.eventLoopIsActive = False
        # On Windows, the args passed into the constructor are ignored. Not
        # very handy, so set the ones we want to use. On Linux and FreeBSD, in
        # order to set the WM_CLASS property for X11, we pass "OpenLP" in as a
        # command line argument. This interferes with files being passed in as
        # command line arguments, so we remove it from the list.
        if 'OpenLP' in args:
            args.remove('OpenLP')
        self.args.extend(args)
        # provide a listener for widgets to reqest a screen update.
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'openlp_process_events'), self.processEvents)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'cursor_busy'), self.setBusyCursor)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'cursor_normal'), self.setNormalCursor)
        # Decide how many screens we have and their size
        screens = ScreenList.create(self.desktop())
        # First time checks in settings
        has_run_wizard = Settings().value(u'general/has run wizard', False)
        if not has_run_wizard:
            if FirstTimeForm(screens).exec_() == QtGui.QDialog.Accepted:
                Settings().setValue(u'general/has run wizard', True)
        # Correct stylesheet bugs
        if os.name == u'nt':
            base_color = self.palette().color(QtGui.QPalette.Active,
                QtGui.QPalette.Base)
            application_stylesheet = \
                u'* {alternate-background-color: ' + \
                base_color.name() + ';}\n'
            application_stylesheet += nt_repair_stylesheet
            self.setStyleSheet(application_stylesheet)
        show_splash = Settings().value(u'general/show splash', True)
        if show_splash:
            self.splash = SplashScreen()
            self.splash.show()
        # make sure Qt really display the splash screen
        self.processEvents()
        # start the main app window
        self.mainWindow = MainWindow(self)
        self.mainWindow.show()
        if show_splash:
            # now kill the splashscreen
            self.splash.finish(self.mainWindow)
            log.debug(u'Splashscreen closed')
        # make sure Qt really display the splash screen
        self.processEvents()
        self.mainWindow.repaint()
        self.processEvents()
        if not has_run_wizard:
            self.mainWindow.firstTime()
        update_check = Settings().value(u'general/update check', True)
        if update_check:
            VersionThread(self.mainWindow).start()
        Receiver.send_message(u'live_display_blank_check')
        self.mainWindow.appStartup()
        # Skip exec_() for gui tests
        if not testing:
            return self.exec_()

    def isAlreadyRunning(self):
        """
        Look to see if OpenLP is already running and ask if a 2nd copy
        is to be started.
        """
        self.sharedMemory = QtCore.QSharedMemory('OpenLP')
        if self.sharedMemory.attach():
            status = QtGui.QMessageBox.critical(None,
                UiStrings().Error, UiStrings().OpenLPStart,
                QtGui.QMessageBox.StandardButtons(
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No))
            if status == QtGui.QMessageBox.No:
                return True
            return False
        else:
            self.sharedMemory.create(1)
            return False

    def hookException(self, exctype, value, traceback):
        if not hasattr(self, u'mainWindow'):
            log.exception(''.join(format_exception(exctype, value, traceback)))
            return
        if not hasattr(self, u'exceptionForm'):
            self.exceptionForm = ExceptionForm(self.mainWindow)
        self.exceptionForm.exceptionTextEdit.setPlainText(
            ''.join(format_exception(exctype, value, traceback)))
        self.setNormalCursor()
        self.exceptionForm.exec_()

    def setBusyCursor(self):
        """
        Sets the Busy Cursor for the Application
        """
        self.setOverrideCursor(QtCore.Qt.BusyCursor)
        self.processEvents()

    def setNormalCursor(self):
        """
        Sets the Normal Cursor for the Application
        """
        self.restoreOverrideCursor()

    def event(self, event):
        """
        Enables direct file opening on OS X
        """
        if event.type() == QtCore.QEvent.FileOpen:
            file_name = event.file()
            log.debug(u'Got open file event for %s!', file_name)
            self.args.insert(0, file_name)
            return True
        else:
            return QtGui.QApplication.event(self, event)


def set_up_logging(log_path):
    """
    Setup our logging using log_path
    """
    check_directory_exists(log_path)
    filename = os.path.join(log_path, u'openlp.log')
    logfile = logging.FileHandler(filename, u'w')
    logfile.setFormatter(logging.Formatter(
        u'%(asctime)s %(name)-55s %(levelname)-8s %(message)s'))
    log.addHandler(logfile)
    if log.isEnabledFor(logging.DEBUG):
        print 'Logging to:', filename


def main(args=None):
    """
    The main function which parses command line options and then runs
    the PyQt4 Application.
    """
    # Set up command line options.
    usage = 'Usage: %prog [options] [qt-options]'
    parser = OptionParser(usage=usage)
    parser.add_option('-e', '--no-error-form', dest='no_error_form',
        action='store_true', help='Disable the error notification form.')
    parser.add_option('-l', '--log-level', dest='loglevel',
        default='warning', metavar='LEVEL', help='Set logging to LEVEL '
        'level. Valid values are "debug", "info", "warning".')
    parser.add_option('-p', '--portable', dest='portable',
        action='store_true', help='Specify if this should be run as a '
        'portable app, off a USB flash drive (not implemented).')
    parser.add_option('-d', '--dev-version', dest='dev_version',
        action='store_true', help='Ignore the version file and pull the '
        'version directly from Bazaar')
    parser.add_option('-s', '--style', dest='style',
        help='Set the Qt4 style (passed directly to Qt4).')
    parser.add_option('--testing', dest='testing',
        action='store_true', help='Run by testing framework')
    # Parse command line options and deal with them.
    # Use args supplied programatically if possible.
    (options, args) = parser.parse_args(args) if args else parser.parse_args()
    if options.portable:
        app_path = AppLocation.get_directory(AppLocation.AppDir)
        set_up_logging(os.path.abspath(os.path.join(app_path, u'..',
            u'..', u'Other')))
        log.info(u'Running portable')
    else:
        set_up_logging(AppLocation.get_directory(AppLocation.CacheDir))
    qt_args = []
    if options.loglevel.lower() in ['d', 'debug']:
        log.setLevel(logging.DEBUG)
    elif options.loglevel.lower() in ['w', 'warning']:
        log.setLevel(logging.WARNING)
    else:
        log.setLevel(logging.INFO)
    if options.style:
        qt_args.extend(['-style', options.style])
    # Throw the rest of the arguments at Qt, just in case.
    qt_args.extend(args)
    # Bug #1018855: Set the WM_CLASS property in X11
    if platform.system() not in ['Windows', 'Darwin']:
        qt_args.append('OpenLP')
    # Initialise the resources
    qInitResources()
    # Now create and actually run the application.
    app = OpenLP(qt_args)
    app.setOrganizationName(u'OpenLP')
    app.setOrganizationDomain(u'openlp.org')
    if options.portable:
        app.setApplicationName(u'OpenLPPortable')
        Settings.setDefaultFormat(Settings.IniFormat)
        # Get location OpenLPPortable.ini
        portable_settings_file = os.path.abspath(os.path.join(app_path, u'..',
            u'..', u'Data', u'OpenLP.ini'))
        # Make this our settings file
        log.info(u'INI file: %s', portable_settings_file)
        Settings.setFilename(portable_settings_file)
        portable_settings = Settings()
        # Set our data path
        data_path = os.path.abspath(os.path.join(app_path,
            u'..', u'..', u'Data',))
        log.info(u'Data path: %s', data_path)
        # Point to our data path
        portable_settings.setValue(u'advanced/data path', data_path)
        portable_settings.setValue(u'advanced/is portable', True)
        portable_settings.sync()
    else:
        app.setApplicationName(u'OpenLP')
    app.setApplicationVersion(get_application_version()[u'version'])
    # Instance check
    if not options.testing:
        # Instance check
        if app.isAlreadyRunning():
            sys.exit()
    # First time checks in settings
    if not Settings().value(u'general/has run wizard', False):
        if not FirstTimeLanguageForm().exec_():
            # if cancel then stop processing
            sys.exit()
    # i18n Set Language
    language = LanguageManager.get_language()
    app_translator, default_translator = \
        LanguageManager.get_translator(language)
    if not app_translator.isEmpty():
        app.installTranslator(app_translator)
    if not default_translator.isEmpty():
        app.installTranslator(default_translator)
    else:
        log.debug(u'Could not find default_translator.')
    if not options.no_error_form:
        sys.excepthook = app.hookException
    # Do not run method app.exec_() when running gui tests
    if options.testing:
        app.run(qt_args, testing=True)
        # For gui tests we need access to window intances and their components
        return app
    else:
        sys.exit(app.run(qt_args))
