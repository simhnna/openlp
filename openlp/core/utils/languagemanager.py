# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2010 Raoul Snyman                                        #
# Portions copyright (c) 2008-2010 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Meinert Jordan, Andreas Preikschat, Christian      #
# Richter, Philip Ridout, Maikel Stuivenberg, Martin Thompson, Jon Tibble,    #
# Carsten Tinggaard, Frode Woldsund                                           #
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
import os

from PyQt4 import QtCore, QtGui

from openlp.core.utils import AppLocation
from openlp.core.lib import translate

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
        if app_translator.load(language, lang_path):
            return app_translator

    @staticmethod
    def find_qm_files():
        """
        Find all available language files in this OpenLP install
        """
        trans_dir = QtCore.QDir(AppLocation.get_directory(
            AppLocation.LanguageDir))
        file_names = trans_dir.entryList(QtCore.QStringList("*.qm"),
                QtCore.QDir.Files, QtCore.QDir.Name)
        for name in file_names:
            file_names.replaceInStrings(name, trans_dir.filePath(name))
        return file_names

    @staticmethod
    def language_name(qm_file):
        """
        Load the language name from a language file

        ``qm_file``
            The file to obtain the name from
        """
        translator = QtCore.QTranslator()
        translator.load(qm_file)
        return translator.translate('OpenLP.MainWindow', 'English')

    @staticmethod
    def get_language():
        """
        Retrieve a saved language to use from settings
        """
        settings = QtCore.QSettings(u'OpenLP', u'OpenLP')
        language = unicode(settings.value(
            u'general/language', QtCore.QVariant(u'[en]')).toString())
        log.info(u'Language file: \'%s\' Loaded from conf file' % language)
        reg_ex = QtCore.QRegExp("^\[(.*)\]")
        if reg_ex.exactMatch(language):
            LanguageManager.auto_language = True
            language = reg_ex.cap(1)
        return language

    @staticmethod
    def set_language(action):
        """
        Set the language to translate OpenLP into

        ``action``
            The language menu option
        """
        if action is None:
            action_name = u'en'
        else:
            action_name = u'%s' % action.objectName()
        qm_list = LanguageManager.get_qm_list()
        if LanguageManager.auto_language:
            language = u'[%s]' % qm_list[action_name]
        else:
            language = u'%s' % qm_list[action_name]
        QtCore.QSettings().setValue(
            u'general/language', QtCore.QVariant(language))
        log.info(u'Language file: \'%s\' written to conf file' % language)
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
            name = unicode(qmf).split(u'.')[0]
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
