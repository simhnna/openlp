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
"""
The :mod:`ui` module provides standard UI components for OpenLP.
"""
import logging

from PyQt4 import QtCore, QtGui

from openlp.core.lib import build_icon, Receiver, translate
from openlp.core.utils.actions import ActionList

log = logging.getLogger(__name__)

class UiStrings(object):
    """
    Provide standard strings for objects to use.
    """
    __instance__ = None

    def __new__(cls):
        """
        Override the default object creation method to return a single instance.
        """
        if not cls.__instance__:
            cls.__instance__ = object.__new__(cls)
        return cls.__instance__

    def __init__(self):
        """
        These strings should need a good reason to be retranslated elsewhere.
        Should some/more/less of these have an &amp; attached?
        """
        self.About = translate('OpenLP.Ui', 'About')
        self.Add = translate('OpenLP.Ui', '&Add')
        self.Advanced = translate('OpenLP.Ui', 'Advanced')
        self.AllFiles = translate('OpenLP.Ui', 'All Files')
        self.Bottom = translate('OpenLP.Ui', 'Bottom')
        self.Browse = translate('OpenLP.Ui', 'Browse...')
        self.Cancel = translate('OpenLP.Ui', 'Cancel')
        self.CCLINumberLabel = translate('OpenLP.Ui', 'CCLI number:')
        self.CreateService = translate('OpenLP.Ui', 'Create a new service.')
        self.ConfirmDelete = translate('OpenLP.Ui', 'Confirm Delete')
        self.Continuous = translate('OpenLP.Ui', 'Continuous')
        self.Default = unicode(translate('OpenLP.Ui', 'Default'))
        self.Delete = translate('OpenLP.Ui', '&Delete')
        self.DisplayStyle = translate('OpenLP.Ui', 'Display style:')
        self.Duplicate = translate('OpenLP.Ui', 'Duplicate Error')
        self.Edit = translate('OpenLP.Ui', '&Edit')
        self.EmptyField = translate('OpenLP.Ui', 'Empty Field')
        self.Error = translate('OpenLP.Ui', 'Error')
        self.Export = translate('OpenLP.Ui', 'Export')
        self.File = translate('OpenLP.Ui', 'File')
        self.FontSizePtUnit = translate('OpenLP.Ui', 'pt',
            'Abbreviated font pointsize unit')
        self.Help = translate('OpenLP.Ui', 'Help')
        self.Hours = translate('OpenLP.Ui', 'h',
            'The abbreviated unit for hours')
        self.Image = translate('OpenLP.Ui', 'Image')
        self.Import = translate('OpenLP.Ui', 'Import')
        self.LayoutStyle = translate('OpenLP.Ui', 'Layout style:')
        self.Live = translate('OpenLP.Ui', 'Live')
        self.LiveBGError = translate('OpenLP.Ui', 'Live Background Error')
        self.LiveToolbar = translate('OpenLP.Ui', 'Live Toolbar')
        self.Load = translate('OpenLP.Ui', 'Load')
        self.Minutes = translate('OpenLP.Ui', 'm',
            'The abbreviated unit for minutes')
        self.Middle = translate('OpenLP.Ui', 'Middle')
        self.New = translate('OpenLP.Ui', 'New')
        self.NewService = translate('OpenLP.Ui', 'New Service')
        self.NewTheme = translate('OpenLP.Ui', 'New Theme')
        self.NextTrack = translate('OpenLP.Ui', 'Next Track')
        self.NFSs = translate('OpenLP.Ui', 'No File Selected', 'Singular')
        self.NFSp = translate('OpenLP.Ui', 'No Files Selected', 'Plural')
        self.NISs = translate('OpenLP.Ui', 'No Item Selected', 'Singular')
        self.NISp = translate('OpenLP.Ui', 'No Items Selected', 'Plural')
        self.OLPV1 = translate('OpenLP.Ui', 'openlp.org 1.x')
        self.OLPV2 = translate('OpenLP.Ui', 'OpenLP 2.0')
        self.OpenLPStart = translate('OpenLP.Ui', 'OpenLP is already running. '
            'Do you wish to continue?')
        self.OpenService = translate('OpenLP.Ui', 'Open service.')
        self.PlaySlidesInLoop = translate('OpenLP.Ui','Play Slides in Loop')
        self.PlaySlidesToEnd = translate('OpenLP.Ui','Play Slides to End')
        self.Preview = translate('OpenLP.Ui', 'Preview')
        self.PrintService = translate('OpenLP.Ui', 'Print Service')
        self.ReplaceBG = translate('OpenLP.Ui', 'Replace Background')
        self.ReplaceLiveBG = translate('OpenLP.Ui', 'Replace live background.')
        self.ResetBG = translate('OpenLP.Ui', 'Reset Background')
        self.ResetLiveBG = translate('OpenLP.Ui', 'Reset live background.')
        self.Seconds = translate('OpenLP.Ui', 's',
            'The abbreviated unit for seconds')
        self.SaveAndPreview = translate('OpenLP.Ui', 'Save && Preview')
        self.Search = translate('OpenLP.Ui', 'Search')
        self.SearchThemes = translate(
            'OpenLP.Ui', 'Search Themes...', 'Search bar place holder text ')
        self.SelectDelete = translate('OpenLP.Ui', 'You must select an item '
            'to delete.')
        self.SelectEdit = translate('OpenLP.Ui', 'You must select an item to '
            'edit.')
        self.Settings = translate('OpenLP.Ui', 'Settings')
        self.SaveService = translate('OpenLP.Ui', 'Save Service')
        self.Service = translate('OpenLP.Ui', 'Service')
        self.Split = translate('OpenLP.Ui', 'Optional &Split')
        self.SplitToolTip = translate('OpenLP.Ui', 'Split a slide into two '
            'only if it does not fit on the screen as one slide.')
        self.StartTimeCode = unicode(translate('OpenLP.Ui', 'Start %s'))
        self.StopPlaySlidesInLoop = translate('OpenLP.Ui',
            'Stop Play Slides in Loop')
        self.StopPlaySlidesToEnd = translate('OpenLP.Ui',
            'Stop Play Slides to End')
        self.Theme = translate('OpenLP.Ui', 'Theme', 'Singular')
        self.Themes = translate('OpenLP.Ui', 'Themes', 'Plural')
        self.Tools = translate('OpenLP.Ui', 'Tools')
        self.Top = translate('OpenLP.Ui', 'Top')
        self.UnsupportedFile = translate('OpenLP.Ui', 'Unsupported File')
        self.VersePerSlide = translate('OpenLP.Ui', 'Verse Per Slide')
        self.VersePerLine = translate('OpenLP.Ui', 'Verse Per Line')
        self.Version = translate('OpenLP.Ui', 'Version')
        self.View = translate('OpenLP.Ui', 'View')
        self.ViewMode = translate('OpenLP.Ui', 'View Mode')


def add_welcome_page(parent, image):
    """
    Generate an opening welcome page for a wizard using a provided image.

    ``parent``
        A ``QWizard`` object to add the welcome page to.

    ``image``
        A splash image for the wizard.
    """
    parent.welcomePage = QtGui.QWizardPage()
    parent.welcomePage.setPixmap(QtGui.QWizard.WatermarkPixmap,
        QtGui.QPixmap(image))
    parent.welcomePage.setObjectName(u'WelcomePage')
    parent.welcomeLayout = QtGui.QVBoxLayout(parent.welcomePage)
    parent.welcomeLayout.setObjectName(u'WelcomeLayout')
    parent.titleLabel = QtGui.QLabel(parent.welcomePage)
    parent.titleLabel.setObjectName(u'TitleLabel')
    parent.welcomeLayout.addWidget(parent.titleLabel)
    parent.welcomeLayout.addSpacing(40)
    parent.informationLabel = QtGui.QLabel(parent.welcomePage)
    parent.informationLabel.setWordWrap(True)
    parent.informationLabel.setObjectName(u'InformationLabel')
    parent.welcomeLayout.addWidget(parent.informationLabel)
    parent.welcomeLayout.addStretch()
    parent.addPage(parent.welcomePage)


def create_button_box(dialog, name, standard_buttons, custom_buttons=[]):
    """
    Creates a QDialogButtonBox with the given buttons. The ``accepted()`` and
    ``rejected()`` signals of the button box are connected with the dialogs
    ``accept()`` and ``reject()`` slots.

    ``dialog``
        The parent object. This has to be a ``QDialog`` descendant.

    ``name``
        A string which is set as object name.

    ``standard_buttons``
        A list of strings for the used buttons. It might contain: ``ok``,
        ``save``, ``cancel``, ``close``, and ``defaults``.

    ``custom_buttons``
        A list of additional buttons. If a item is a instance of
        QtGui.QAbstractButton it is added with QDialogButtonBox.ActionRole.
        Otherwhise the item has to be a tuple of a button and a ButtonRole.
    """
    buttons = QtGui.QDialogButtonBox.NoButton
    if u'ok' in standard_buttons:
        buttons |= QtGui.QDialogButtonBox.Ok
    if u'save' in standard_buttons:
        buttons |= QtGui.QDialogButtonBox.Save
    if u'cancel' in standard_buttons:
        buttons |= QtGui.QDialogButtonBox.Cancel
    if u'close' in standard_buttons:
        buttons |= QtGui.QDialogButtonBox.Close
    if u'defaults' in standard_buttons:
        buttons |= QtGui.QDialogButtonBox.RestoreDefaults
    button_box = QtGui.QDialogButtonBox(dialog)
    button_box.setObjectName(name)
    button_box.setStandardButtons(buttons)
    for button in custom_buttons:
        if isinstance(button, QtGui.QAbstractButton):
            button_box.addButton(button, QtGui.QDialogButtonBox.ActionRole)
        else:
            button_box.addButton(*button)
    QtCore.QObject.connect(button_box, QtCore.SIGNAL(u'accepted()'),
        dialog.accept)
    QtCore.QObject.connect(button_box, QtCore.SIGNAL(u'rejected()'),
        dialog.reject)
    return button_box


def critical_error_message_box(title=None, message=None, parent=None,
    question=False):
    """
    Provides a standard critical message box for errors that OpenLP displays
    to users.

    ``title``
        The title for the message box.

    ``message``
        The message to display to the user.

    ``parent``
        The parent UI element to attach the dialog to.

    ``question``
        Should this message box question the user.
    """
    if question:
        return QtGui.QMessageBox.critical(parent, UiStrings().Error, message,
            QtGui.QMessageBox.StandardButtons(
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No))
    data = {u'message': message}
    data[u'title'] = title if title else UiStrings().Error
    return Receiver.send_message(u'openlp_error_message', data)


def create_horizontal_adjusting_combo_box(parent, name):
    """
    Creates a QComboBox with adapting width for media items.

    ``parent``
        The parent widget.

    ``name``
        A string set as object name for the combo box.
    """
    combo = QtGui.QComboBox(parent)
    combo.setObjectName(name)
    combo.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
    combo.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
    return combo


def create_button(parent, name, **kwargs):
    """
    Return an button with the object name set and the given parameters.

    ``parent``
        A QtCore.QWidget for the buttons parent (required).

    ``name``
        A string which is set as object name (required).

    ``role``
        A string which can have one value out of ``delete``, ``up``, and
        ``down``. This decides about default values for properties like text,
        icon, or tooltip.

    ``text``
        A string for the action text.

    ``icon``
        Either a QIcon, a resource string, or a file location string for the
        action icon.

    ``tooltip``
        A string for the action tool tip.

    ``enabled``
        False in case the button should be disabled.
    """
    if u'role' in kwargs:
        role = kwargs.pop(u'role')
        if role == u'delete':
            kwargs.setdefault(u'text', UiStrings().Delete)
            kwargs.setdefault(u'tooltip',
                translate('OpenLP.Ui', 'Delete the selected item.'))
        elif role == u'up':
            kwargs.setdefault(u'icon', u':/services/service_up.png')
            kwargs.setdefault(u'tooltip',
                translate('OpenLP.Ui', 'Move selection up one position.'))
        elif role == u'down':
            kwargs.setdefault(u'icon', u':/services/service_down.png')
            kwargs.setdefault(u'tooltip',
                translate('OpenLP.Ui', 'Move selection down one position.'))
        else:
            log.warn(u'The role "%s" is not defined in create_push_button().',
                role)
    if kwargs.pop(u'class', u'') == u'toolbutton':
        button = QtGui.QToolButton(parent)
    else:
        button = QtGui.QPushButton(parent)
    button.setObjectName(name)
    if kwargs.get(u'text'):
        button.setText(kwargs.pop(u'text'))
    if kwargs.get(u'icon'):
        button.setIcon(build_icon(kwargs.pop(u'icon')))
    if kwargs.get(u'tooltip'):
        button.setToolTip(kwargs.pop(u'tooltip'))
    if not kwargs.pop(u'enabled', True):
        button.setEnabled(False)
    if kwargs.get(u'click'):
        QtCore.QObject.connect(button, QtCore.SIGNAL(u'clicked()'),
            kwargs.pop(u'click'))
    for key in kwargs.keys():
        if key not in [u'text', u'icon', u'tooltip', u'click']:
            log.warn(u'Parameter %s was not consumed in create_button().', key)
    return button


def create_action(parent, name, **kwargs):
    """
    Return an action with the object name set and the given parameters.

    ``parent``
        A QtCore.QObject for the actions parent (required).

    ``name``
        A string which is set as object name (required).

    ``text``
        A string for the action text.

    ``icon``
        Either a QIcon, a resource string, or a file location string for the
        action icon.

    ``tooltip``
        A string for the action tool tip.

    ``statustip``
        A string for the action status tip.

    ``checked``
        A bool for the state. If ``None`` the Action is not checkable.

    ``enabled``
        False in case the action should be disabled.

    ``visible``
        False in case the action should be hidden.

    ``separator``
        True in case the action will be considered a separator.

    #FIXME: check
    ``data``
        Data which is set as QVariant type.

    ``shortcuts``
        A QList<QKeySequence> (or a list of strings) which are set as shortcuts.

    ``context``
        A context for the shortcut execution.

    ``category``
        A category the action should be listed in the shortcut dialog.

    ``triggers``
        A slot which is connected to the actions ``triggered()`` slot.
    """
    action = QtGui.QAction(parent)
    action.setObjectName(name)
    if kwargs.get(u'text'):
        action.setText(kwargs.pop(u'text'))
    if kwargs.get(u'icon'):
        action.setIcon(build_icon(kwargs.pop(u'icon')))
    if kwargs.get(u'tooltip'):
        action.setToolTip(kwargs.pop(u'tooltip'))
    if kwargs.get(u'statustip'):
        action.setStatusTip(kwargs.pop(u'statustip'))
    if kwargs.get(u'checked') is not None:
        action.setCheckable(True)
        action.setChecked(kwargs.pop(u'checked'))
    if not kwargs.pop(u'enabled', True):
        action.setEnabled(False)
    if not kwargs.pop(u'visible', True):
        action.setVisible(False)
    if kwargs.pop(u'separator', False):
        action.setSeparator(True)
    if u'data' in kwargs:
        action.setData(kwargs.pop(u'data'))
    if kwargs.get(u'shortcuts'):
        action.setShortcuts(kwargs.pop(u'shortcuts'))
    if u'context' in kwargs:
        action.setShortcutContext(kwargs.pop(u'context'))
    if kwargs.get(u'category'):
        action_list = ActionList.get_instance()
        action_list.add_action(action, unicode(kwargs.pop(u'category')))
    if kwargs.get(u'triggers'):
        QtCore.QObject.connect(action, QtCore.SIGNAL(u'triggered(bool)'),
            kwargs.pop(u'triggers'))
    for key in kwargs.keys():
        if key not in [u'text', u'icon', u'tooltip', u'statustip', u'checked',
            u'shortcuts', u'category', u'triggers']:
            log.warn(u'Parameter %s was not consumed in create_action().', key)
    return action


def create_widget_action(parent, name=u'', **kwargs):
    """
    Return a new QAction by calling ``create_action(parent, name, **kwargs)``.
    The shortcut context defaults to ``QtCore.Qt.WidgetShortcut`` and the action
    is added to the parents action list.
    """
    kwargs.setdefault(u'context', QtCore.Qt.WidgetShortcut)
    action = create_action(parent, name, **kwargs)
    parent.addAction(action)
    return action


def set_case_insensitive_completer(cache, widget):
    """
    Sets a case insensitive text completer for a widget.

    ``cache``
        The list of items to use as suggestions.

    ``widget``
        A widget to set the completer (QComboBox or QTextEdit instance)
    """
    completer = QtGui.QCompleter(cache)
    completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
    widget.setCompleter(completer)


def create_valign_selection_widgets(parent):
    """
    Creates a standard label and combo box for asking users to select a
    vertical alignment.

    ``parent``
        The parent object. This should be a ``QWidget`` descendant.

    Returns a tuple of QLabel and QComboBox.
    """
    label = QtGui.QLabel(parent)
    label.setText(translate('OpenLP.Ui', '&Vertical Align:'))
    combo_box = QtGui.QComboBox(parent)
    combo_box.addItem(UiStrings().Top)
    combo_box.addItem(UiStrings().Middle)
    combo_box.addItem(UiStrings().Bottom)
    label.setBuddy(combo_box)
    return label, combo_box


def find_and_set_in_combo_box(combo_box, value_to_find):
    """
    Find a string in a combo box and set it as the selected item if present

    ``combo_box``
        The combo box to check for selected items

    ``value_to_find``
        The value to find
    """
    index = combo_box.findText(value_to_find,
        QtCore.Qt.MatchExactly)
    if index == -1:
        # Not Found.
        index = 0
    combo_box.setCurrentIndex(index)
