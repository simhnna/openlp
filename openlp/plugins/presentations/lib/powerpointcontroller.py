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
"""
This modul is for controlling powerpiont. PPT API documentation:
`http://msdn.microsoft.com/en-us/library/aa269321(office.10).aspx`_
"""
import os
import logging

if os.name == 'nt':
    from win32com.client import Dispatch
    import winreg
    import win32ui
    import pywintypes

from openlp.core.lib import ScreenList
from openlp.core.lib.ui import UiStrings, critical_error_message_box, translate
from openlp.core.common import trace_error_handler
from .presentationcontroller import PresentationController, PresentationDocument


log = logging.getLogger(__name__)


class PowerpointController(PresentationController):
    """
    Class to control interactions with PowerPoint Presentations. It creates the runtime Environment , Loads the and
    Closes the Presentation. As well as triggering the correct activities based on the users input.
    """
    log.info('PowerpointController loaded')

    def __init__(self, plugin):
        """
        Initialise the class
        """
        log.debug('Initialising')
        super(PowerpointController, self).__init__(plugin, 'Powerpoint', PowerpointDocument)
        self.supports = ['ppt', 'pps', 'pptx', 'ppsx']
        self.process = None

    def check_available(self):
        """
        PowerPoint is able to run on this machine.
        """
        log.debug('check_available')
        if os.name == 'nt':
            try:
                winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, 'PowerPoint.Application').Close()
                return True
            except WindowsError:
                pass
        return False

    if os.name == 'nt':
        def start_process(self):
            """
            Loads PowerPoint process.
            """
            log.debug('start_process')
            if not self.process:
                self.process = Dispatch('PowerPoint.Application')
            self.process.Visible = True
            self.process.WindowState = 2

        def kill(self):
            """
            Called at system exit to clean up any running presentations.
            """
            log.debug('Kill powerpoint')
            while self.docs:
                self.docs[0].close_presentation()
            if self.process is None:
                return
            try:
                if self.process.Presentations.Count > 0:
                    return
                self.process.Quit()
            except (AttributeError, pywintypes.com_error):
                pass
            self.process = None


class PowerpointDocument(PresentationDocument):
    """
    Class which holds information and controls a single presentation.
    """

    def __init__(self, controller, presentation):
        """
        Constructor, store information about the file and initialise.

        :param controller:
        :param presentation:
        """
        log.debug('Init Presentation Powerpoint')
        super(PowerpointDocument, self).__init__(controller, presentation)
        self.presentation = None

    def load_presentation(self):
        """
        Called when a presentation is added to the SlideController. Opens the PowerPoint file using the process created
        earlier.
        """
        log.debug('load_presentation')
        try:
            if not self.controller.process or not self.controller.process.Visible:
                self.controller.start_process()
            self.controller.process.Presentations.Open(self.file_path, False, False, True)
            self.presentation = self.controller.process.Presentations(self.controller.process.Presentations.Count)
            self.create_thumbnails()
            # Powerpoint 2013 pops up when loading a file, so we minimize it again
            if self.presentation.Application.Version == u'15.0':
                try:
                    self.presentation.Application.WindowState = 2
                except:
                    log.error('Failed to minimize main powerpoint window')
                    trace_error_handler(log)
            return True
        except pywintypes.com_error:
            log.error('PPT open failed')
            trace_error_handler(log)
            return False

    def create_thumbnails(self):
        """
        Create the thumbnail images for the current presentation.

        Note an alternative and quicker method would be do::

            self.presentation.Slides[n].Copy()
            thumbnail = QApplication.clipboard.image()

        However, for the moment, we want a physical file since it makes life easier elsewhere.
        """
        log.debug('create_thumbnails')
        if self.check_thumbnails():
            return
        for num in range(self.presentation.Slides.Count):
            self.presentation.Slides(num + 1).Export(
                os.path.join(self.get_thumbnail_folder(), 'slide%d.png' % (num + 1)), 'png', 320, 240)

    def close_presentation(self):
        """
        Close presentation and clean up objects. This is triggered by a new object being added to SlideController or
        OpenLP being shut down.
        """
        log.debug('ClosePresentation')
        if self.presentation:
            try:
                self.presentation.Close()
            except pywintypes.com_error:
                pass
        self.presentation = None
        self.controller.remove_doc(self)

    def is_loaded(self):
        """
        Returns ``True`` if a presentation is loaded.
        """
        log.debug('is_loaded')
        try:
            if not self.controller.process.Visible:
                return False
            if self.controller.process.Windows.Count == 0:
                return False
            if self.controller.process.Presentations.Count == 0:
                return False
        except (AttributeError, pywintypes.com_error):
            return False
        return True

    def is_active(self):
        """
        Returns ``True`` if a presentation is currently active.
        """
        log.debug('is_active')
        if not self.is_loaded():
            return False
        try:
            if self.presentation.SlideShowWindow is None:
                return False
            if self.presentation.SlideShowWindow.View is None:
                return False
        except (AttributeError, pywintypes.com_error):
            return False
        return True

    def unblank_screen(self):
        """
        Unblanks (restores) the presentation.
        """
        log.debug('unblank_screen')
        try:
            self.presentation.SlideShowSettings.Run()
            self.presentation.SlideShowWindow.View.State = 1
            self.presentation.SlideShowWindow.Activate()
            if self.presentation.Application.Version == '14.0':
                # Unblanking is broken in PowerPoint 2010, need to redisplay
                slide = self.presentation.SlideShowWindow.View.CurrentShowPosition
                click = self.presentation.SlideShowWindow.View.GetClickIndex()
                self.presentation.SlideShowWindow.View.GotoSlide(slide)
                if click:
                    self.presentation.SlideShowWindow.View.GotoClick(click)
        except pywintypes.com_error:
            log.error('COM error while in unblank_screen')
            trace_error_handler(log)
            self.show_error_msg()

    def blank_screen(self):
        """
        Blanks the screen.
        """
        log.debug('blank_screen')
        try:
            self.presentation.SlideShowWindow.View.State = 3
        except pywintypes.com_error:
            log.error('COM error while in blank_screen')
            trace_error_handler(log)
            self.show_error_msg()

    def is_blank(self):
        """
        Returns ``True`` if screen is blank.
        """
        log.debug('is_blank')
        if self.is_active():
            try:
                return self.presentation.SlideShowWindow.View.State == 3
            except pywintypes.com_error:
                log.error('COM error while in is_blank')
                trace_error_handler(log)
                self.show_error_msg()
        else:
            return False

    def stop_presentation(self):
        """
        Stops the current presentation and hides the output.
        """
        log.debug('stop_presentation')
        try:
            self.presentation.SlideShowWindow.View.Exit()
        except pywintypes.com_error:
            log.error('COM error while in stop_presentation')
            trace_error_handler(log)
            self.show_error_msg()

    if os.name == 'nt':
        def start_presentation(self):
            """
            Starts a presentation from the beginning.
            """
            log.debug('start_presentation')
            # SlideShowWindow measures its size/position by points, not pixels
            try:
                dpi = win32ui.GetActiveWindow().GetDC().GetDeviceCaps(88)
            except win32ui.error:
                try:
                    dpi = win32ui.GetForegroundWindow().GetDC().GetDeviceCaps(88)
                except win32ui.error:
                    dpi = 96
            size = ScreenList().current['size']
            ppt_window = self.presentation.SlideShowSettings.Run()
            if not ppt_window:
                return
            try:
                ppt_window.Top = size.y() * 72 / dpi
                ppt_window.Height = size.height() * 72 / dpi
                ppt_window.Left = size.x() * 72 / dpi
                ppt_window.Width = size.width() * 72 / dpi
            except AttributeError as e:
                log.error('AttributeError while in start_presentation')
                log.error(e)
            # Powerpoint 2013 pops up when starting a file, so we minimize it again
            if self.presentation.Application.Version == u'15.0':
                try:
                    self.presentation.Application.WindowState = 2
                except:
                    log.error('Failed to minimize main powerpoint window')
                    trace_error_handler(log)

    def get_slide_number(self):
        """
        Returns the current slide number.
        """
        log.debug('get_slide_number')
        ret = 0
        try:
            ret = self.presentation.SlideShowWindow.View.CurrentShowPosition
        except pywintypes.com_error:
            log.error('COM error while in get_slide_number')
            trace_error_handler(log)
            self.show_error_msg()
        return ret

    def get_slide_count(self):
        """
        Returns total number of slides.
        """
        log.debug('get_slide_count')
        ret = 0
        try:
            ret = self.presentation.Slides.Count
        except pywintypes.com_error:
            log.error('COM error while in get_slide_count')
            trace_error_handler(log)
            self.show_error_msg()
        return ret

    def goto_slide(self, slide_no):
        """
        Moves to a specific slide in the presentation.

        :param slide_no: The slide the text is required for, starting at 1
        """
        log.debug('goto_slide')
        try:
            self.presentation.SlideShowWindow.View.GotoSlide(slide_no)
        except pywintypes.com_error:
            log.error('COM error while in goto_slide')
            trace_error_handler(log)
            self.show_error_msg()

    def next_step(self):
        """
        Triggers the next effect of slide on the running presentation.
        """
        log.debug('next_step')
        try:
            self.presentation.SlideShowWindow.View.Next()
        except pywintypes.com_error:
            log.error('COM error while in next_step')
            trace_error_handler(log)
            self.show_error_msg()
            return
        if self.get_slide_number() > self.get_slide_count():
            self.previous_step()

    def previous_step(self):
        """
        Triggers the previous slide on the running presentation.
        """
        log.debug('previous_step')
        try:
            self.presentation.SlideShowWindow.View.Previous()
        except pywintypes.com_error:
            log.error('COM error while in previous_step')
            trace_error_handler(log)
            self.show_error_msg()

    def get_slide_text(self, slide_no):
        """
        Returns the text on the slide.

        :param slide_no: The slide the text is required for, starting at 1
        """
        return _get_text_from_shapes(self.presentation.Slides(slide_no).Shapes)

    def get_slide_notes(self, slide_no):
        """
        Returns the text on the slide.

        :param slide_no: The slide the text is required for, starting at 1
        """
        return _get_text_from_shapes(self.presentation.Slides(slide_no).NotesPage.Shapes)

    def show_error_msg(self):
        """
        Stop presentation and display an error message.
        """
        self.stop_presentation()
        critical_error_message_box(UiStrings().Error, translate('PresentationPlugin.PowerpointDocument',
                                                                'An error occurred in the Powerpoint integration '
                                                                'and the presentation will be stopped. '
                                                                'Restart the presentation if you wish to present it.'))


def _get_text_from_shapes(shapes):
    """
    Returns any text extracted from the shapes on a presentation slide.

    :param shapes: A set of shapes to search for text.
    """
    text = ''
    for index in range(shapes.Count):
        shape = shapes(index + 1)
        if shape.HasTextFrame:
            text += shape.TextFrame.TextRange.Text + '\n'
    return text
