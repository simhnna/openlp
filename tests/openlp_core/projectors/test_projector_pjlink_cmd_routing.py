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
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_get_data_unknown_command(self, mock_log):
        """
        Test not a valid command
        """
        # GIVEN: Test object
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.pjlink_functions = MagicMock()
        log_warning_text = [call('({ip}) get_data(): Invalid packet - '
                                 'unknown command "UNKN"'.format(ip=pjlink.name))]
        log_debug_text = [call('(___TEST_ONE___) get_data(ip="111.111.111.111" buffer="%1UNKN=Huh?"'),
                          call('(___TEST_ONE___) get_data(): Checking new data "%1UNKN=Huh?"'),
                          call('(___TEST_ONE___) get_data() header="%1UNKN" data="Huh?"'),
                          call('(___TEST_ONE___) get_data() version="1" cmd="UNKN"'),
                          call('(___TEST_ONE___) Cleaning buffer - msg = "get_data(): '
                               'Invalid packet - unknown command "UNKN""'),
                          call('(___TEST_ONE___) Finished cleaning buffer - 0 bytes dropped')]

        # WHEN: get_data called with an unknown command
        pjlink.get_data(buff='{prefix}1UNKN=Huh?'.format(prefix=PJLINK_PREFIX))

        # THEN: Appropriate log entries should have been made and methods called/not called
        mock_log.warning.assert_has_calls(log_warning_text)
        mock_log.debug.assert_has_calls(log_debug_text)
        assert pjlink.pjlink_functions.called is False, 'Should not have accessed pjlink_functions'

    def test_process_command_call_clss(self):
        """
        Test process_command calls proper function
        """
        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'process_clss') as mock_process_clss:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            log_debug_calls = [call('({ip}) Processing command "CLSS" with data "1"'.format(ip=pjlink.name)),
                               call('({ip}) Calling function for CLSS'.format(ip=pjlink.name))]

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
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'process_pjlink') as mock_process_pjlink, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'change_status') as mock_change_status, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'disconnect_from_host') as mock_disconnect, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorAuthentication') as mock_authentication:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            log_error_calls = [call('({ip}) PJLINK: {msg}'.format(ip=pjlink.name, msg=STATUS_MSG[E_AUTHENTICATION]))]
            log_debug_calls = [call('({ip}) Processing command "PJLINK" with data "ERRA"'.format(ip=pjlink.name))]

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
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'process_clss') as mock_process_clss:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            log_error_text = [call('({ip}) CLSS: {msg}'.format(ip=pjlink.name, msg=STATUS_MSG[E_UNDEFINED]))]
            log_debug_text = [call('({ip}) Processing command "CLSS" with data "ERR1"'.format(ip=pjlink.name)),
                              call('({ip}) Calling function for CLSS'.format(ip=pjlink.name))]

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
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'process_clss') as mock_process_clss:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            log_error_text = [call('({ip}) CLSS: {msg}'.format(ip=pjlink.name, msg=STATUS_MSG[E_PARAMETER]))]
            log_debug_text = [call('({ip}) Processing command "CLSS" with data "ERR2"'.format(ip=pjlink.name)),
                              call('({ip}) Calling function for CLSS'.format(ip=pjlink.name))]

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
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'process_clss') as mock_process_clss:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            log_error_text = [call('({ip}) CLSS: {msg}'.format(ip=pjlink.name, msg=STATUS_MSG[E_UNAVAILABLE]))]
            log_debug_text = [call('({ip}) Processing command "CLSS" with data "ERR3"'.format(ip=pjlink.name)),
                              call('({ip}) Calling function for CLSS'.format(ip=pjlink.name))]

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
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'process_clss') as mock_process_clss:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            log_error_text = [call('({ip}) CLSS: {msg}'.format(ip=pjlink.name, msg=STATUS_MSG[E_PROJECTOR]))]
            log_debug_text = [call('({ip}) Processing command "CLSS" with data "ERR4"'.format(ip=pjlink.name)),
                              call('({ip}) Calling function for CLSS'.format(ip=pjlink.name))]

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
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'process_clss') as mock_process_clss:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.pjlink_functions = MagicMock()
            log_warning_text = [call('({ip}) Unable to process command="CLSS" (Future option?)'.format(ip=pjlink.name))]
            log_debug_text = [call('({ip}) Processing command "CLSS" with data "Huh?"'.format(ip=pjlink.name))]

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
        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'process_clss') as mock_process_clss:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            log_debug_calls = [call('({ip}) Processing command "CLSS" with data "OK"'.format(ip=pjlink.name)),
                               call('({ip}) Command "CLSS" returned OK'.format(ip=pjlink.name))]

            # WHEN: process_command is called with valid function and data
            pjlink.process_command(cmd='CLSS', data='OK')

            # THEN: Appropriate log entries should have been made and methods called
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_send_command.assert_called_once_with(cmd='CLSS')
            mock_process_clss.assert_not_called()
