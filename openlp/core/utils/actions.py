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
The :mod:`~openlp.core.utils.actions` module provides action list classes used
by the shortcuts system.
"""
from PyQt4 import QtCore, QtGui

class ActionCategory(object):
    """
    The :class:`~openlp.core.utils.ActionCategory` class encapsulates a
    category for the :class:`~openlp.core.utils.CategoryList` class.
    """
    def __init__(self, name, weight=0):
        self.name = name
        self.weight = weight
        self.actions = CategoryActionList()


class CategoryActionList(object):
    """
    The :class:`~openlp.core.utils.CategoryActionList` class provides a sorted
    list of actions within a category.
    """
    def __init__(self):
        self.index = 0
        self.actions = []

    def __getitem__(self, key):
        for weight, action in self.actions:
            if action.text() == key:
                return action
        raise KeyError(u'Action "%s" does not exist.' % key)

    def __contains__(self, item):
        return self.has_key(item)

    def __len__(self):
        return len(self.actions)

    def __iter__(self):
        return self

    def __next__(self):
        """
        Python 3 "next" method.
        """
        if self.index >= len(self.actions):
            self.index = 0
            raise StopIteration
        else:
            self.index += 1
            return self.actions[self.index - 1][1]

    def next(self):
        """
        Python 2 "next" method.
        """
        return self.__next__()

    def has_key(self, key):
        for weight, action in self.actions:
            if action.text() == key:
                return True
        return False

    def append(self, name):
        weight = 0
        if len(self.actions) > 0:
            weight = self.actions[-1][0] + 1
        self.add(name, weight)

    def add(self, action, weight=0):
        self.actions.append((weight, action))
        self.actions.sort(key=lambda act: act[0])

    def remove(self, remove_action):
        for action in self.actions:
            if action[1] == remove_action:
                self.actions.remove(action)
                return


class CategoryList(object):
    """
    The :class:`~openlp.core.utils.CategoryList` class encapsulates a category
    list for the :class:`~openlp.core.utils.ActionList` class and provides an
    iterator interface for walking through the list of actions in this category.
    """

    def __init__(self):
        self.index = 0
        self.categories = []

    def __getitem__(self, key):
        for category in self.categories:
            if category.name == key:
                return category
        raise KeyError(u'Category "%s" does not exist.' % key)

    def __contains__(self, item):
        return self.has_key(item)

    def __len__(self):
        return len(self.categories)

    def __iter__(self):
        return self

    def __next__(self):
        """
        Python 3 "next" method for iterator.
        """
        if self.index >= len(self.categories):
            self.index = 0
            raise StopIteration
        else:
            self.index += 1
            return self.categories[self.index - 1]

    def next(self):
        """
        Python 2 "next" method for iterator.
        """
        return self.__next__()

    def has_key(self, key):
        for category in self.categories:
            if category.name == key:
                return True
        return False

    def append(self, name, actions=None):
        weight = 0
        if len(self.categories) > 0:
            weight = self.categories[-1].weight + 1
        if actions:
            self.add(name, weight, actions)
        else:
            self.add(name, weight)

    def add(self, name, weight=0, actions=None):
        category = ActionCategory(name, weight)
        if actions:
            for action in actions:
                if isinstance(action, tuple):
                    category.actions.add(action[0], action[1])
                else:
                    category.actions.append(action)
        self.categories.append(category)
        self.categories.sort(key=lambda cat: cat.weight)

    def remove(self, name):
        for category in self.categories:
            if category.name == name:
                self.categories.remove(category)


class ActionList(object):
    """
    The :class:`~openlp.core.utils.ActionList` class contains a list of menu
    actions and categories associated with those actions. Each category also
    has a weight by which it is sorted when iterating through the list of
    actions or categories.
    """
    instance = None
    shortcut_map = {}

    def __init__(self):
        self.categories = CategoryList()

    @staticmethod
    def get_instance():
        if ActionList.instance is None:
            ActionList.instance = ActionList()
        return ActionList.instance

    def add_action(self, action, category=None, weight=None):
        """
        Add an action to the list of actions.

        ``action``
            The action to add (QAction). **Note**, the action must not have an
            empty ``objectName``.

        ``category``
            The category this action belongs to. The category can be a QString
            or python unicode string. **Note**, if the category is ``None``, the
            category and its actions are being hidden in the shortcut dialog.
            However, if they are added, it is possible to avoid assigning
            shortcuts twice, which is important.

        ``weight``
            The weight specifies how important a category is. However, this only
            has an impact on the order the categories are displayed.
        """
        if category not in self.categories:
            self.categories.append(category)
        action.defaultShortcuts = action.shortcuts()
        if weight is None:
            self.categories[category].actions.append(action)
        else:
            self.categories[category].actions.add(action, weight)
        # Load the shortcut from the config.
        settings = QtCore.QSettings()
        settings.beginGroup(u'shortcuts')
        shortcuts = settings.value(action.objectName(),
            QtCore.QVariant(action.shortcuts())).toStringList()
        settings.endGroup()
        if not shortcuts:
            action.setShortcuts([])
            return
        # We have to do this to ensure that the loaded shortcut list e. g.
        # STRG+O (German) is converted to CTRL+O, which is only done when we
        # convert the strings in this way (QKeySequence -> QString -> unicode).
        shortcuts = map(QtGui.QKeySequence, shortcuts)
        shortcuts = map(unicode, map(QtGui.QKeySequence.toString, shortcuts))
        # Check the alternate shortcut first, to avoid problems when the
        # alternate shortcut becomes the primary shortcut after removing the
        # (initial) primary shortcut due to conflicts.
        if len(shortcuts) == 2:
            existing_actions = ActionList.shortcut_map.get(shortcuts[1], [])
            # Check for conflicts with other actions considering the shortcut
            # context.
            if self._is_shortcut_available(existing_actions, action):
                actions = ActionList.shortcut_map.get(shortcuts[1], [])
                actions.append(action)
                ActionList.shortcut_map[shortcuts[1]] = actions
            else:
                shortcuts.remove(shortcuts[1])
        # Check the primary shortcut.
        existing_actions = ActionList.shortcut_map.get(shortcuts[0], [])
        # Check for conflicts with other actions considering the shortcut
        # context.
        if self._is_shortcut_available(existing_actions, action):
            actions = ActionList.shortcut_map.get(shortcuts[0], [])
            actions.append(action)
            ActionList.shortcut_map[shortcuts[0]] = actions
        else:
            shortcuts.remove(shortcuts[0])
        action.setShortcuts(
            [QtGui.QKeySequence(shortcut) for shortcut in shortcuts])

    def remove_action(self, action, category=None):
        """
        This removes an action from its category. Empty categories are
        automatically removed.

        ``action``
            The ``QAction`` object to be removed.

        ``category``
            The name (unicode string) of the category, which contains the
            action. Defaults to None.
        """
        if category not in self.categories:
            return
        self.categories[category].actions.remove(action)
        # Remove empty categories.
        if not self.categories[category].actions:
            self.categories.remove(category)
        shortcuts = map(unicode,
            map(QtGui.QKeySequence.toString, action.shortcuts()))
        for shortcut in shortcuts:
            # Remove action from the list of actions which are using this
            # shortcut.
            ActionList.shortcut_map[shortcut].remove(action)
            # Remove empty entries.
            if not ActionList.shortcut_map[shortcut]:
                del ActionList.shortcut_map[shortcut]

    def add_category(self, name, weight):
        """
        Add an empty category to the list of categories. This is ony convenient
        for categories with a given weight.

        ``name``
            The category's name.

        ``weight``
            The category's weight (int).
        """
        if name in self.categories:
            # Only change the weight and resort the categories again.
            for category in self.categories:
                if category.name == name:
                    category.weight = weight
            self.categories.categories.sort(key=lambda cat: cat.weight)
            return
        self.categories.add(name, weight)

    def update_shortcut_map(self, action, old_shortcuts):
        """
        Remove the action for the given ``old_shortcuts`` from the
        ``shortcut_map`` to ensure its up-to-dateness.

        **Note**: The new action's shortcuts **must** be assigned to the given
        ``action`` **before** calling this method.

        ``action``
            The action whose shortcuts are supposed to be updated in the
            ``shortcut_map``.

        ``old_shortcuts``
            A list of unicode keysequences.
        """
        for old_shortcut in old_shortcuts:
            # Remove action from the list of actions which are using this
            # shortcut.
            ActionList.shortcut_map[old_shortcut].remove(action)
            # Remove empty entries.
            if not ActionList.shortcut_map[old_shortcut]:
                del ActionList.shortcut_map[old_shortcut]
        new_shortcuts = map(unicode,
            map(QtGui.QKeySequence.toString, action.shortcuts()))
        # Add the new shortcuts to the map.
        for new_shortcut in new_shortcuts:
            existing_actions = ActionList.shortcut_map.get(new_shortcut, [])
            existing_actions.append(action)
            ActionList.shortcut_map[new_shortcut] = existing_actions

    def _is_shortcut_available(self, existing_actions, action):
        """
        Checks if the given ``action`` may use its assigned shortcut(s) or not.
        Returns ``True`` or ``False.

        ``existing_actions``
            A list of actions which already use a particular shortcut.

        ``action``
            The action which wants to use a particular shortcut.
        """
        local = action.shortcutContext() in \
            [QtCore.Qt.WindowShortcut, QtCore.Qt.ApplicationShortcut]
        affected_actions = filter(lambda a: isinstance(a, QtGui.QAction),
            self.getAllChildObjects(action.parent())) if local else []
        for existing_action in existing_actions:
            if action is existing_action:
                continue
            if not local or existing_action in affected_actions:
                return False
            if existing_action.shortcutContext() \
                in [QtCore.Qt.WindowShortcut, QtCore.Qt.ApplicationShortcut]:
                return False
            elif action in self.getAllChildObjects(existing_action.parent()):
                return False
        return True
    
    def getAllChildObjects(self, qobject):
        """
        Goes recursively through the children of ``qobject`` and returns a list
        of all child objects.
        """
        children = [child for child in qobject.children()]
        for child in qobject.children():
            children.append(self.getAllChildObjects(child))
        return children


class CategoryOrder(object):
    """
    An enumeration class for category weights.
    """
    standardMenu = -20
    standardToolbar = -10
