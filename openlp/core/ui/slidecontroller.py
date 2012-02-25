# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2012 Raoul Snyman                                        #
# Portions copyright (c) 2008-2012 Tim Bentley, Gerald Britton, Jonathan      #
# Corwin, Michael Gorven, Scott Guerrieri, Matthias Hub, Meinert Jordan,      #
# Armin Köhler, Joshua Miller, Stevan Pettit, Andreas Preikschat, Mattias     #
# Põldaru, Christian Richter, Philip Ridout, Simon Scudder, Jeffrey Smith,    #
# Maikel Stuivenberg, Martin Thompson, Jon Tibble, Frode Woldsund             #
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
import copy
from collections import deque

from PyQt4 import QtCore, QtGui

from openlp.core.lib import OpenLPToolbar, Receiver, ItemCapabilities, \
    translate, build_icon, build_html, PluginManager, ServiceItem
from openlp.core.lib.ui import UiStrings, shortcut_action
from openlp.core.lib import SlideLimits, ServiceItemAction
from openlp.core.ui import HideMode, MainDisplay, Display, ScreenList
from openlp.core.utils.actions import ActionList, CategoryOrder

log = logging.getLogger(__name__)

class SlideList(QtGui.QTableWidget):
    """
    Customised version of QTableWidget which can respond to keyboard
    events.
    """
    def __init__(self, parent=None):
        QtGui.QTableWidget.__init__(self, parent.controller)


class Controller(QtGui.QWidget):
    """
    Controller is a general controller widget.
    """
    def __init__(self, parent, isLive=False):
        """
        Set up the general Controller.
        """
        QtGui.QWidget.__init__(self, parent)
        self.isLive = isLive
        self.display = None

    def sendToPlugins(self, *args):
        """
        This is the generic function to send signal for control widgets,
        created from within other plugins
        This function is needed to catch the current controller
        """
        sender = self.sender().objectName() if self.sender().objectName() \
            else self.sender().text()
        controller = self
        Receiver.send_message('%s' % sender, [controller, args])

class SlideController(Controller):
    """
    SlideController is the slide controller widget. This widget is what the
    user uses to control the displaying of verses/slides/etc on the screen.
    """
    def __init__(self, parent, isLive=False):
        """
        Set up the Slide Controller.
        """
        Controller.__init__(self, parent, isLive)
        self.screens = ScreenList.get_instance()
        try:
            self.ratio = float(self.screens.current[u'size'].width()) / \
                float(self.screens.current[u'size'].height())
        except ZeroDivisionError:
            self.ratio = 1
        self.imageManager = self.parent().imageManager
        self.mediaController = self.parent().mediaController
        self.loopList = [
            u'Play Slides Menu',
            u'Loop Separator',
            u'Image SpinBox'
        ]
        self.songEditList = [
            u'Edit Song',
        ]
        self.nextPreviousList = [
            u'Previous Slide',
            u'Next Slide'
        ]
        self.timer_id = 0
        self.songEdit = False
        self.selectedRow = 0
        self.serviceItem = None
        self.slide_limits = None
        self.updateSlideLimits()
        self.panel = QtGui.QWidget(parent.controlSplitter)
        self.slideList = {}
        # Layout for holding panel
        self.panelLayout = QtGui.QVBoxLayout(self.panel)
        self.panelLayout.setSpacing(0)
        self.panelLayout.setMargin(0)
        # Type label for the top of the slide controller
        self.typeLabel = QtGui.QLabel(self.panel)
        if self.isLive:
            self.typeLabel.setText(UiStrings().Live)
            self.split = 1
            self.typePrefix = u'live'
            self.keypress_queue = deque()
            self.keypress_loop = False
        else:
            self.typeLabel.setText(UiStrings().Preview)
            self.split = 0
            self.typePrefix = u'preview'
        self.typeLabel.setStyleSheet(u'font-weight: bold; font-size: 12pt;')
        self.typeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.panelLayout.addWidget(self.typeLabel)
        # Splitter
        self.splitter = QtGui.QSplitter(self.panel)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.panelLayout.addWidget(self.splitter)
        # Actual controller section
        self.controller = QtGui.QWidget(self.splitter)
        self.controller.setGeometry(QtCore.QRect(0, 0, 100, 536))
        self.controller.setSizePolicy(
            QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Maximum))
        self.controllerLayout = QtGui.QVBoxLayout(self.controller)
        self.controllerLayout.setSpacing(0)
        self.controllerLayout.setMargin(0)
        # Controller list view
        self.previewListWidget = SlideList(self)
        self.previewListWidget.setColumnCount(1)
        self.previewListWidget.horizontalHeader().setVisible(False)
        self.previewListWidget.setColumnWidth(0, self.controller.width())
        self.previewListWidget.isLive = self.isLive
        self.previewListWidget.setObjectName(u'previewListWidget')
        self.previewListWidget.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectRows)
        self.previewListWidget.setSelectionMode(
            QtGui.QAbstractItemView.SingleSelection)
        self.previewListWidget.setEditTriggers(
            QtGui.QAbstractItemView.NoEditTriggers)
        self.previewListWidget.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.previewListWidget.setAlternatingRowColors(True)
        self.controllerLayout.addWidget(self.previewListWidget)
        # Build the full toolbar
        self.toolbar = OpenLPToolbar(self)
        sizeToolbarPolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
            QtGui.QSizePolicy.Fixed)
        sizeToolbarPolicy.setHorizontalStretch(0)
        sizeToolbarPolicy.setVerticalStretch(0)
        sizeToolbarPolicy.setHeightForWidth(
            self.toolbar.sizePolicy().hasHeightForWidth())
        self.toolbar.setSizePolicy(sizeToolbarPolicy)
        self.previousItem = self.toolbar.addToolbarButton(
            u'Previous Slide',
            u':/slides/slide_previous.png',
            translate('OpenLP.SlideController', 'Move to previous.'),
            self.onSlideSelectedPrevious,
            shortcuts=[QtCore.Qt.Key_Up, QtCore.Qt.Key_PageUp],
            context=QtCore.Qt.WidgetWithChildrenShortcut)
        self.nextItem = self.toolbar.addToolbarButton(
            u'Next Slide',
            u':/slides/slide_next.png',
            translate('OpenLP.SlideController', 'Move to next.'),
            self.onSlideSelectedNext,
            shortcuts=[QtCore.Qt.Key_Down, QtCore.Qt.Key_PageDown],
            context=QtCore.Qt.WidgetWithChildrenShortcut)
        self.toolbar.addToolbarSeparator(u'Close Separator')
        if self.isLive:
            # Hide Menu
            self.hideMenu = QtGui.QToolButton(self.toolbar)
            self.hideMenu.setText(translate('OpenLP.SlideController', 'Hide'))
            self.hideMenu.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
            self.toolbar.addToolbarWidget(u'Hide Menu', self.hideMenu)
            self.hideMenu.setMenu(QtGui.QMenu(
                translate('OpenLP.SlideController', 'Hide'), self.toolbar))
            self.blankScreen = shortcut_action(self.hideMenu, u'blankScreen',
                [QtCore.Qt.Key_Period], self.onBlankDisplay,
                u':/slides/slide_blank.png', False,
                unicode(UiStrings().LiveToolbar))
            self.blankScreen.setText(
                translate('OpenLP.SlideController', 'Blank Screen'))
            self.themeScreen = shortcut_action(self.hideMenu, u'themeScreen',
                [QtGui.QKeySequence(u'T')], self.onThemeDisplay,
                u':/slides/slide_theme.png', False,
                unicode(UiStrings().LiveToolbar))
            self.themeScreen.setText(
                translate('OpenLP.SlideController', 'Blank to Theme'))
            self.desktopScreen = shortcut_action(self.hideMenu,
                u'desktopScreen', [QtGui.QKeySequence(u'D')],
                self.onHideDisplay, u':/slides/slide_desktop.png', False,
                unicode(UiStrings().LiveToolbar))
            self.desktopScreen.setText(
                translate('OpenLP.SlideController', 'Show Desktop'))
            self.hideMenu.setDefaultAction(self.blankScreen)
            self.hideMenu.menu().addAction(self.blankScreen)
            self.hideMenu.menu().addAction(self.themeScreen)
            self.hideMenu.menu().addAction(self.desktopScreen)
            self.toolbar.addToolbarSeparator(u'Loop Separator')
            # Play Slides Menu
            self.playSlidesMenu = QtGui.QToolButton(self.toolbar)
            self.playSlidesMenu.setText(translate('OpenLP.SlideController',
                'Play Slides'))
            self.playSlidesMenu.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
            self.toolbar.addToolbarWidget(u'Play Slides Menu',
                self.playSlidesMenu)
            self.playSlidesMenu.setMenu(QtGui.QMenu(
                translate('OpenLP.SlideController', 'Play Slides'),
                self.toolbar))
            self.playSlidesLoop = shortcut_action(self.playSlidesMenu,
                u'playSlidesLoop', [], self.onPlaySlidesLoop,
                u':/media/media_time.png', False,
                unicode(UiStrings().LiveToolbar))
            self.playSlidesLoop.setText(UiStrings().PlaySlidesInLoop)
            self.playSlidesOnce = shortcut_action(self.playSlidesMenu,
                u'playSlidesOnce', [], self.onPlaySlidesOnce,
                u':/media/media_time.png', False,
                unicode(UiStrings().LiveToolbar))
            self.playSlidesOnce.setText(UiStrings().PlaySlidesToEnd)
            if QtCore.QSettings().value(self.parent().generalSettingsSection +
                u'/enable slide loop', QtCore.QVariant(True)).toBool():
                self.playSlidesMenu.setDefaultAction(self.playSlidesLoop)
            else:
                self.playSlidesMenu.setDefaultAction(self.playSlidesOnce)
            self.playSlidesMenu.menu().addAction(self.playSlidesLoop)
            self.playSlidesMenu.menu().addAction(self.playSlidesOnce)
            # Loop Delay Spinbox
            self.delaySpinBox = QtGui.QSpinBox()
            self.delaySpinBox.setRange(1, 180)
            self.toolbar.addToolbarWidget(u'Image SpinBox', self.delaySpinBox)
            self.delaySpinBox.setSuffix(UiStrings().Seconds)
            self.delaySpinBox.setToolTip(translate('OpenLP.SlideController',
                'Delay between slides in seconds.'))
        else:
            self.toolbar.addToolbarButton(
                # Does not need translating - control string.
                u'Go Live', u':/general/general_live.png',
                translate('OpenLP.SlideController', 'Move to live.'),
                self.onGoLive)
            self.toolbar.addToolbarButton(
                # Does not need translating - control string.
                u'Add to Service', u':/general/general_add.png',
                translate('OpenLP.SlideController', 'Add to Service.'),
                self.onPreviewAddToService)
            self.toolbar.addToolbarSeparator(u'Close Separator')
            self.toolbar.addToolbarButton(
                # Does not need translating - control string.
                u'Edit Song', u':/general/general_edit.png',
                translate('OpenLP.SlideController',
                'Edit and reload song preview.'),
                self.onEditSong)
        self.controllerLayout.addWidget(self.toolbar)
        # Build the Media Toolbar
        self.mediaController.add_controller_items(self, self.controllerLayout)
        if self.isLive:
            # Build the Song Toolbar
            self.songMenu = QtGui.QToolButton(self.toolbar)
            self.songMenu.setText(translate('OpenLP.SlideController', 'Go To'))
            self.songMenu.setPopupMode(QtGui.QToolButton.InstantPopup)
            self.toolbar.addToolbarWidget(u'Song Menu', self.songMenu)
            self.songMenu.setMenu(QtGui.QMenu(
                translate('OpenLP.SlideController', 'Go To'), self.toolbar))
            # Stuff for items with background audio.
            self.audioPauseItem = QtGui.QToolButton(self.toolbar)
            self.audioPauseItem.setIcon(
                QtGui.QIcon(u':/slides/media_playback_pause.png'))
            self.audioPauseItem.setText(translate('OpenLP.SlideController',
                'Pause audio.'))
            self.audioPauseItem.setCheckable(True)
            self.toolbar.addToolbarWidget(u'Pause Audio', self.audioPauseItem)
            QtCore.QObject.connect(self.audioPauseItem,
                QtCore.SIGNAL(u'clicked(bool)'),  self.onAudioPauseClicked)
            self.audioPauseItem.setVisible(False)
            self.audioMenu = QtGui.QMenu(
                translate('OpenLP.SlideController', 'Background Audio'),
                self.toolbar)
            self.nextTrackItem = shortcut_action(self.audioMenu,
                u'nextTrackItem', [], self.onNextTrackClicked,
                u':/slides/media_playback_next.png',
                category=unicode(UiStrings().LiveToolbar))
            self.nextTrackItem.setText(
                translate('OpenLP.SlideController', 'Next Track'))
            self.audioMenu.addAction(self.nextTrackItem)
            self.trackMenu = self.audioMenu.addMenu(
                translate('OpenLP.SlideController', 'Tracks'))
            self.audioPauseItem.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
            self.audioPauseItem.setMenu(self.audioMenu)
            self.audioTimeLabel = QtGui.QLabel(u' 00:00 ', self.toolbar)
            self.audioTimeLabel.setAlignment(
                QtCore.Qt.AlignCenter|QtCore.Qt.AlignHCenter)
            self.audioTimeLabel.setStyleSheet(
                u'background-color: palette(background); '
                u'border-top-color: palette(shadow); '
                u'border-left-color: palette(shadow); '
                u'border-bottom-color: palette(light); '
                u'border-right-color: palette(light); '
                u'border-radius: 3px; border-style: inset; '
                u'border-width: 1; font-family: monospace; margin: 2px;'
            )
            self.audioTimeLabel.setObjectName(u'audioTimeLabel')
            self.toolbar.addToolbarWidget(
                u'Time Remaining', self.audioTimeLabel)
            self.toolbar.makeWidgetsInvisible([u'Song Menu', u'Pause Audio',
                u'Time Remaining'])
        # Screen preview area
        self.previewFrame = QtGui.QFrame(self.splitter)
        self.previewFrame.setGeometry(QtCore.QRect(0, 0, 300, 300 * self.ratio))
        self.previewFrame.setMinimumHeight(100)
        self.previewFrame.setSizePolicy(QtGui.QSizePolicy(
            QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored,
            QtGui.QSizePolicy.Label))
        self.previewFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.previewFrame.setFrameShadow(QtGui.QFrame.Sunken)
        self.previewFrame.setObjectName(u'previewFrame')
        self.grid = QtGui.QGridLayout(self.previewFrame)
        self.grid.setMargin(8)
        self.grid.setObjectName(u'grid')
        self.slideLayout = QtGui.QVBoxLayout()
        self.slideLayout.setSpacing(0)
        self.slideLayout.setMargin(0)
        self.slideLayout.setObjectName(u'SlideLayout')
        self.previewDisplay = Display(self, self.isLive, self)
        self.previewDisplay.setGeometry(QtCore.QRect(0, 0, 300, 300))
        self.previewDisplay.screen = {u'size':self.previewDisplay.geometry()}
        self.previewDisplay.setup()
        self.slideLayout.insertWidget(0, self.previewDisplay)
        self.previewDisplay.hide()
        # Actual preview screen
        self.slidePreview = QtGui.QLabel(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
            QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.slidePreview.sizePolicy().hasHeightForWidth())
        self.slidePreview.setSizePolicy(sizePolicy)
        self.slidePreview.setFrameShape(QtGui.QFrame.Box)
        self.slidePreview.setFrameShadow(QtGui.QFrame.Plain)
        self.slidePreview.setLineWidth(1)
        self.slidePreview.setScaledContents(True)
        self.slidePreview.setObjectName(u'slidePreview')
        self.slideLayout.insertWidget(0, self.slidePreview)
        self.grid.addLayout(self.slideLayout, 0, 0, 1, 1)
        if self.isLive:
            self.current_shortcut = u''
            self.shortcutTimer = QtCore.QTimer()
            self.shortcutTimer.setObjectName(u'shortcutTimer')
            self.shortcutTimer.setSingleShot(True)
            self.verseShortcut = shortcut_action(self, u'verseShortcut',
                [QtGui.QKeySequence(u'V')], self.slideShortcutActivated,
                category=unicode(UiStrings().LiveToolbar),
                context=QtCore.Qt.WidgetWithChildrenShortcut)
            self.verseShortcut.setText(translate(
                'OpenLP.SlideController', 'Go to "Verse"'))
            self.shortcut0 = shortcut_action(self, u'0',
                [QtGui.QKeySequence(u'0')], self.slideShortcutActivated,
                context=QtCore.Qt.WidgetWithChildrenShortcut)
            self.shortcut1 = shortcut_action(self, u'1',
                [QtGui.QKeySequence(u'1')], self.slideShortcutActivated,
                context=QtCore.Qt.WidgetWithChildrenShortcut)
            self.shortcut2 = shortcut_action(self, u'2',
                [QtGui.QKeySequence(u'2')], self.slideShortcutActivated,
                context=QtCore.Qt.WidgetWithChildrenShortcut)
            self.shortcut3 = shortcut_action(self, u'3',
                [QtGui.QKeySequence(u'3')], self.slideShortcutActivated,
                context=QtCore.Qt.WidgetWithChildrenShortcut)
            self.shortcut4 = shortcut_action(self, u'4',
                [QtGui.QKeySequence(u'4')], self.slideShortcutActivated,
                context=QtCore.Qt.WidgetWithChildrenShortcut)
            self.shortcut5 = shortcut_action(self, u'5',
                [QtGui.QKeySequence(u'5')], self.slideShortcutActivated,
                context=QtCore.Qt.WidgetWithChildrenShortcut)
            self.shortcut6 = shortcut_action(self, u'6',
                [QtGui.QKeySequence(u'6')], self.slideShortcutActivated,
                context=QtCore.Qt.WidgetWithChildrenShortcut)
            self.shortcut7 = shortcut_action(self, u'7',
                [QtGui.QKeySequence(u'7')], self.slideShortcutActivated,
                context=QtCore.Qt.WidgetWithChildrenShortcut)
            self.shortcut8 = shortcut_action(self, u'8',
                [QtGui.QKeySequence(u'8')], self.slideShortcutActivated,
                context=QtCore.Qt.WidgetWithChildrenShortcut)
            self.shortcut9 = shortcut_action(self, u'9',
                [QtGui.QKeySequence(u'9')], self.slideShortcutActivated,
                context=QtCore.Qt.WidgetWithChildrenShortcut)
            self.chorusShortcut = shortcut_action(self, u'chorusShortcut',
                [QtGui.QKeySequence(u'C')], self.slideShortcutActivated,
                category=unicode(UiStrings().LiveToolbar),
                context=QtCore.Qt.WidgetWithChildrenShortcut)
            self.chorusShortcut.setText(translate(
                'OpenLP.SlideController', 'Go to "Chorus"'))
            self.bridgeShortcut = shortcut_action(self, u'bridgeShortcut',
                [QtGui.QKeySequence(u'B')], self.slideShortcutActivated,
                category=unicode(UiStrings().LiveToolbar),
                context=QtCore.Qt.WidgetWithChildrenShortcut)
            self.bridgeShortcut.setText(translate(
                'OpenLP.SlideController', 'Go to "Bridge"'))
            self.preChorusShortcut = shortcut_action(self, u'preChorusShortcut',
                [QtGui.QKeySequence(u'P')], self.slideShortcutActivated,
                category=unicode(UiStrings().LiveToolbar),
                context=QtCore.Qt.WidgetWithChildrenShortcut)
            self.preChorusShortcut.setText(translate(
                'OpenLP.SlideController', 'Go to "Pre-Chorus"'))
            self.introShortcut = shortcut_action(self, u'introShortcut',
                [QtGui.QKeySequence(u'I')], self.slideShortcutActivated,
                category=unicode(UiStrings().LiveToolbar),
                context=QtCore.Qt.WidgetWithChildrenShortcut)
            self.introShortcut.setText(translate(
                'OpenLP.SlideController', 'Go to "Intro"'))
            self.endingShortcut = shortcut_action(self, u'endingShortcut',
                [QtGui.QKeySequence(u'E')], self.slideShortcutActivated,
                category=unicode(UiStrings().LiveToolbar),
                context=QtCore.Qt.WidgetWithChildrenShortcut)
            self.endingShortcut.setText(translate(
                'OpenLP.SlideController', 'Go to "Ending"'))
            self.otherShortcut = shortcut_action(self, u'otherShortcut',
                [QtGui.QKeySequence(u'O')], self.slideShortcutActivated,
                category=unicode(UiStrings().LiveToolbar),
                context=QtCore.Qt.WidgetWithChildrenShortcut)
            self.otherShortcut.setText(translate(
                'OpenLP.SlideController', 'Go to "Other"'))
            self.previewListWidget.addActions([
                self.shortcut0, self.shortcut1, self.shortcut2, self.shortcut3,
                self.shortcut4, self.shortcut5, self.shortcut6, self.shortcut7,
                self.shortcut8, self.shortcut9, self.verseShortcut,
                self.chorusShortcut, self.bridgeShortcut,
                self.preChorusShortcut, self.introShortcut, self.endingShortcut,
                self.otherShortcut
            ])
            QtCore.QObject.connect(
                self.shortcutTimer, QtCore.SIGNAL(u'timeout()'),
                self.slideShortcutActivated)
        # Signals
        QtCore.QObject.connect(self.previewListWidget,
            QtCore.SIGNAL(u'clicked(QModelIndex)'), self.onSlideSelected)
        if self.isLive:
            QtCore.QObject.connect(Receiver.get_receiver(),
                QtCore.SIGNAL(u'slidecontroller_live_spin_delay'),
                self.receiveSpinDelay)
            QtCore.QObject.connect(Receiver.get_receiver(),
                QtCore.SIGNAL(u'slidecontroller_toggle_display'),
                self.toggleDisplay)
            self.toolbar.makeWidgetsInvisible(self.loopList)
        else:
            QtCore.QObject.connect(self.previewListWidget,
                QtCore.SIGNAL(u'doubleClicked(QModelIndex)'),
                self.onGoLiveClick)
            self.toolbar.makeWidgetsInvisible(self.songEditList)
        if self.isLive:
            self.setLiveHotkeys(self)
            self.__addActionsToWidget(self.previewListWidget)
        else:
            self.setPreviewHotkeys()
            self.previewListWidget.addActions(
                [self.nextItem,
                self.previousItem])
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'slidecontroller_%s_stop_loop' % self.typePrefix),
            self.onStopLoop)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'slidecontroller_%s_next' % self.typePrefix),
            self.onSlideSelectedNext)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'slidecontroller_%s_previous' % self.typePrefix),
            self.onSlideSelectedPrevious)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'slidecontroller_%s_change' % self.typePrefix),
            self.onSlideChange)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'slidecontroller_%s_set' % self.typePrefix),
            self.onSlideSelectedIndex)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'slidecontroller_%s_blank' % self.typePrefix),
            self.onSlideBlank)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'slidecontroller_%s_unblank' % self.typePrefix),
            self.onSlideUnblank)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'slidecontroller_update_slide_limits'),
            self.updateSlideLimits)

    def slideShortcutActivated(self):
        """
        Called, when a shortcut has been activated to jump to a chorus, verse,
        etc.

        **Note**: This implementation is based on shortcuts. But it rather works
        like "key sequenes". You have to press one key after the other and
        **not** at the same time.
        For example to jump to "V3" you have to press "V" and afterwards but
        within a time frame of 350ms you have to press "3".
        """
        try:
            from openlp.plugins.songs.lib import VerseType
            SONGS_PLUGIN_AVAILABLE = True
        except ImportError:
            SONGS_PLUGIN_AVAILABLE = False
        verse_type = unicode(self.sender().objectName())
        if verse_type.startswith(u'verseShortcut'):
            if SONGS_PLUGIN_AVAILABLE:
                self.current_shortcut = \
                    VerseType.TranslatedTags[VerseType.Verse]
            else:
                self.current_shortcut = u'V'
        elif verse_type.startswith(u'chorusShortcut'):
            if SONGS_PLUGIN_AVAILABLE:
                self.current_shortcut = \
                    VerseType.TranslatedTags[VerseType.Chorus]
            else:
                self.current_shortcut = u'C'
        elif verse_type.startswith(u'bridgeShortcut'):
            if SONGS_PLUGIN_AVAILABLE:
                self.current_shortcut = \
                    VerseType.TranslatedTags[VerseType.Bridge]
            else:
                self.current_shortcut = u'B'
        elif verse_type.startswith(u'preChorusShortcut'):
            if SONGS_PLUGIN_AVAILABLE:
                self.current_shortcut = \
                    VerseType.TranslatedTags[VerseType.PreChorus]
            else:
                self.current_shortcut = u'P'
        elif verse_type.startswith(u'introShortcut'):
            if SONGS_PLUGIN_AVAILABLE:
                self.current_shortcut = \
                    VerseType.TranslatedTags[VerseType.Intro]
            else:
                self.current_shortcut = u'I'
        elif verse_type.startswith(u'endingShortcut'):
            if SONGS_PLUGIN_AVAILABLE:
                self.current_shortcut = \
                    VerseType.TranslatedTags[VerseType.Ending]
            else:
                self.current_shortcut = u'E'
        elif verse_type.startswith(u'otherShortcut'):
            if SONGS_PLUGIN_AVAILABLE:
                self.current_shortcut = \
                    VerseType.TranslatedTags[VerseType.Other]
            else:
                self.current_shortcut = u'O'
        elif verse_type.isnumeric():
            self.current_shortcut += verse_type
        self.current_shortcut = self.current_shortcut.upper()
        keys = self.slideList.keys()
        matches = [match for match in keys
            if match.startswith(self.current_shortcut)]
        if len(matches) == 1:
            self.shortcutTimer.stop()
            self.current_shortcut = u''
            self.__checkUpdateSelectedSlide(self.slideList[matches[0]])
            self.slideSelected()
        elif verse_type != u'shortcutTimer':
            # Start the time as we did not have any match.
            self.shortcutTimer.start(350)
        else:
            # The timer timed out.
            if self.current_shortcut in keys:
                # We had more than one match for example "V1" and "V10", but
                # "V1" was the slide we wanted to go.
                self.__checkUpdateSelectedSlide(
                    self.slideList[self.current_shortcut])
                self.slideSelected()
           # Reset the shortcut.
            self.current_shortcut = u''

    def setPreviewHotkeys(self):
        self.previousItem.setObjectName(u'previousItemPreview')
        self.nextItem.setObjectName(u'nextItemPreview')
        action_list = ActionList.get_instance()
        action_list.add_action(self.previousItem)
        action_list.add_action(self.nextItem)

    def setLiveHotkeys(self, parent=None):
        self.previousItem.setObjectName(u'previousItemLive')
        self.nextItem.setObjectName(u'nextItemLive')
        action_list = ActionList.get_instance()
        action_list.add_category(
            unicode(UiStrings().LiveToolbar), CategoryOrder.standardToolbar)
        action_list.add_action(self.previousItem)
        action_list.add_action(self.nextItem)
        self.previousService = shortcut_action(parent, u'previousService',
            [QtCore.Qt.Key_Left], self.servicePrevious,
            category=unicode(UiStrings().LiveToolbar),
            context=QtCore.Qt.WidgetWithChildrenShortcut)
        self.previousService.setText(
            translate('OpenLP.SlideController', 'Previous Service'))
        self.nextService = shortcut_action(parent, 'nextService',
            [QtCore.Qt.Key_Right], self.serviceNext,
            category=unicode(UiStrings().LiveToolbar),
            context=QtCore.Qt.WidgetWithChildrenShortcut)
        self.nextService.setText(
            translate('OpenLP.SlideController', 'Next Service'))
        self.escapeItem = shortcut_action(parent, 'escapeItem',
            [QtCore.Qt.Key_Escape], self.liveEscape,
            category=unicode(UiStrings().LiveToolbar),
            context=QtCore.Qt.WidgetWithChildrenShortcut)
        self.escapeItem.setText(
            translate('OpenLP.SlideController', 'Escape Item'))

    def liveEscape(self):
        self.display.setVisible(False)
        self.mediaController.video_stop([self])

    def toggleDisplay(self, action):
        """
        Toggle the display settings triggered from remote messages.
        """
        if action == u'blank' or action == u'hide':
            self.onBlankDisplay(True)
        elif action == u'theme':
            self.onThemeDisplay(True)
        elif action == u'desktop':
            self.onHideDisplay(True)
        elif action == u'show':
            self.onBlankDisplay(False)
            self.onThemeDisplay(False)
            self.onHideDisplay(False)

    def servicePrevious(self):
        """
        Live event to select the previous service item from the service manager.
        """
        self.keypress_queue.append(ServiceItemAction.Previous)
        self._process_queue()

    def serviceNext(self):
        """
        Live event to select the next service item from the service manager.
        """
        self.keypress_queue.append(ServiceItemAction.Next)
        self._process_queue()

    def _process_queue(self):
        """
        Process the service item request queue.  The key presses can arrive
        faster than the processing so implement a FIFO queue.
        """
        if len(self.keypress_queue):
            while len(self.keypress_queue) and not self.keypress_loop:
                self.keypress_loop = True
                keypressCommand = self.keypress_queue.popleft()
                if keypressCommand == ServiceItemAction.Previous:
                    Receiver.send_message('servicemanager_previous_item')
                elif keypressCommand == ServiceItemAction.PreviousLastSlide:
                    # Go to the last slide of the previous item
                    Receiver.send_message('servicemanager_previous_item', u'last slide')
                else:
                    Receiver.send_message('servicemanager_next_item')
            self.keypress_loop = False

    def screenSizeChanged(self):
        """
        Settings dialog has changed the screen size of adjust output and
        screen previews.
        """
        # rebuild display as screen size changed
        if self.display:
            self.display.close()
        self.display = MainDisplay(self, self.imageManager, self.isLive,
            self)
        self.display.setup()
        if self.isLive:
            self.__addActionsToWidget(self.display)
            self.display.audioPlayer.connectSlot(QtCore.SIGNAL(u'tick(qint64)'), self.onAudioTimeRemaining)
        # The SlidePreview's ratio.
        try:
            self.ratio = float(self.screens.current[u'size'].width()) / \
                float(self.screens.current[u'size'].height())
        except ZeroDivisionError:
            self.ratio = 1
        self.mediaController.setup_display(self.display)
        self.previewSizeChanged()
        self.previewDisplay.setup()
        serviceItem = ServiceItem()
        self.previewDisplay.webView.setHtml(build_html(serviceItem,
            self.previewDisplay.screen, None, self.isLive,
            plugins=PluginManager.get_instance().plugins))
        self.mediaController.setup_display(self.previewDisplay)
        if self.serviceItem:
            self.refreshServiceItem()

    def __addActionsToWidget(self, widget):
        widget.addActions([
            self.previousItem, self.nextItem,
            self.previousService, self.nextService,
            self.escapeItem])

    def previewSizeChanged(self):
        """
        Takes care of the SlidePreview's size. Is called when one of the the
        splitters is moved or when the screen size is changed. Note, that this
        method is (also) called frequently from the mainwindow *paintEvent*.
        """
        if self.ratio < float(self.previewFrame.width()) / float(
            self.previewFrame.height()):
            # We have to take the height as limit.
            max_height = self.previewFrame.height() - self.grid.margin() * 2
            self.slidePreview.setFixedSize(QtCore.QSize(
                max_height * self.ratio, max_height))
            self.previewDisplay.setFixedSize(QtCore.QSize(
                max_height * self.ratio, max_height))
            self.previewDisplay.screen = {
                u'size': self.previewDisplay.geometry()}
        else:
            # We have to take the width as limit.
            max_width = self.previewFrame.width() - self.grid.margin() * 2
            self.slidePreview.setFixedSize(QtCore.QSize(max_width,
                max_width / self.ratio))
            self.previewDisplay.setFixedSize(QtCore.QSize(max_width,
                max_width / self.ratio))
            self.previewDisplay.screen = {
                u'size': self.previewDisplay.geometry()}
        # Make sure that the frames have the correct size.
        self.previewListWidget.setColumnWidth(0,
            self.previewListWidget.viewport().size().width())
        if self.serviceItem:
            # Sort out songs, bibles, etc.
            if self.serviceItem.is_text():
                self.previewListWidget.resizeRowsToContents()
            else:
                # Sort out image heights.
                width = self.parent().controlSplitter.sizes()[self.split]
                for framenumber in range(len(self.serviceItem.get_frames())):
                    self.previewListWidget.setRowHeight(
                        framenumber, width / self.ratio)

    def onSongBarHandler(self):
        request = unicode(self.sender().text())
        slideno = self.slideList[request]
        self.__updatePreviewSelection(slideno)
        self.slideSelected()

    def receiveSpinDelay(self, value):
        """
        Adjusts the value of the ``delaySpinBox`` to the given one.
        """
        self.delaySpinBox.setValue(int(value))

    def updateSlideLimits(self):
        """
        Updates the Slide Limits variable from the settings.
        """
        self.slide_limits = QtCore.QSettings().value(
            self.parent().advancedlSettingsSection + u'/slide limits',
            QtCore.QVariant(SlideLimits.End)).toInt()[0]

    def enableToolBar(self, item):
        """
        Allows the toolbars to be reconfigured based on Controller Type
        and ServiceItem Type
        """
        if self.isLive:
            self.enableLiveToolBar(item)
        else:
            self.enablePreviewToolBar(item)

    def enableLiveToolBar(self, item):
        """
        Allows the live toolbar to be customised
        """
        # Work-around for OS X, hide and then show the toolbar
        # See bug #791050
        self.toolbar.hide()
        self.mediabar.setVisible(False)
        self.toolbar.makeWidgetsInvisible([u'Song Menu'])
        self.toolbar.makeWidgetsInvisible(self.loopList)
        # Reset the button
        self.playSlidesOnce.setChecked(False)
        self.playSlidesOnce.setIcon(build_icon(u':/media/media_time.png'))
        self.playSlidesLoop.setChecked(False)
        self.playSlidesLoop.setIcon(build_icon(u':/media/media_time.png'))
        if item.is_text():
            if QtCore.QSettings().value(
                self.parent().songsSettingsSection + u'/display songbar',
                QtCore.QVariant(True)).toBool() and len(self.slideList) > 0:
                self.toolbar.makeWidgetsVisible([u'Song Menu'])
        if item.is_capable(ItemCapabilities.CanLoop) and \
            len(item.get_frames()) > 1:
            self.toolbar.makeWidgetsVisible(self.loopList)
        if item.is_media():
            self.mediabar.setVisible(True)
            self.toolbar.makeWidgetsInvisible(self.nextPreviousList)
        else:
            # Work-around for OS X, hide and then show the toolbar
            # See bug #791050
            self.toolbar.makeWidgetsVisible(self.nextPreviousList)
        self.toolbar.show()

    def enablePreviewToolBar(self, item):
        """
        Allows the Preview toolbar to be customised
        """
        # Work-around for OS X, hide and then show the toolbar
        # See bug #791050
        self.toolbar.hide()
        self.mediabar.setVisible(False)
        self.toolbar.makeWidgetsInvisible(self.songEditList)
        if item.is_capable(ItemCapabilities.CanEdit) and item.from_plugin:
            self.toolbar.makeWidgetsVisible(self.songEditList)
        elif item.is_media():
            self.mediabar.setVisible(True)
            self.toolbar.makeWidgetsInvisible(self.nextPreviousList)
        if not item.is_media():
            # Work-around for OS X, hide and then show the toolbar
            # See bug #791050
            self.toolbar.makeWidgetsVisible(self.nextPreviousList)
        self.toolbar.show()

    def refreshServiceItem(self):
        """
        Method to update the service item if the screen has changed
        """
        log.debug(u'refreshServiceItem live = %s' % self.isLive)
        if self.serviceItem.is_text() or self.serviceItem.is_image():
            item = self.serviceItem
            item.render()
            self._processItem(item, self.selectedRow)

    def addServiceItem(self, item):
        """
        Method to install the service item into the controller
        Called by plugins
        """
        log.debug(u'addServiceItem live = %s' % self.isLive)
        item.render()
        slideno = 0
        if self.songEdit:
            slideno = self.selectedRow
        self.songEdit = False
        self._processItem(item, slideno)

    def replaceServiceManagerItem(self, item):
        """
        Replacement item following a remote edit
        """
        if item == self.serviceItem:
            self._processItem(item, self.previewListWidget.currentRow())

    def addServiceManagerItem(self, item, slideno):
        """
        Method to install the service item into the controller and
        request the correct toolbar for the plugin.
        Called by ServiceManager
        """
        log.debug(u'addServiceManagerItem live = %s' % self.isLive)
        # If no valid slide number is specified we take the first one, but we
        # remember the initial value to see if we should reload the song or not
        slidenum = slideno
        if slideno == -1:
            slidenum = 0
        # If service item is the same as the current one, only change slide
        if slideno >= 0 and item == self.serviceItem:
            self.__checkUpdateSelectedSlide(slidenum)
            self.slideSelected()
        else:
            self._processItem(item, slidenum)

    def _processItem(self, serviceItem, slideno):
        """
        Loads a ServiceItem into the system from ServiceManager
        Display the slide number passed
        """
        log.debug(u'processManagerItem live = %s' % self.isLive)
        self.onStopLoop()
        old_item = self.serviceItem
        # take a copy not a link to the servicemanager copy.
        self.serviceItem = copy.copy(serviceItem)
        if old_item and self.isLive and old_item.is_capable(
            ItemCapabilities.ProvidesOwnDisplay):
            self._resetBlank()
        Receiver.send_message(u'%s_start' % serviceItem.name.lower(),
            [serviceItem, self.isLive, self.hideMode(), slideno])
        self.slideList = {}
        width = self.parent().controlSplitter.sizes()[self.split]
        self.previewListWidget.clear()
        self.previewListWidget.setRowCount(0)
        self.previewListWidget.setColumnWidth(0, width)
        if self.isLive:
            self.songMenu.menu().clear()
            self.display.audioPlayer.reset()
            self.setAudioItemsVisibility(False)
            self.audioPauseItem.setChecked(False)
            # If the current item has background audio
            if self.serviceItem.is_capable(ItemCapabilities.HasBackgroundAudio):
                log.debug(u'Starting to play...')
                self.display.audioPlayer.addToPlaylist(
                    self.serviceItem.background_audio)
                self.trackMenu.clear()
                for counter in range(len(self.serviceItem.background_audio)):
                    action = self.trackMenu.addAction(os.path.basename(
                        self.serviceItem.background_audio[counter]))
                    action.setData(counter)
                    QtCore.QObject.connect(action,
                        QtCore.SIGNAL(u'triggered(bool)'),
                        self.onTrackTriggered)
                self.display.audioPlayer.repeat = QtCore.QSettings().value(
                    self.parent().generalSettingsSection + \
                        u'/audio repeat list',
                    QtCore.QVariant(False)).toBool()
                if QtCore.QSettings().value(
                    self.parent().generalSettingsSection + \
                        u'/audio start paused',
                    QtCore.QVariant(True)).toBool():
                    self.audioPauseItem.setChecked(True)
                    self.display.audioPlayer.pause()
                else:
                    self.display.audioPlayer.play()
                self.setAudioItemsVisibility(True)
        row = 0
        text = []
        for framenumber, frame in enumerate(self.serviceItem.get_frames()):
            self.previewListWidget.setRowCount(
                self.previewListWidget.rowCount() + 1)
            item = QtGui.QTableWidgetItem()
            slideHeight = 0
            if self.serviceItem.is_text():
                if frame[u'verseTag']:
                    # These tags are already translated.
                    verse_def = frame[u'verseTag']
                    verse_def = u'%s%s' % (verse_def[0], verse_def[1:])
                    two_line_def = u'%s\n%s' % (verse_def[0], verse_def[1:])
                    row = two_line_def
                    if verse_def not in self.slideList:
                        self.slideList[verse_def] = framenumber
                        if self.isLive:
                            self.songMenu.menu().addAction(verse_def,
                                self.onSongBarHandler)
                else:
                    row += 1
                    self.slideList[unicode(row)] = row - 1
                item.setText(frame[u'text'])
            else:
                label = QtGui.QLabel()
                label.setMargin(4)
                label.setScaledContents(True)
                if self.serviceItem.is_command():
                    label.setPixmap(QtGui.QPixmap(frame[u'image']))
                else:
                    # If current slide set background to image
                    if framenumber == slideno:
                        self.serviceItem.bg_image_bytes = \
                            self.imageManager.get_image_bytes(frame[u'title'])
                    image = self.imageManager.get_image(frame[u'title'])
                    label.setPixmap(QtGui.QPixmap.fromImage(image))
                self.previewListWidget.setCellWidget(framenumber, 0, label)
                slideHeight = width * self.parent().renderer.screen_ratio
                row += 1
                self.slideList[unicode(row)] = row - 1
            text.append(unicode(row))
            self.previewListWidget.setItem(framenumber, 0, item)
            if not slideHeight:
                self.previewListWidget.setRowHeight(framenumber, slideHeight)
        self.previewListWidget.setVerticalHeaderLabels(text)
        if self.serviceItem.is_text():
            self.previewListWidget.resizeRowsToContents()
        self.previewListWidget.setColumnWidth(0,
            self.previewListWidget.viewport().size().width())
        self.__updatePreviewSelection(slideno)
        self.enableToolBar(serviceItem)
        # Pass to display for viewing.
        # Postpone image build, we need to do this later to avoid the theme
        # flashing on the screen
        if not self.serviceItem.is_image():
            self.display.buildHtml(self.serviceItem)
        if serviceItem.is_media():
            self.onMediaStart(serviceItem)
        self.slideSelected(True)
        self.previewListWidget.setFocus()
        if old_item:
            # Close the old item after the new one is opened
            # This avoids the service theme/desktop flashing on screen
            # However opening a new item of the same type will automatically
            # close the previous, so make sure we don't close the new one.
            if old_item.is_command() and not serviceItem.is_command():
                Receiver.send_message(u'%s_stop' %
                    old_item.name.lower(), [old_item, self.isLive])
            if old_item.is_media() and not serviceItem.is_media():
                self.onMediaClose()
        Receiver.send_message(u'slidecontroller_%s_started' % self.typePrefix,
            [serviceItem])

    def __updatePreviewSelection(self, slideno):
        """
        Utility method to update the selected slide in the list.
        """
        if slideno > self.previewListWidget.rowCount():
            self.previewListWidget.selectRow(
                self.previewListWidget.rowCount() - 1)
        else:
            self.__checkUpdateSelectedSlide(slideno)

    # Screen event methods
    def onSlideSelectedIndex(self, message):
        """
        Go to the requested slide
        """
        index = int(message[0])
        if not self.serviceItem:
            return
        if self.serviceItem.is_command():
            Receiver.send_message(u'%s_slide' % self.serviceItem.name.lower(),
                [self.serviceItem, self.isLive, index])
            self.updatePreview()
        else:
            self.__checkUpdateSelectedSlide(index)
            self.slideSelected()

    def mainDisplaySetBackground(self):
        """
        Allow the main display to blank the main display at startup time
        """
        log.debug(u'mainDisplaySetBackground live = %s' % self.isLive)
        display_type = QtCore.QSettings().value(
            self.parent().generalSettingsSection + u'/screen blank',
            QtCore.QVariant(u'')).toString()
        if self.screens.which_screen(self.window()) != \
            self.screens.which_screen(self.display):
            # Order done to handle initial conversion
            if display_type == u'themed':
                self.onThemeDisplay(True)
            elif display_type == u'hidden':
                self.onHideDisplay(True)
            elif display_type == u'blanked':
                self.onBlankDisplay(True)
            else:
                Receiver.send_message(u'live_display_show')
        else:
            self.liveEscape()

    def onSlideBlank(self):
        """
        Handle the slidecontroller blank event
        """
        self.onBlankDisplay(True)

    def onSlideUnblank(self):
        """
        Handle the slidecontroller unblank event
        """
        self.onBlankDisplay(False)

    def onBlankDisplay(self, checked=None):
        """
        Handle the blank screen button actions
        """
        if checked is None:
            checked = self.blankScreen.isChecked()
        log.debug(u'onBlankDisplay %s' % checked)
        self.hideMenu.setDefaultAction(self.blankScreen)
        self.blankScreen.setChecked(checked)
        self.themeScreen.setChecked(False)
        self.desktopScreen.setChecked(False)
        if checked:
            QtCore.QSettings().setValue(
                self.parent().generalSettingsSection + u'/screen blank',
                QtCore.QVariant(u'blanked'))
        else:
            QtCore.QSettings().remove(
                self.parent().generalSettingsSection + u'/screen blank')
        self.blankPlugin()
        self.updatePreview()

    def onThemeDisplay(self, checked=None):
        """
        Handle the Theme screen button
        """
        if checked is None:
            checked = self.themeScreen.isChecked()
        log.debug(u'onThemeDisplay %s' % checked)
        self.hideMenu.setDefaultAction(self.themeScreen)
        self.blankScreen.setChecked(False)
        self.themeScreen.setChecked(checked)
        self.desktopScreen.setChecked(False)
        if checked:
            QtCore.QSettings().setValue(
                self.parent().generalSettingsSection + u'/screen blank',
                QtCore.QVariant(u'themed'))
        else:
            QtCore.QSettings().remove(
                self.parent().generalSettingsSection + u'/screen blank')
        self.blankPlugin()
        self.updatePreview()

    def onHideDisplay(self, checked=None):
        """
        Handle the Hide screen button
        """
        if checked is None:
            checked = self.desktopScreen.isChecked()
        log.debug(u'onHideDisplay %s' % checked)
        self.hideMenu.setDefaultAction(self.desktopScreen)
        self.blankScreen.setChecked(False)
        self.themeScreen.setChecked(False)
        self.desktopScreen.setChecked(checked)
        if checked:
            QtCore.QSettings().setValue(
                self.parent().generalSettingsSection + u'/screen blank',
                QtCore.QVariant(u'hidden'))
        else:
            QtCore.QSettings().remove(
                self.parent().generalSettingsSection + u'/screen blank')
        self.hidePlugin(checked)
        self.updatePreview()

    def blankPlugin(self):
        """
        Blank/Hide the display screen within a plugin if required.
        """
        hide_mode = self.hideMode()
        log.debug(u'blankPlugin %s ', hide_mode)
        if self.serviceItem is not None:
            if hide_mode:
                if not self.serviceItem.is_command():
                    Receiver.send_message(u'live_display_hide', hide_mode)
                Receiver.send_message(u'%s_blank'
                    % self.serviceItem.name.lower(),
                    [self.serviceItem, self.isLive, hide_mode])
            else:
                if not self.serviceItem.is_command():
                    Receiver.send_message(u'live_display_show')
                Receiver.send_message(u'%s_unblank'
                    % self.serviceItem.name.lower(),
                    [self.serviceItem, self.isLive])
        else:
            if hide_mode:
                Receiver.send_message(u'live_display_hide', hide_mode)
            else:
                Receiver.send_message(u'live_display_show')

    def hidePlugin(self, hide):
        """
        Tell the plugin to hide the display screen.
        """
        log.debug(u'hidePlugin %s ', hide)
        if self.serviceItem is not None:
            if hide:
                Receiver.send_message(u'live_display_hide', HideMode.Screen)
                Receiver.send_message(u'%s_hide'
                    % self.serviceItem.name.lower(),
                    [self.serviceItem, self.isLive])
            else:
                if not self.serviceItem.is_command():
                    Receiver.send_message(u'live_display_show')
                Receiver.send_message(u'%s_unblank'
                    % self.serviceItem.name.lower(),
                    [self.serviceItem, self.isLive])
        else:
            if hide:
                Receiver.send_message(u'live_display_hide', HideMode.Screen)
            else:
                Receiver.send_message(u'live_display_show')

    def onSlideSelected(self):
        """
        Slide selected in controller
        """
        self.slideSelected()

    def slideSelected(self, start=False):
        """
        Generate the preview when you click on a slide.
        if this is the Live Controller also display on the screen
        """
        row = self.previewListWidget.currentRow()
        self.selectedRow = 0
        if row > -1 and row < self.previewListWidget.rowCount():
            if self.serviceItem.is_command():
                if self.isLive and not start:
                    Receiver.send_message(
                        u'%s_slide' % self.serviceItem.name.lower(),
                        [self.serviceItem, self.isLive, row])
            else:
                toDisplay = self.serviceItem.get_rendered_frame(row)
                if self.serviceItem.is_text():
                    self.display.text(toDisplay)
                else:
                    if start:
                        self.display.buildHtml(self.serviceItem, toDisplay)
                    else:
                        self.display.image(toDisplay)
                    # reset the store used to display first image
                    self.serviceItem.bg_image_bytes = None
            self.updatePreview()
            self.selectedRow = row
            self.__checkUpdateSelectedSlide(row)
        Receiver.send_message(u'slidecontroller_%s_changed' % self.typePrefix,
            row)

    def onSlideChange(self, row):
        """
        The slide has been changed. Update the slidecontroller accordingly
        """
        self.__checkUpdateSelectedSlide(row)
        self.updatePreview()
        Receiver.send_message(u'slidecontroller_%s_changed' % self.typePrefix,
            row)

    def updatePreview(self):
        """
        This updates the preview frame, for example after changing a slide or
        using *Blank to Theme*.
        """
        log.debug(u'updatePreview %s ' % self.screens.current[u'primary'])
        if not self.screens.current[u'primary'] and self.serviceItem and \
            self.serviceItem.is_capable(ItemCapabilities.ProvidesOwnDisplay):
            # Grab now, but try again in a couple of seconds if slide change
            # is slow
            QtCore.QTimer.singleShot(0.5, self.grabMainDisplay)
            QtCore.QTimer.singleShot(2.5, self.grabMainDisplay)
        else:
            self.slidePreview.setPixmap(self.display.preview())

    def grabMainDisplay(self):
        """
        Creates an image of the current screen and updates the preview frame.
        """
        winid = QtGui.QApplication.desktop().winId()
        rect = self.screens.current[u'size']
        winimg = QtGui.QPixmap.grabWindow(winid, rect.x(),
            rect.y(), rect.width(), rect.height())
        self.slidePreview.setPixmap(winimg)

    def onSlideSelectedNext(self, wrap=None):
        """
        Go to the next slide.
        """
        if not self.serviceItem:
            return
        Receiver.send_message(u'%s_next' % self.serviceItem.name.lower(),
            [self.serviceItem, self.isLive])
        if self.serviceItem.is_command() and self.isLive:
            self.updatePreview()
        else:
            row = self.previewListWidget.currentRow() + 1
            if row == self.previewListWidget.rowCount():
                if wrap is None:
                    if self.slide_limits == SlideLimits.Wrap:
                        row = 0
                    elif self.isLive and self.slide_limits == SlideLimits.Next:
                        self.serviceNext()
                        return
                    else:
                        row = self.previewListWidget.rowCount() - 1
                elif wrap:
                    row = 0
                else:
                    row = self.previewListWidget.rowCount() - 1
            self.__checkUpdateSelectedSlide(row)
            self.slideSelected()

    def onSlideSelectedPrevious(self):
        """
        Go to the previous slide.
        """
        if not self.serviceItem:
            return
        Receiver.send_message(u'%s_previous' % self.serviceItem.name.lower(),
            [self.serviceItem, self.isLive])
        if self.serviceItem.is_command() and self.isLive:
            self.updatePreview()
        else:
            row = self.previewListWidget.currentRow() - 1
            if row == -1:
                if self.slide_limits == SlideLimits.Wrap:
                    row = self.previewListWidget.rowCount() - 1
                elif self.isLive and self.slide_limits == SlideLimits.Next:
                    self.keypress_queue.append(ServiceItemAction.PreviousLastSlide)
                    self._process_queue()
                    return
                else:
                    row = 0
            self.__checkUpdateSelectedSlide(row)
            self.slideSelected()

    def __checkUpdateSelectedSlide(self, row):
        if row + 1 < self.previewListWidget.rowCount():
            self.previewListWidget.scrollToItem(
                self.previewListWidget.item(row + 1, 0))
        self.previewListWidget.selectRow(row)

    def onToggleLoop(self):
        """
        Toggles the loop state.
        """
        if self.playSlidesLoop.isChecked() or self.playSlidesOnce.isChecked():
            self.onStartLoop()
        else:
            self.onStopLoop()

    def onStartLoop(self):
        """
        Start the timer loop running and store the timer id
        """
        if self.previewListWidget.rowCount() > 1:
            self.timer_id = self.startTimer(
                int(self.delaySpinBox.value()) * 1000)

    def onStopLoop(self):
        """
        Stop the timer loop running
        """
        if self.timer_id != 0:
            self.killTimer(self.timer_id)
            self.timer_id = 0

    def onPlaySlidesLoop(self, checked=None):
        """
        Start or stop 'Play Slides in Loop'
        """
        if checked is None:
            checked = self.playSlidesLoop.isChecked()
        else:
            self.playSlidesLoop.setChecked(checked)
        log.debug(u'onPlaySlidesLoop %s' % checked)
        if checked:
            self.playSlidesLoop.setIcon(build_icon(u':/media/media_stop.png'))
            self.playSlidesLoop.setText(UiStrings().StopPlaySlidesInLoop)
            self.playSlidesOnce.setIcon(build_icon(u':/media/media_time.png'))
            self.playSlidesOnce.setText(UiStrings().PlaySlidesToEnd)
        else:
            self.playSlidesLoop.setIcon(build_icon(u':/media/media_time.png'))
            self.playSlidesLoop.setText(UiStrings().PlaySlidesInLoop)
        self.playSlidesMenu.setDefaultAction(self.playSlidesLoop)
        self.playSlidesOnce.setChecked(False)
        self.onToggleLoop()

    def onPlaySlidesOnce(self, checked=None):
        """
        Start or stop 'Play Slides to End'
        """
        if checked is None:
            checked = self.playSlidesOnce.isChecked()
        else:
            self.playSlidesOnce.setChecked(checked)
        log.debug(u'onPlaySlidesOnce %s' % checked)
        if checked:
            self.playSlidesOnce.setIcon(build_icon(u':/media/media_stop.png'))
            self.playSlidesOnce.setText(UiStrings().StopPlaySlidesToEnd)
            self.playSlidesLoop.setIcon(build_icon(u':/media/media_time.png'))
            self.playSlidesLoop.setText(UiStrings().PlaySlidesInLoop)
        else:
            self.playSlidesOnce.setIcon(build_icon(u':/media/media_time'))
            self.playSlidesOnce.setText(UiStrings().PlaySlidesToEnd)
        self.playSlidesMenu.setDefaultAction(self.playSlidesOnce)
        self.playSlidesLoop.setChecked(False)
        self.onToggleLoop()

    def setAudioItemsVisibility(self, visible):
        if visible:
            self.toolbar.makeWidgetsVisible([u'Song Menu', u'Pause Audio', u'Time Remaining'])
        else:
            self.toolbar.makeWidgetsInvisible([u'Song Menu', u'Pause Audio', u'Time Remaining'])

    def onAudioPauseClicked(self, checked):
        if not self.audioPauseItem.isVisible():
            return
        if checked:
            self.display.audioPlayer.pause()
        else:
            self.display.audioPlayer.play()

    def timerEvent(self, event):
        """
        If the timer event is for this window select next slide
        """
        if event.timerId() == self.timer_id:
            self.onSlideSelectedNext(self.playSlidesLoop.isChecked())

    def onEditSong(self):
        """
        From the preview display requires the service Item to be editied
        """
        self.songEdit = True
        Receiver.send_message(u'%s_edit' % self.serviceItem.name.lower(),
            u'P:%s' % self.serviceItem.edit_id)

    def onPreviewAddToService(self):
        """
        From the preview display request the Item to be added to service
        """
        if self.serviceItem:
            self.parent().serviceManagerContents.addServiceItem(
                self.serviceItem)

    def onGoLiveClick(self):
        """
        triggered by clicking the Preview slide items
        """
        if QtCore.QSettings().value(u'advanced/double click live',
            QtCore.QVariant(False)).toBool():
            # Live and Preview have issues if we have video or presentations
            # playing in both at the same time.
            if self.serviceItem.is_command():
                Receiver.send_message(u'%s_stop' %
                    self.serviceItem.name.lower(),
                    [self.serviceItem, self.isLive])
            if self.serviceItem.is_media():
                self.onMediaClose()
            self.onGoLive()

    def onGoLive(self):
        """
        If preview copy slide item to live
        """
        row = self.previewListWidget.currentRow()
        if row > -1 and row < self.previewListWidget.rowCount():
            if self.serviceItem.from_service:
                Receiver.send_message('servicemanager_preview_live',
                    u'%s:%s' % (self.serviceItem._uuid, row))
            else:
                self.parent().liveController.addServiceManagerItem(
                    self.serviceItem, row)

    def onMediaStart(self, item):
        """
        Respond to the arrival of a media service item
        """
        log.debug(u'SlideController onMediaStart')
        file = os.path.join(item.get_frame_path(), item.get_frame_title())
        self.mediaController.video(self, file, False, False)
        if not self.isLive or self.mediaController.withLivePreview:
            self.previewDisplay.show()
            self.slidePreview.hide()

    def onMediaClose(self):
        """
        Respond to a request to close the Video
        """
        log.debug(u'SlideController onMediaClose')
        self.mediaController.video_reset(self)
        self.previewDisplay.hide()
        self.slidePreview.show()

    def _resetBlank(self):
        """
        Used by command items which provide their own displays to reset the
        screen hide attributes
        """
        hide_mode = self.hideMode()
        if hide_mode == HideMode.Blank:
            self.onBlankDisplay(True)
        elif hide_mode == HideMode.Theme:
            self.onThemeDisplay(True)
        elif hide_mode == HideMode.Screen:
            self.onHideDisplay(True)
        else:
            self.hidePlugin(False)

    def hideMode(self):
        """
        Determine what the hide mode should be according to the blank button
        """
        if not self.isLive:
            return None
        elif self.blankScreen.isChecked():
            return HideMode.Blank
        elif self.themeScreen.isChecked():
            return HideMode.Theme
        elif self.desktopScreen.isChecked():
            return HideMode.Screen
        else:
            return None

    def onNextTrackClicked(self):
        self.display.audioPlayer.next()

    def onAudioTimeRemaining(self, time):
        seconds = self.display.audioPlayer.mediaObject.remainingTime() // 1000
        minutes = seconds // 60
        seconds %= 60
        self.audioTimeLabel.setText(u' %02d:%02d ' % (minutes, seconds))

    def onTrackTriggered(self):
        action = self.sender()
        index = action.data().toInt()[0]
        self.display.audioPlayer.goTo(index)
