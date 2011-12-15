# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2011 Raoul Snyman                                        #
# Portions copyright (c) 2008-2011 Tim Bentley, Gerald Britton, Jonathan      #
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
"""
The :mod:`advancedtab` provides an advanced settings facility.
"""
from PyQt4 import QtCore, QtGui

from openlp.core.lib import SettingsTab, translate, build_icon
from openlp.core.lib.ui import UiStrings
from openlp.core.utils import get_images_filter
from datetime import datetime
import re

class AdvancedTab(SettingsTab):
    """
    The :class:`AdvancedTab` manages the advanced settings tab including the UI
    and the loading and saving of the displayed settings.
    """
    def __init__(self, parent):
        """
        Initialise the settings tab
        """
        advancedTranslated = translate(u'OpenLP.AdvancedTab', u'Advanced')
        self.default_service_name = unicode(translate(u'OpenLP.AdvancedTab',
            u'Service %Y-%m-%d'))
        self.default_service_example = unicode(translate(u'OpenLP.AdvancedTab',
            u'%Y-%m-%d',
            u'This should be the date part of default service name.'))
        self.wrong_characters_expression = \
            re.compile(r'[\[\]/\;,><&*:%=+@!#^()|?^]+')
        self.default_image = u':/graphics/openlp-splash-screen.png'
        self.default_color = u'#ffffff'
        self.icon_path = u':/system/system_settings.png'
        SettingsTab.__init__(self, parent, u'Advanced', advancedTranslated)

    def setupUi(self):
        """
        Configure the UI elements for the tab.
        """
        self.setObjectName(u'AdvancedTab')
        SettingsTab.setupUi(self)
        self.uiGroupBox = QtGui.QGroupBox(self.leftColumn)
        self.uiGroupBox.setObjectName(u'uiGroupBox')
        self.uiLayout = QtGui.QFormLayout(self.uiGroupBox)
        self.uiLayout.setObjectName(u'uiLayout')
        self.recentLabel = QtGui.QLabel(self.uiGroupBox)
        self.recentLabel.setObjectName(u'recentLabel')
        self.recentSpinBox = QtGui.QSpinBox(self.uiGroupBox)
        self.recentSpinBox.setObjectName(u'recentSpinBox')
        self.recentSpinBox.setMinimum(0)
        self.uiLayout.addRow(self.recentLabel, self.recentSpinBox)
        self.mediaPluginCheckBox = QtGui.QCheckBox(self.uiGroupBox)
        self.mediaPluginCheckBox.setObjectName(u'mediaPluginCheckBox')
        self.uiLayout.addRow(self.mediaPluginCheckBox)
        self.doubleClickLiveCheckBox = QtGui.QCheckBox(self.uiGroupBox)
        self.doubleClickLiveCheckBox.setObjectName(u'doubleClickLiveCheckBox')
        self.uiLayout.addRow(self.doubleClickLiveCheckBox)
        self.singleClickPreviewCheckBox = QtGui.QCheckBox(self.uiGroupBox)
        self.singleClickPreviewCheckBox.setObjectName(
            u'singleClickPreviewCheckBox')
        self.uiLayout.addRow(self.singleClickPreviewCheckBox)
        self.expandServiceItemCheckBox = QtGui.QCheckBox(self.uiGroupBox)
        self.expandServiceItemCheckBox.setObjectName(
            u'expandServiceItemCheckBox')
        self.uiLayout.addRow(self.expandServiceItemCheckBox)
        self.enableAutoCloseCheckBox = QtGui.QCheckBox(self.uiGroupBox)
        self.enableAutoCloseCheckBox.setObjectName(
            u'enableAutoCloseCheckBox')
        self.uiLayout.addRow(self.enableAutoCloseCheckBox)
        self.leftLayout.addWidget(self.uiGroupBox)
        self.defaultServiceGroupBox = QtGui.QGroupBox(self.leftColumn)
        self.defaultServiceGroupBox.setObjectName(u'defaultServiceGroupBox')
        self.defaultServiceLayout = QtGui.QFormLayout(
            self.defaultServiceGroupBox)
        self.defaultServiceLayout.setObjectName(u'defaultServiceLayout')
        self.defaultServiceLabel = QtGui.QLabel(self.defaultServiceGroupBox)
        self.defaultServiceLabel.setObjectName(u'defaultServiceLabel')
        self.defaultServiceEdit = QtGui.QLineEdit(self.defaultServiceGroupBox)
        self.defaultServiceEdit.setObjectName(u'defaultServiceEdit')
        self.defaultServiceRevertButton = QtGui.QToolButton(
            self.defaultServiceGroupBox)
        self.defaultServiceRevertButton.setObjectName(
            u'defaultServiceRevertButton')
        self.defaultServiceRevertButton.setIcon(
            build_icon(u':/general/general_revert.png'))
        self.defaultServiceHBox = QtGui.QHBoxLayout()
        self.defaultServiceHBox.setObjectName(u'defaultServiceHBox')
        self.defaultServiceHBox.addWidget(self.defaultServiceLabel)
        self.defaultServiceHBox.addWidget(self.defaultServiceEdit)
        self.defaultServiceHBox.addWidget(self.defaultServiceRevertButton)
        self.defaultServiceLayout.addRow(self.defaultServiceHBox)
        self.defaultServiceExampleLabel = QtGui.QLabel(
            self.defaultServiceGroupBox)
        self.defaultServiceExampleLabel.setObjectName(
            u'defaultServiceExampleLabel')
        self.defaultServiceExample = QtGui.QLabel(self.defaultServiceGroupBox)
        self.defaultServiceExample.setObjectName(u'defaultServiceExample')
        self.defaultServiceLayout.addRow(self.defaultServiceExampleLabel,
            self.defaultServiceExample)
        self.defaultServiceNoteLabel = QtGui.QLabel(self.defaultServiceGroupBox)
        self.defaultServiceNoteLabel.setWordWrap(True)
        self.defaultServiceNoteLabel.setObjectName(u'defaultServiceNoteLabel')
        self.defaultServiceLayout.addRow(self.defaultServiceNoteLabel)
        self.leftLayout.addWidget(self.defaultServiceGroupBox)
        self.leftLayout.addStretch()
        self.defaultImageGroupBox = QtGui.QGroupBox(self.rightColumn)
        self.defaultImageGroupBox.setObjectName(u'defaultImageGroupBox')
        self.defaultImageLayout = QtGui.QFormLayout(self.defaultImageGroupBox)
        self.defaultImageLayout.setObjectName(u'defaultImageLayout')
        self.defaultColorLabel = QtGui.QLabel(self.defaultImageGroupBox)
        self.defaultColorLabel.setObjectName(u'defaultColorLabel')
        self.defaultColorButton = QtGui.QPushButton(self.defaultImageGroupBox)
        self.defaultColorButton.setObjectName(u'defaultColorButton')
        self.defaultImageLayout.addRow(self.defaultColorLabel,
            self.defaultColorButton)
        self.defaultFileLabel = QtGui.QLabel(self.defaultImageGroupBox)
        self.defaultFileLabel.setObjectName(u'defaultFileLabel')
        self.defaultFileEdit = QtGui.QLineEdit(self.defaultImageGroupBox)
        self.defaultFileEdit.setObjectName(u'defaultFileEdit')
        self.defaultBrowseButton = QtGui.QToolButton(self.defaultImageGroupBox)
        self.defaultBrowseButton.setObjectName(u'defaultBrowseButton')
        self.defaultBrowseButton.setIcon(
            build_icon(u':/general/general_open.png'))
        self.defaultRevertButton = QtGui.QToolButton(self.defaultImageGroupBox)
        self.defaultRevertButton.setObjectName(u'defaultRevertButton')
        self.defaultRevertButton.setIcon(
            build_icon(u':/general/general_revert.png'))
        self.defaultFileLayout = QtGui.QHBoxLayout()
        self.defaultFileLayout.setObjectName(u'defaultFileLayout')
        self.defaultFileLayout.addWidget(self.defaultFileEdit)
        self.defaultFileLayout.addWidget(self.defaultBrowseButton)
        self.defaultFileLayout.addWidget(self.defaultRevertButton)
        self.defaultImageLayout.addRow(self.defaultFileLabel,
            self.defaultFileLayout)
        self.rightLayout.addWidget(self.defaultImageGroupBox)
        self.hideMouseGroupBox = QtGui.QGroupBox(self.leftColumn)
        self.hideMouseGroupBox.setObjectName(u'hideMouseGroupBox')
        self.hideMouseLayout = QtGui.QVBoxLayout(self.hideMouseGroupBox)
        self.hideMouseLayout.setObjectName(u'hideMouseLayout')
        self.hideMouseCheckBox = QtGui.QCheckBox(self.hideMouseGroupBox)
        self.hideMouseCheckBox.setObjectName(u'hideMouseCheckBox')
        self.hideMouseLayout.addWidget(self.hideMouseCheckBox)
        self.rightLayout.addWidget(self.hideMouseGroupBox)
        self.rightLayout.addStretch()

        QtCore.QObject.connect(self.defaultServiceEdit,
            QtCore.SIGNAL(u'textChanged(QString)'),
            self.onDefaultServiceUpdated)
        QtCore.QObject.connect(self.defaultServiceRevertButton,
            QtCore.SIGNAL(u'pressed()'),
            self.onDefaultServiceRevertButtonPressed)
        QtCore.QObject.connect(self.defaultColorButton,
            QtCore.SIGNAL(u'pressed()'), self.onDefaultColorButtonPressed)
        QtCore.QObject.connect(self.defaultBrowseButton,
            QtCore.SIGNAL(u'pressed()'), self.onDefaultBrowseButtonPressed)
        QtCore.QObject.connect(self.defaultRevertButton,
            QtCore.SIGNAL(u'pressed()'), self.onDefaultRevertButtonPressed)

    def retranslateUi(self):
        """
        Setup the interface translation strings.
        """
        self.tabTitleVisible = UiStrings().Advanced
        self.uiGroupBox.setTitle(
            translate('OpenLP.AdvancedTab', 'UI Settings'))
        self.recentLabel.setText(
            translate('OpenLP.AdvancedTab',
                'Number of recent files to display:'))
        self.mediaPluginCheckBox.setText(translate('OpenLP.AdvancedTab',
            'Remember active media manager tab on startup'))
        self.doubleClickLiveCheckBox.setText(translate('OpenLP.AdvancedTab',
            'Double-click to send items straight to live'))
        self.singleClickPreviewCheckBox.setText(translate('OpenLP.AdvancedTab',
            'Preview items when clicked in Media Manager'))
        self.expandServiceItemCheckBox.setText(translate('OpenLP.AdvancedTab',
            'Expand new service items on creation'))
        self.enableAutoCloseCheckBox.setText(translate('OpenLP.AdvancedTab',
            'Enable application exit confirmation'))
        self.defaultServiceGroupBox.setTitle(
            translate(u'OpenLP.AdvancedTab', u'Default Service'))
        self.defaultServiceLabel.setText(
            translate(u'OpenLP.AdvancedTab', u'Default service name:'))
        self.defaultServiceRevertButton.setToolTip(unicode(
            translate(u'OpenLP.AdvancedTab',
            u'Revert to the default service name "%s".')) %
            self.default_service_name)
        self.defaultServiceExampleLabel.setText(translate('OpenLP.AdvancedTab',
            u'Example:'))
        self.defaultServiceNoteLabel.setText(unicode(
            translate(u'OpenLP.AdvancedTab', u'Default service name when '
            'saving a new service. You can use date placeholders, e.g %s '
            'results in %s. Leave it empty to use no default value.')) % 
            (self.default_service_example,
            datetime.now().strftime(self.default_service_example)))
        self.hideMouseGroupBox.setTitle(translate('OpenLP.AdvancedTab',
            'Mouse Cursor'))
        self.hideMouseCheckBox.setText(translate('OpenLP.AdvancedTab',
            'Hide mouse cursor when over display window'))
        self.defaultImageGroupBox.setTitle(translate('OpenLP.AdvancedTab',
            'Default Image'))
        self.defaultColorLabel.setText(translate('OpenLP.AdvancedTab',
            'Background color:'))
        self.defaultColorButton.setToolTip(translate('OpenLP.AdvancedTab',
            'Click to select a color.'))
        self.defaultFileLabel.setText(translate('OpenLP.AdvancedTab',
            'Image file:'))
        self.defaultBrowseButton.setToolTip(translate('OpenLP.AdvancedTab',
            'Browse for an image file to display.'))
        self.defaultRevertButton.setToolTip(translate('OpenLP.AdvancedTab',
            'Revert to the default OpenLP logo.'))

    def load(self):
        """
        Load settings from disk.
        """
        settings = QtCore.QSettings()
        settings.beginGroup(self.settingsSection)
        # The max recent files value does not have an interface and so never
        # gets actually stored in the settings therefore the default value of
        # 20 will always be used.
        self.recentSpinBox.setMaximum(QtCore.QSettings().value(
            u'max recent files', QtCore.QVariant(20)).toInt()[0])
        self.recentSpinBox.setValue(settings.value(u'recent file count',
            QtCore.QVariant(4)).toInt()[0])
        self.mediaPluginCheckBox.setChecked(
            settings.value(u'save current plugin',
            QtCore.QVariant(False)).toBool())
        self.doubleClickLiveCheckBox.setChecked(
            settings.value(u'double click live',
            QtCore.QVariant(False)).toBool())
        self.singleClickPreviewCheckBox.setChecked(
            settings.value(u'single click preview',
            QtCore.QVariant(False)).toBool())
        self.expandServiceItemCheckBox.setChecked(
            settings.value(u'expand service item',
            QtCore.QVariant(False)).toBool())
        self.enableAutoCloseCheckBox.setChecked(
            settings.value(u'enable exit confirmation',
            QtCore.QVariant(True)).toBool())
        self.hideMouseCheckBox.setChecked(
            settings.value(u'hide mouse', QtCore.QVariant(False)).toBool())
        self.service_name = unicode(settings.value(u'default service name',
            self.default_service_name).toString())
        self.defaultServiceEdit.setText(self.service_name)
        self.default_color = settings.value(u'default color',
            QtCore.QVariant(u'#ffffff')).toString()
        self.defaultFileEdit.setText(settings.value(u'default image',
            QtCore.QVariant(u':/graphics/openlp-splash-screen.png'))\
            .toString())
        settings.endGroup()
        self.defaultColorButton.setStyleSheet(
            u'background-color: %s' % self.default_color)

    def save(self):
        """
        Save settings to disk.
        """
        self.service_name = unicode(self.defaultServiceEdit.text())
        preset_okay, name_example = self.generate_service_name_example(
            self.service_name)
        if not preset_okay:
            # should alert or something
            pass
        settings = QtCore.QSettings()
        settings.beginGroup(self.settingsSection)
        if self.service_name == self.default_service_name:
            settings.remove(u'default service name')
        else:
            settings.setValue(u'default service name', self.service_name)
        settings.setValue(u'recent file count',
            QtCore.QVariant(self.recentSpinBox.value()))
        settings.setValue(u'save current plugin',
            QtCore.QVariant(self.mediaPluginCheckBox.isChecked()))
        settings.setValue(u'double click live',
            QtCore.QVariant(self.doubleClickLiveCheckBox.isChecked()))
        settings.setValue(u'single click preview',
            QtCore.QVariant(self.singleClickPreviewCheckBox.isChecked()))
        settings.setValue(u'expand service item',
            QtCore.QVariant(self.expandServiceItemCheckBox.isChecked()))
        settings.setValue(u'enable exit confirmation',
            QtCore.QVariant(self.enableAutoCloseCheckBox.isChecked()))
        settings.setValue(u'hide mouse',
            QtCore.QVariant(self.hideMouseCheckBox.isChecked()))
        settings.setValue(u'default color', self.default_color)
        settings.setValue(u'default image', self.defaultFileEdit.text())
        settings.endGroup()

    def generate_service_name_example(self, service_name_preset):
        preset_okay = True
        try:
            service_name_example = datetime.now().strftime(
                unicode(service_name_preset))
            if self.wrong_characters_expression.search(service_name_example):
                service_name_example = translate(u'OpenLP.AdvancedTab',
                    u'Filename contains wrong characters.')
                preset_okay = False
        except ValueError:
            service_name_example = translate(u'OpenLP.AdvancedTab',
                u'Syntax error.')
            preset_okay = False
        return preset_okay, service_name_example

    def onDefaultServiceUpdated(self, preset):
        preset_okay, name_example = self.generate_service_name_example(preset)
        self.defaultServiceExample.setText(name_example)

    def onDefaultServiceRevertButtonPressed(self):
        self.defaultServiceEdit.setText(self.default_service_name)
        self.defaultServiceEdit.setFocus()

    def onDefaultColorButtonPressed(self):
        new_color = QtGui.QColorDialog.getColor(
            QtGui.QColor(self.default_color), self)
        if new_color.isValid():
            self.default_color = new_color.name()
            self.defaultColorButton.setStyleSheet(
                u'background-color: %s' % self.default_color)

    def onDefaultBrowseButtonPressed(self):
        file_filters = u'%s;;%s (*.*) (*)' % (get_images_filter(),
            UiStrings().AllFiles)
        filename = QtGui.QFileDialog.getOpenFileName(self,
            translate('OpenLP.AdvancedTab', 'Open File'), '',
            file_filters)
        if filename:
            self.defaultFileEdit.setText(filename)
        self.defaultFileEdit.setFocus()

    def onDefaultRevertButtonPressed(self):
        self.defaultFileEdit.setText(u':/graphics/openlp-splash-screen.png')
        self.defaultFileEdit.setFocus()
