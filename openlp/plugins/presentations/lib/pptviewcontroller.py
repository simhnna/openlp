# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2010 Raoul Snyman                                        #
# Portions copyright (c) 2008-2010 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Christian Richter, Maikel Stuivenberg, Martin      #
# Thompson, Jon Tibble, Carsten Tinggaard                                     #
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

import os
import logging

if os.name == u'nt':
    from ctypes import cdll
    from ctypes.wintypes import RECT

from presentationcontroller import PresentationController, PresentationDocument
from openlp.core.lib import resize_image

log = logging.getLogger(__name__)

class PptviewController(PresentationController):
    """
    Class to control interactions with PowerPOint Viewer Presentations
    It creates the runtime Environment , Loads the and Closes the Presentation
    As well as triggering the correct activities based on the users input
    """
    log.info(u'PPTViewController loaded')

    def __init__(self, plugin):
        """
        Initialise the class
        """
        log.debug(u'Initialising')
        self.process = None
        PresentationController.__init__(self, plugin, u'Powerpoint Viewer')
        self.supports = [u'.ppt', u'.pps', u'.pptx', u'.ppsx']

    def check_available(self):
        """
        PPT Viewer is able to run on this machine
        """
        log.debug(u'check_available')
        if os.name != u'nt':
            return False
        return self.check_installed()

    if os.name == u'nt':
        def check_installed(self):
            """
            Check the viewer is installed
            """
            log.debug(u'Check installed')
            try:
                self.start_process()
                return self.process.CheckInstalled()
            except WindowsError:
                return False

        def start_process(self):
            """
            Loads the PPTVIEWLIB library
            """
            if self.process:
                return
            log.debug(u'start PPTView')
            dllpath = os.path.join(self.plugin.pluginManager.basepath,
                u'presentations', u'lib', u'pptviewlib', u'pptviewlib.dll')
            self.process = cdll.LoadLibrary(dllpath)
            #self.process.SetDebug(1)

        def kill(self):
            """
            Called at system exit to clean up any running presentations
            """
            log.debug(u'Kill pptviewer')
            while self.docs:
                self.docs[0].close_presentation()

        def add_doc(self, name):
            """
            Called when a new powerpoint document is opened
            """
            log.debug(u'Add Doc PPTView')
            doc = PptviewDocument(self, name)
            self.docs.append(doc)
            return doc

class PptviewDocument(PresentationDocument):
    """
    Class which holds information and controls a single presentation
    """
    def __init__(self, controller, presentation):
        """
        Constructor, store information about the file and initialise 
        """
        log.debug(u'Init Presentation PowerPoint')
        PresentationDocument.__init__(self, controller, presentation)
        self.presentation = None
        self.pptid = None
        self.blanked = False
        self.hidden = False

    def load_presentation(self):
        """
        Called when a presentation is added to the SlideController.
        It builds the environment, starts communcations with the background
        PptView task started earlier.

        ``presentation``
        The file name of the presentations to run.
        """
        log.debug(u'LoadPresentation')
        rendermanager = self.controller.plugin.renderManager
        rect = rendermanager.screens.current[u'size']
        rect = RECT(rect.x(), rect.y(), rect.right(), rect.bottom())
        filepath = str(self.filepath.replace(u'/', u'\\'))
        self.pptid = self.controller.process.OpenPPT(filepath, None, rect,
            str(self.get_temp_folder()) + '\\')
        if self.pptid:
            self.create_thumbnails()
            self.stop_presentation()
            return True
        else:
            return False

    def create_thumbnails(self):
        """
        PPTviewLib creates large BMP's, but we want small PNG's for consistency.
        Convert them here.
        """
        if self.check_thumbnails():
            return
        for idx in range(self.get_slide_count()):
            path = u'%s\\%s.bmp' % (self.get_temp_folder(), unicode(idx + 1))            
            self.convert_image(path, idx)

    def close_presentation(self):
        """
        Close presentation and clean up objects
        Triggerent by new object being added to SlideController orOpenLP
        being shut down
        """
        log.debug(u'ClosePresentation')
        self.controller.process.ClosePPT(self.pptid)
        self.pptid = -1
        self.controller.remove_doc(self)

    def is_loaded(self):
        """
        Returns true if a presentation is loaded
        """
        if self.pptid < 0:
            return False
        if self.get_slide_count() < 0:
            return False
        return True

    def is_active(self):
        """
        Returns true if a presentation is currently active
        """
        return self.is_loaded() and not self.hidden

    def blank_screen(self):
        """
        Blanks the screen
        """
        self.controller.process.Blank(self.pptid)
        self.blanked = True

    def unblank_screen(self):
        """
        Unblanks (restores) the presentationn
        """
        self.controller.process.Unblank(self.pptid)
        self.blanked = False

    def is_blank(self):
        """
        Returns true if screen is blank
        """
        log.debug(u'is blank OpenOffice')
        return self.blanked

    def stop_presentation(self):
        """
        Stops the current presentation and hides the output
        """
        self.hidden = True
        self.controller.process.Stop(self.pptid)

    def start_presentation(self):
        """
        Starts a presentation from the beginning
        """
        if self.hidden:
            self.hidden = False
            self.controller.process.Resume(self.pptid)
        else:
            self.controller.process.RestartShow(self.pptid)

    def get_slide_number(self):
        """
        Returns the current slide number
        """
        return self.controller.process.GetCurrentSlide(self.pptid)

    def get_slide_count(self):
        """
        Returns total number of slides
        """
        return self.controller.process.GetSlideCount(self.pptid)

    def goto_slide(self, slideno):
        """
        Moves to a specific slide in the presentation
        """
        self.controller.process.GotoSlide(self.pptid, slideno)

    def next_step(self):
        """
        Triggers the next effect of slide on the running presentation
        """
        self.controller.process.NextStep(self.pptid)

    def previous_step(self):
        """
        Triggers the previous slide on the running presentation
        """
        self.controller.process.PrevStep(self.pptid)

