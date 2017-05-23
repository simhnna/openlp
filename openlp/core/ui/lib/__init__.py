# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2017 OpenLP Developers                                   #
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

from .colorbutton import ColorButton
from .listpreviewwidget import ListPreviewWidget
from .listwidgetwithdnd import ListWidgetWithDnD
from .mediadockmanager import MediaDockManager
from .dockwidget import OpenLPDockWidget
from .toolbar import OpenLPToolbar
from .wizard import OpenLPWizard, WizardStrings
from .pathedit import PathEdit, PathType
from .spelltextedit import SpellTextEdit
from .treewidgetwithdnd import TreeWidgetWithDnD

__all__ = ['ColorButton', 'ListPreviewWidget', 'ListWidgetWithDnD', 'MediaDockManager', 'OpenLPDockWidget',
           'OpenLPToolbar', 'OpenLPWizard', 'PathEdit', 'PathType', 'SpellTextEdit', 'TreeWidgetWithDnD',
           'WizardStrings']
