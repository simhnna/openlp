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
The :mod:`languagemanager` module provides all the translation settings and
language file loading for OpenLP.
"""
import logging
import re
import sys

from PyQt4 import QtCore, QtGui

from openlp.core.utils import AppLocation
from openlp.core.lib import translate, Settings

log = logging.getLogger(__name__)

class LanguageManager(object):
    """
    Helper for Language selection
    """
    __qm_list__ = {}
    auto_language = False

    @staticmethod
    def get_translator(language):
        """
        Set up a translator to use in this instance of OpenLP

        ``language``
            The language to load into the translator
        """
        if LanguageManager.auto_language:
            language = QtCore.QLocale.system().name()
        lang_path = AppLocation.get_directory(AppLocation.LanguageDir)
        app_translator = QtCore.QTranslator()
        app_translator.load(language, lang_path)
        # A translator for buttons and other default strings provided by Qt.
        if sys.platform != u'win32' and sys.platform != u'darwin':
            lang_path = QtCore.QLibraryInfo.location(
                QtCore.QLibraryInfo.TranslationsPath)
        default_translator = QtCore.QTranslator()
        default_translator.load(u'qt_%s' % language, lang_path)
        return app_translator, default_translator

    @staticmethod
    def find_qm_files():
        """
        Find all available language files in this OpenLP install
        """
        log.debug(u'Translation files: %s', AppLocation.get_directory(
            AppLocation.LanguageDir))
        trans_dir = QtCore.QDir(AppLocation.get_directory(
            AppLocation.LanguageDir))
        file_names = trans_dir.entryList(
            u'*.qm', QtCore.QDir.Files, QtCore.QDir.Name)
        # Remove qm files from the list which start with "qt_".
        file_names = filter(
            lambda file_: not file_.startswith(u'qt_'), file_names)
        names = []
        for name in file_names:
            names.append(trans_dir.filePath(name))
            #file_names.replaceInStrings(name, trans_dir.filePath(name))
        return names

    @staticmethod
    def language_name(qm_file):
        """
        Load the language name from a language file

        ``qm_file``
            The file to obtain the name from
        """
        translator = QtCore.QTranslator()
        translator.load(qm_file)
        return translator.translate('OpenLP.MainWindow', 'English',
            'Please add the name of your language here')

    @staticmethod
    def get_language():
        """
        Retrieve a saved language to use from settings
        """
        language = Settings().value(u'general/language', u'[en]')
        language = str(language)
        log.info(u'Language file: \'%s\' Loaded from conf file' % language)
        if re.match(r'[[].*[]]', language):
            LanguageManager.auto_language = True
            language = re.sub(r'[\[\]]', '', language)
        return language

    @staticmethod
    def set_language(action, message=True):
        """
        Set the language to translate OpenLP into

        ``action``
            The language menu option

        ``message``
            Display the message option
        """
        language = u'en'
        if action:
            action_name = unicode(action.objectName())
            if action_name == u'autoLanguageItem':
                LanguageManager.auto_language = True
            else:
                LanguageManager.auto_language = False
                qm_list = LanguageManager.get_qm_list()
                language = unicode(qm_list[action_name])
        if LanguageManager.auto_language:
            language = u'[%s]' % language
        Settings().setValue(u'general/language', language)
        log.info(u'Language file: \'%s\' written to conf file' % language)
        if message:
            QtGui.QMessageBox.information(None,
                translate('OpenLP.LanguageManager', 'Language'),
                translate('OpenLP.LanguageManager',
                    'Please restart OpenLP to use your new language setting.'))

    @staticmethod
    def init_qm_list():
        """
        Initialise the list of available translations
        """
        LanguageManager.__qm_list__ = {}
        qm_files = LanguageManager.find_qm_files()
        for counter, qmf in enumerate(qm_files):
            reg_ex = QtCore.QRegExp("^.*i18n/(.*).qm")
            if reg_ex.exactMatch(qmf):
                name = u'%s' % reg_ex.cap(1)
                LanguageManager.__qm_list__[u'%#2i %s' % (counter + 1,
                    LanguageManager.language_name(qmf))] = name

    @staticmethod
    def get_qm_list():
        """
        Return the list of available translations
        """
        if not LanguageManager.__qm_list__:
            LanguageManager.init_qm_list()
        return LanguageManager.__qm_list__
