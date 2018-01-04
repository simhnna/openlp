# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2015 OpenLP Developers                                   #
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
Package to test the openlp.core.projectors.pjlink command routing.
"""

from unittest import TestCase
from unittest.mock import MagicMock, call, patch

import openlp.core.projectors.pjlink
from openlp.core.projectors.constants import PJLINK_ERRORS, PJLINK_PREFIX, STATUS_MSG, \
    E_AUTHENTICATION, E_PARAMETER, E_PROJECTOR, E_UNAVAILABLE, E_UNDEFINED
from openlp.core.projectors.db import Projector
from openlp.core.projectors.pjlink import PJLink

from tests.resources.projector.data import TEST1_DATA


class TestPJLinkRouting(TestCase):
    """
    Tests for the PJLink module command routing
    """
    def test_get_data_unknown_command(self):
        """
        Test not a valid command
        """
        # GIVEN: Test object
        log_warning_text = [call('(111.111.111.111) get_data(): Invalid packet - unknown command "UNK"')]
        log_debug_text = [call('(111.111.111.111) get_data(ip="111.111.111.111" buffer="b\'%1UNK=Huh?\'"'),
                          call('(111.111.111.111) get_data(): Checking new data "%1UNK=Huh?"')]

        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, '_trash_buffer') as mock_buffer:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.pjlink_functions = MagicMock()

            # WHEN: get_data called with an unknown command
            pjlink.get_data(buff='{prefix}1UNK=Huh?'.format(prefix=PJLINK_PREFIX).encode('utf-8'))

            # THEN: Appropriate log entries should have been made and methods called/not called
            mock_log.debug.assert_has_calls(log_debug_text)
            mock_log.warning.assert_has_calls(log_warning_text)
            assert pjlink.pjlink_functions.called is False, 'Should not have accessed pjlink_functions'
            assert mock_buffer.called is True, 'Should have called _trash_buffer'

    def test_process_command_call_clss(self):
        """
        Test process_command calls proper function
        """
        # GIVEN: Test object and mocks
        log_debug_calls = [call('(111.111.111.111) Processing command "CLSS" with data "1"'),
                           call('(111.111.111.111) Calling function for CLSS')]

        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'process_clss') as mock_process_clss:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

            # WHEN: process_command is called with valid function and data
            pjlink.process_command(cmd='CLSS', data='1')

            # THEN: Appropriate log entries should have been made and methods called
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_process_clss.assert_called_once_with(data='1')

    def test_process_command_erra(self):
        """
        Test ERRA - Authentication Error
        """
        # GIVEN: Test object
        log_error_calls = [call('(111.111.111.111) PJLINK: {msg}'.format(msg=STATUS_MSG[E_AUTHENTICATION]))]
        log_debug_calls = [call('(111.111.111.111) Processing command "PJLINK" with data "ERRA"')]

        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'process_pjlink') as mock_process_pjlink, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'change_status') as mock_change_status, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'disconnect_from_host') as mock_disconnect, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorAuthentication') as mock_authentication:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

            # WHEN: process_command called with ERRA
            pjlink.process_command(cmd='PJLINK', data=PJLINK_ERRORS[E_AUTHENTICATION])

            # THEN: Appropriate log entries should have been made and methods called/not called
            assert mock_disconnect.called is True, 'disconnect_from_host should have been called'
            mock_log.error.assert_has_calls(log_error_calls)
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_change_status.assert_called_once_with(status=E_AUTHENTICATION)
            mock_authentication.emit.assert_called_once_with(pjlink.name)
            mock_process_pjlink.assert_not_called()

    def test_process_command_err1(self):
        """
        Test ERR1 - Undefined projector function
        """
        # GIVEN: Test object
        log_error_text = [call('(111.111.111.111) CLSS: {msg}'.format(msg=STATUS_MSG[E_UNDEFINED]))]
        log_debug_text = [call('(111.111.111.111) Processing command "CLSS" with data "ERR1"'),
                          call('(111.111.111.111) Calling function for CLSS')]

        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'process_clss') as mock_process_clss:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

            # WHEN: process_command called with ERR1
            pjlink.process_command(cmd='CLSS', data=PJLINK_ERRORS[E_UNDEFINED])

            # THEN: Appropriate log entries should have been made and methods called
            mock_log.error.assert_has_calls(log_error_text)
            mock_log.debug.assert_has_calls(log_debug_text)
            mock_process_clss.assert_called_once_with(data=PJLINK_ERRORS[E_UNDEFINED])

    def test_process_command_err2(self):
        """
        Test ERR2 - Parameter Error
        """
        # GIVEN: Test object
        log_error_text = [call('(111.111.111.111) CLSS: {msg}'.format(msg=STATUS_MSG[E_PARAMETER]))]
        log_debug_text = [call('(111.111.111.111) Processing command "CLSS" with data "ERR2"'),
                          call('(111.111.111.111) Calling function for CLSS')]

        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'process_clss') as mock_process_clss:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

            # WHEN: process_command called with ERR2
            pjlink.process_command(cmd='CLSS', data=PJLINK_ERRORS[E_PARAMETER])

            # THEN: Appropriate log entries should have been made and methods called/not called
            mock_log.error.assert_has_calls(log_error_text)
            mock_log.debug.assert_has_calls(log_debug_text)
            mock_process_clss.assert_called_once_with(data=PJLINK_ERRORS[E_PARAMETER])

    def test_process_command_err3(self):
        """
        Test ERR3 - Unavailable error
        """
        # GIVEN: Test object
        log_error_text = [call('(111.111.111.111) CLSS: {msg}'.format(msg=STATUS_MSG[E_UNAVAILABLE]))]
        log_debug_text = [call('(111.111.111.111) Processing command "CLSS" with data "ERR3"'),
                          call('(111.111.111.111) Calling function for CLSS')]

        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'process_clss') as mock_process_clss:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

            # WHEN: process_command called with ERR3
            pjlink.process_command(cmd='CLSS', data=PJLINK_ERRORS[E_UNAVAILABLE])

            # THEN: Appropriate log entries should have been made and methods called
            mock_log.error.assert_has_calls(log_error_text)
            mock_log.debug.assert_has_calls(log_debug_text)
            mock_process_clss.assert_called_once_with(data=PJLINK_ERRORS[E_UNAVAILABLE])

    def test_process_command_err4(self):
        """
        Test ERR3 - Unavailable error
        """
        # GIVEN: Test object
        log_error_text = [call('(111.111.111.111) CLSS: {msg}'.format(msg=STATUS_MSG[E_PROJECTOR]))]
        log_debug_text = [call('(111.111.111.111) Processing command "CLSS" with data "ERR4"'),
                          call('(111.111.111.111) Calling function for CLSS')]

        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'process_clss') as mock_process_clss:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

            # WHEN: process_command called with ERR4
            pjlink.process_command(cmd='CLSS', data=PJLINK_ERRORS[E_PROJECTOR])

            # THEN: Appropriate log entries should have been made and methods called
            mock_log.error.assert_has_calls(log_error_text)
            mock_log.debug.assert_has_calls(log_debug_text)
            mock_process_clss.assert_called_once_with(data=PJLINK_ERRORS[E_PROJECTOR])

    def test_process_command_future(self):
        """
        Test command valid but no method to process yet
        """
        # GIVEN: Test object
        log_warning_text = [call('(111.111.111.111) Unable to process command="CLSS" (Future option?)')]
        log_debug_text = [call('(111.111.111.111) Processing command "CLSS" with data "Huh?"')]

        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'process_clss') as mock_process_clss:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.pjlink_functions = MagicMock()

            # WHEN: Processing a possible future command
            pjlink.process_command(cmd='CLSS', data="Huh?")

            # THEN: Appropriate log entries should have been made and methods called/not called
            mock_log.debug.assert_has_calls(log_debug_text)
            mock_log.warning.assert_has_calls(log_warning_text)
            assert pjlink.pjlink_functions.called is False, 'Should not have accessed pjlink_functions'
            assert mock_process_clss.called is False, 'Should not have called process_clss'

    def test_process_command_ok(self):
        """
        Test command returned success
        """
        # GIVEN: Initial mocks and data
        # GIVEN: Test object and mocks
        log_debug_calls = [call('(111.111.111.111) Processing command "CLSS" with data "OK"'),
                           call('(111.111.111.111) Command "CLSS" returned OK')]

        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'process_clss') as mock_process_clss:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

            # WHEN: process_command is called with valid function and data
            pjlink.process_command(cmd='CLSS', data='OK')

            # THEN: Appropriate log entries should have been made and methods called
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_send_command.assert_called_once_with(cmd='CLSS')
            mock_process_clss.assert_not_called()
