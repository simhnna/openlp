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
"""
Package to test the openlp.core.threading package.
"""
from unittest.mock import MagicMock, call, patch

from openlp.core.version import run_thread


def test_run_thread_no_name():
    """
    Test that trying to run a thread without a name results in an exception being thrown
    """
    # GIVEN: A fake worker
    # WHEN: run_thread() is called without a name
    try:
        run_thread(MagicMock(), '')
        assert False, 'A ValueError should have been thrown to prevent blank names'
    except ValueError:
        # THEN: A ValueError should have been thrown
        assert True, 'A ValueError was correctly thrown'


@patch('openlp.core.threading.Registry')
def test_run_thread_exists(MockRegistry):
    """
    Test that trying to run a thread with a name that already exists will throw a KeyError
    """
    # GIVEN: A mocked registry with a main window object
    mocked_main_window = MagicMock()
    mocked_main_window.threads = {'test_thread': MagicMock()}
    MockRegistry.return_value.get.return_value = mocked_main_window

    # WHEN: run_thread() is called
    try:
        run_thread(MagicMock(), 'test_thread')
        assert False, 'A KeyError should have been thrown to show that a thread with this name already exists'
    except KeyError:
        assert True, 'A KeyError was correctly thrown'


@patch('openlp.core.threading.QtCore.QThread')
@patch('openlp.core.threading.Registry')
def test_run_thread(MockRegistry, MockQThread):
    """
    Test that running a thread works correctly
    """
    # GIVEN: A mocked registry with a main window object
    mocked_main_window = MagicMock()
    mocked_main_window.threads = {}
    MockRegistry.return_value.get.return_value = mocked_main_window

    # WHEN: run_thread() is called
    run_thread(MagicMock(), 'test_thread')

    # THEN: The thread should be in the threads list and the correct methods should have been called
    assert len(mocked_main_window.threads.keys()) == 1, 'There should be 1 item in the list of threads'
    assert list(mocked_main_window.threads.keys()) == ['test_thread'], 'The test_thread item should be in the list'
    mocked_worker = mocked_main_window.threads['test_thread']['worker']
    mocked_thread = mocked_main_window.threads['test_thread']['thread']
    mocked_worker.moveToThread.assert_called_once_with(mocked_thread)
    mocked_thread.started.connect.assert_called_once_with(mocked_worker.start)
    expected_quit_calls = [call(mocked_thread.quit), call(mocked_worker.deleteLater)]
    assert mocked_worker.quit.connect.call_args_list == expected_quit_calls, \
        'The workers quit signal should be connected twice'
    assert mocked_thread.finished.connect.call_args_list[0] == call(mocked_thread.deleteLater), \
        'The threads finished signal should be connected to its deleteLater slot'
    assert mocked_thread.finished.connect.call_count == 2, 'The signal should have been connected twice'
    mocked_thread.start.assert_called_once_with()
