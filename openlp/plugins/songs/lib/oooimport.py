# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2014 Raoul Snyman                                        #
# Portions copyright (c) 2008-2014 Tim Bentley, Gerald Britton, Jonathan      #
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
import logging
import os
import time

from PyQt4 import QtCore

from openlp.core.utils import get_uno_command, get_uno_instance
from openlp.core.lib import translate
from .songimport import SongImport

log = logging.getLogger(__name__)

if os.name == 'nt':
    from win32com.client import Dispatch
    NoConnectException = Exception
else:
    import uno
    from com.sun.star.connection import NoConnectException
try:
    from com.sun.star.style.BreakType import PAGE_BEFORE, PAGE_AFTER, PAGE_BOTH
except ImportError:
    PAGE_BEFORE = 4
    PAGE_AFTER = 5
    PAGE_BOTH = 6


class OooImport(SongImport):
    """
    Import songs from Impress/Powerpoint docs using Impress
    """
    def __init__(self, manager, **kwargs):
        """
        Initialise the class. Requires a songmanager class which is passed
        to SongImport for writing song to disk
        """
        SongImport.__init__(self, manager, **kwargs)
        self.document = None
        self.processStarted = False

    def doImport(self):
        if not isinstance(self.import_source, list):
            return
        try:
            self.startOoo()
        except NoConnectException as exc:
            self.logError(
                self.import_source[0],
                translate('SongsPlugin.SongImport', 'Cannot access OpenOffice or LibreOffice'))
            log.error(exc)
            return
        self.import_wizard.progress_bar.setMaximum(len(self.import_source))
        for filename in self.import_source:
            if self.stop_import_flag:
                break
            filename = str(filename)
            if os.path.isfile(filename):
                self.openOooFile(filename)
                if self.document:
                    self.processOooDocument()
                    self.closeOooFile()
                else:
                    self.logError(self.filepath, translate('SongsPlugin.SongImport', 'Unable to open file'))
            else:
                self.logError(self.filepath, translate('SongsPlugin.SongImport', 'File not found'))
        self.closeOoo()

    def processOooDocument(self):
        """
        Handle the import process for OpenOffice files. This method facilitates
        allowing subclasses to handle specific types of OpenOffice files.
        """
        if self.document.supportsService("com.sun.star.presentation.PresentationDocument"):
            self.processPres()
        if self.document.supportsService("com.sun.star.text.TextDocument"):
            self.processDoc()

    def startOoo(self):
        """
        Start OpenOffice.org process
        TODO: The presentation/Impress plugin may already have it running
        """
        if os.name == 'nt':
            self.startOooProcess()
            self.desktop = self.oooManager.createInstance('com.sun.star.frame.Desktop')
        else:
            context = uno.getComponentContext()
            resolver = context.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver', context)
            uno_instance = None
            loop = 0
            while uno_instance is None and loop < 5:
                try:
                    uno_instance = get_uno_instance(resolver)
                except NoConnectException:
                    time.sleep(0.1)
                    log.exception("Failed to resolve uno connection")
                    self.startOooProcess()
                    loop += 1
                else:
                    manager = uno_instance.ServiceManager
                    self.desktop = manager.createInstanceWithContext("com.sun.star.frame.Desktop", uno_instance)
                    return
            raise

    def startOooProcess(self):
        try:
            if os.name == 'nt':
                self.oooManager = Dispatch('com.sun.star.ServiceManager')
                self.oooManager._FlagAsMethod('Bridge_GetStruct')
                self.oooManager._FlagAsMethod('Bridge_GetValueObject')
            else:
                cmd = get_uno_command()
                process = QtCore.QProcess()
                process.startDetached(cmd)
            self.processStarted = True
        except:
            log.exception("startOooProcess failed")

    def openOooFile(self, filepath):
        """
        Open the passed file in OpenOffice.org Impress
        """
        self.filepath = filepath
        if os.name == 'nt':
            url = filepath.replace('\\', '/')
            url = url.replace(':', '|').replace(' ', '%20')
            url = 'file:///' + url
        else:
            url = uno.systemPathToFileUrl(filepath)
        properties = []
        properties = tuple(properties)
        try:
            self.document = self.desktop.loadComponentFromURL(url, '_blank',
                0, properties)
            if not self.document.supportsService("com.sun.star.presentation.PresentationDocument") and not \
                    self.document.supportsService("com.sun.star.text.TextDocument"):
                self.closeOooFile()
            else:
                self.import_wizard.increment_progress_bar('Processing file ' + filepath, 0)
        except AttributeError:
            log.exception("openOooFile failed: %s", url)
        return

    def closeOooFile(self):
        """
        Close file.
        """
        self.document.close(True)
        self.document = None

    def closeOoo(self):
        """
        Close OOo. But only if we started it and not on windows
        """
        if self.processStarted:
            self.desktop.terminate()

    def processPres(self):
        """
        Process the file
        """
        doc = self.document
        slides = doc.getDrawPages()
        text = ''
        for slide_no in range(slides.getCount()):
            if self.stop_import_flag:
                self.import_wizard.increment_progress_bar('Import cancelled', 0)
                return
            slide = slides.getByIndex(slide_no)
            slidetext = ''
            for idx in range(slide.getCount()):
                shape = slide.getByIndex(idx)
                if shape.supportsService("com.sun.star.drawing.Text"):
                    if shape.getString().strip() != '':
                        slidetext += shape.getString().strip() + '\n\n'
            if slidetext.strip() == '':
                slidetext = '\f'
            text += slidetext
        self.processSongsText(text)
        return

    def processDoc(self):
        """
        Process the doc file, a paragraph at a time
        """
        text = ''
        paragraphs = self.document.getText().createEnumeration()
        while paragraphs.hasMoreElements():
            paratext = ''
            paragraph = paragraphs.nextElement()
            if paragraph.supportsService("com.sun.star.text.Paragraph"):
                textportions = paragraph.createEnumeration()
                while textportions.hasMoreElements():
                    textportion = textportions.nextElement()
                    if textportion.BreakType in (PAGE_BEFORE, PAGE_BOTH):
                        paratext += '\f'
                    paratext += textportion.getString()
                    if textportion.BreakType in (PAGE_AFTER, PAGE_BOTH):
                        paratext += '\f'
            text += paratext + '\n'
        self.processSongsText(text)

    def processSongsText(self, text):
        songtexts = self.tidyText(text).split('\f')
        self.setDefaults()
        for songtext in songtexts:
            if songtext.strip():
                self.processSongText(songtext.strip())
                if self.checkComplete():
                    self.finish()
                    self.setDefaults()
        if self.checkComplete():
            self.finish()
