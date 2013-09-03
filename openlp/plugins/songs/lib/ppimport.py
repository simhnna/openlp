# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2013 Raoul Snyman                                        #
# Portions copyright (c) 2008-2013 Tim Bentley, Gerald Britton, Jonathan      #
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
The :mod:`ppimport` module provides the functionality for importing
ProPresenter song files into the current installation database.
"""

import os
import base64
from lxml import objectify

from openlp.core.ui.wizard import WizardStrings
from openlp.plugins.songs.lib import strip_rtf
from .songimport import SongImport

class ProPresenterImport(SongImport):
    """
    The :class:`ProPresenterImport` class provides OpenLP with the
    ability to import ProPresenter song files.
    """
    def doImport(self):
        self.import_wizard.progress_bar.setMaximum(len(self.import_source))
        for file_path in self.import_source:
            if self.stop_import_flag:
                return
            self.import_wizard.increment_progress_bar(
                WizardStrings.ImportingType % os.path.basename(file_path))
            root = objectify.parse(open(file_path, 'rb')).getroot()
            self.processSong(root)

    def processSong(self, root):
        self.setDefaults()
        self.title = root.get('CCLISongTitle')
        self.copyright = root.get('CCLICopyrightInfo')
        self.comments = root.get('notes')
        self.ccliNumber = root.get('CCLILicenseNumber')
        for author_key in ['author', 'artist', 'CCLIArtistCredits']:
            author = root.get(author_key)
            if len(author) > 0:
                self.parse_author(author)
        for slide in root.slides.RVDisplaySlide:
            RTFData = slide.displayElements.RVTextElement.get('RTFData')
            rtf = base64.standard_b64decode(RTFData)
            words, encoding = strip_rtf(rtf.decode())
            self.addVerse(words)
        if not self.finish():
            self.logError(self.import_source)
