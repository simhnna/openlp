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
Package to test the openlp.core.projectors.pjlink base package.
"""
from unittest import TestCase
from unittest.mock import call, patch, MagicMock

import openlp.core.projectors.pjlink
from openlp.core.projectors.constants import \
    E_NOT_CONNECTED, E_PARAMETER, E_UNKNOWN_SOCKET_ERROR, STATUS_CODE, STATUS_MSG, \
    S_CONNECTED, S_CONNECTING, S_NOT_CONNECTED, S_OK, S_ON, \
    QSOCKET_STATE
from openlp.core.projectors.db import Projector
from openlp.core.projectors.pjlink import PJLink
from tests.resources.projector.data import TEST1_DATA


class TestPJLinkBase(TestCase):
    """
    Tests for the PJLink module
    """
    def test_status_change(self):
        """
        Test process_command call with ERR2 (Parameter) status
        """
        # GIVEN: Test object
        with patch('openlp.core.projectors.pjlink.PJLink.changeStatus') as mock_changeStatus:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

            # WHEN: process_command is called with "ERR2" status from projector
            pjlink.process_command('POWR', 'ERR2')

            # THEN: change_status should have called change_status with E_UNDEFINED
            #       as first parameter
            mock_changeStatus.called_with(E_PARAMETER,
                                          'change_status should have been called with "{}"'.format(
                                              STATUS_CODE[E_PARAMETER]))

    def test_socket_abort(self):
        """
        Test PJLink.socket_abort calls disconnect_from_host
        """
        # GIVEN: Test object
        with patch('openlp.core.projectors.pjlink.PJLink.disconnect_from_host') as mock_disconnect:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

            # WHEN: Calling socket_abort
            pjlink.socket_abort()

            # THEN: disconnect_from_host should be called
            assert mock_disconnect.called is True, 'Should have called disconnect_from_host'

    def test_poll_loop_not_connected(self):
        """
        Test PJLink.poll_loop not connected return
        """
        # GIVEN: Test object and mocks
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.state = MagicMock()
        pjlink.timer = MagicMock()
        pjlink.state.return_value = False
        pjlink.ConnectedState = True

        # WHEN: PJLink.poll_loop called
        pjlink.poll_loop()

        # THEN: poll_loop should exit without calling any other method
        assert pjlink.timer.called is False, 'Should have returned without calling any other method'

    def test_poll_loop_set_interval(self):
        """
        Test PJLink.poll_loop makes correct calls
        """
        # GIVEN: Mocks and test data
        with patch('openlp.core.projectors.pjlink.PJLink.send_command') as mock_send_command:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.state = MagicMock()
            pjlink.state.return_value = QSOCKET_STATE[S_CONNECTED]
            pjlink.poll_timer = MagicMock()
            pjlink.poll_timer.interval.return_value = 10

            pjlink.poll_time = 20
            pjlink.power = S_ON
            pjlink.source_available = None
            pjlink.other_info = None
            pjlink.manufacturer = None
            pjlink.model = None
            pjlink.pjlink_name = None
            call_list = [
                call('POWR'),
                call('ERST'),
                call('LAMP'),
                call('AVMT'),
                call('INPT'),
                call('INST'),
                call('INFO'),
                call('INF1'),
                call('INF2'),
                call('NAME'),
            ]

            # WHEN: PJLink.poll_loop is called
            pjlink.poll_loop()

            # THEN: proper calls were made to retrieve projector data
            # First, call to update the timer with the next interval
            assert pjlink.poll_timer.setInterval.called is True, 'Timer update interval should have been called'
            # Finally, should have called send_command with a list of projetctor status checks
            mock_send_command.assert_has_calls(call_list, 'Should have queued projector queries')

    def test_projector_change_status_unknown_socket_error(self):
        """
        Test change_status with connection error
        """
        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'changeStatus') as mock_changeStatus, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons') as mock_UpdateIcons:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.projector_status = 0
            pjlink.status_connect = 0
            log_debug_calls = [
                call('({ip}) Changing status to {status} "{msg}"'.format(ip=pjlink.name,
                                                                         status=STATUS_CODE[E_UNKNOWN_SOCKET_ERROR],
                                                                         msg=STATUS_MSG[E_UNKNOWN_SOCKET_ERROR])),
                call('({ip}) status_connect: {code}: "{msg}"'.format(ip=pjlink.name,
                                                                     code=STATUS_CODE[E_NOT_CONNECTED],
                                                                     msg=STATUS_MSG[E_NOT_CONNECTED])),
                call('({ip}) projector_status: {code}: "{msg}"'.format(ip=pjlink.name,
                                                                       code=STATUS_CODE[S_OK],
                                                                       msg=STATUS_MSG[S_OK])),
                call('({ip}) error_status: {code}: "{msg}"'.format(ip=pjlink.name,
                                                                   code=STATUS_CODE[E_UNKNOWN_SOCKET_ERROR],
                                                                   msg=STATUS_MSG[E_UNKNOWN_SOCKET_ERROR]))]

            # WHEN: change_status called with unknown socket error
            pjlink.change_status(status=E_UNKNOWN_SOCKET_ERROR)

            # THEN: Proper settings should change and signals sent
            mock_log.debug.assert_has_calls(log_debug_calls)
            assert pjlink.projector_status == S_OK, 'Projector status should not have changed'
            assert pjlink.status_connect == E_NOT_CONNECTED, 'Status connect should be NOT CONNECTED'
            assert mock_UpdateIcons.emit.called is True, 'Should have called UpdateIcons'
            mock_changeStatus.emit.assert_called_once_with(pjlink.ip, E_UNKNOWN_SOCKET_ERROR,
                                                           STATUS_MSG[E_UNKNOWN_SOCKET_ERROR])

    def test_projector_change_status_connection_status_connecting(self):
        """
        Test change_status with connecting status
        """
        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'changeStatus') as mock_changeStatus, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons') as mock_UpdateIcons:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.projector_status = 0
            pjlink.status_connect = 0
            log_debug_calls = [
                call('({ip}) Changing status to {status} "{msg}"'.format(ip=pjlink.name,
                                                                         status=STATUS_CODE[S_CONNECTING],
                                                                         msg=STATUS_MSG[S_CONNECTING])),
                call('({ip}) status_connect: {code}: "{msg}"'.format(ip=pjlink.name,
                                                                     code=STATUS_CODE[S_CONNECTING],
                                                                     msg=STATUS_MSG[S_CONNECTING])),
                call('({ip}) projector_status: {code}: "{msg}"'.format(ip=pjlink.name,
                                                                       code=STATUS_CODE[S_OK],
                                                                       msg=STATUS_MSG[S_OK])),
                call('({ip}) error_status: {code}: "{msg}"'.format(ip=pjlink.name,
                                                                   code=STATUS_CODE[S_OK],
                                                                   msg=STATUS_MSG[S_OK]))]

            # WHEN: change_status called with CONNECTING
            pjlink.change_status(status=S_CONNECTING)

            # THEN: Proper settings should change and signals sent
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_changeStatus.emit.assert_called_once_with(pjlink.ip, S_CONNECTING, STATUS_MSG[S_CONNECTING])
            assert pjlink.projector_status == S_OK, 'Projector status should not have changed'
            assert pjlink.status_connect == S_CONNECTING, 'Status connect should be CONNECTING'
            assert mock_UpdateIcons.emit.called is True, 'Should have called UpdateIcons'

    def test_projector_change_status_connection_status_connected(self):
        """
        Test change_status with connected status
        """
        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'changeStatus') as mock_changeStatus:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.projector_status = 0
            pjlink.status_connect = 0
            log_debug_calls = [
                call('({ip}) Changing status to {status} "{msg}"'.format(ip=pjlink.name,
                                                                         status=STATUS_CODE[S_CONNECTED],
                                                                         msg=STATUS_MSG[S_CONNECTED])),
                call('({ip}) status_connect: {code}: "{msg}"'.format(ip=pjlink.name,
                                                                     code=STATUS_CODE[S_CONNECTED],
                                                                     msg=STATUS_MSG[S_CONNECTED])),
                call('({ip}) projector_status: {code}: "{msg}"'.format(ip=pjlink.name,
                                                                       code=STATUS_CODE[S_OK],
                                                                       msg=STATUS_MSG[S_OK])),
                call('({ip}) error_status: {code}: "{msg}"'.format(ip=pjlink.name,
                                                                   code=STATUS_CODE[S_OK],
                                                                   msg=STATUS_MSG[S_OK]))]

            # WHEN: change_status called with CONNECTED
            pjlink.change_status(status=S_CONNECTED)

            # THEN: Proper settings should change and signals sent
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_changeStatus.emit.assert_called_once_with(pjlink.ip, S_CONNECTED, 'Connected')
            assert pjlink.projector_status == S_OK, 'Projector status should not have changed'
            assert pjlink.status_connect == S_CONNECTED, 'Status connect should be CONNECTED'

    def test_projector_change_status_connection_status_with_message(self):
        """
        Test change_status with connection status
        """
        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'changeStatus') as mock_changeStatus:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.projector_status = 0
            pjlink.status_connect = 0
            test_message = 'Different Status Message than default'
            log_debug_calls = [
                call('({ip}) Changing status to {status} "{msg}"'.format(ip=pjlink.name,
                                                                         status=STATUS_CODE[S_ON],
                                                                         msg=test_message)),
                call('({ip}) status_connect: {code}: "{msg}"'.format(ip=pjlink.name,
                                                                     code=STATUS_CODE[S_OK],
                                                                     msg=test_message)),
                call('({ip}) projector_status: {code}: "{msg}"'.format(ip=pjlink.name,
                                                                       code=STATUS_CODE[S_ON],
                                                                       msg=test_message)),
                call('({ip}) error_status: {code}: "{msg}"'.format(ip=pjlink.name,
                                                                   code=STATUS_CODE[S_OK],
                                                                   msg=test_message))]

            # WHEN: change_status called with projector ON status
            pjlink.change_status(status=S_ON, msg=test_message)

            # THEN: Proper settings should change and signals sent
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_changeStatus.emit.assert_called_once_with(pjlink.ip, S_ON, test_message)
            assert pjlink.projector_status == S_ON, 'Projector status should be ON'
            assert pjlink.status_connect == S_OK, 'Status connect should not have changed'

    def test_projector_get_av_mute_status(self):
        """
        Test sending command to retrieve shutter/audio state
        """
        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            test_data = 'AVMT'
            log_debug_calls = [call('({ip}) reset_information() connect status is '
                                    '{state}'.format(ip=pjlink.name, state=STATUS_CODE[S_NOT_CONNECTED])),
                               call('({ip}) Sending {cmd} command'.format(ip=pjlink.name, cmd=test_data))]

            # WHEN: get_av_mute_status is called
            pjlink.get_av_mute_status()

            # THEN: log data and send_command should have been called
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_send_command.assert_called_once_with(cmd=test_data)

    def test_projector_get_available_inputs(self):
        """
        Test sending command to retrieve avaliable inputs
        """
        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            test_data = 'INST'
            log_debug_calls = [call('({ip}) reset_information() connect status is '
                                    '{state}'.format(ip=pjlink.name, state=STATUS_CODE[S_NOT_CONNECTED])),
                               call('({ip}) Sending {cmd} command'.format(ip=pjlink.name, cmd=test_data))]

            # WHEN: get_available_inputs is called
            pjlink.get_available_inputs()

            # THEN: log data and send_command should have been called
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_send_command.assert_called_once_with(cmd=test_data)

    def test_projector_get_error_status(self):
        """
        Test sending command to retrieve projector error status
        """
        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            test_data = 'ERST'
            log_debug_calls = [call('({ip}) reset_information() connect status is '
                                    '{state}'.format(ip=pjlink.name, state=STATUS_CODE[S_NOT_CONNECTED])),
                               call('({ip}) Sending {cmd} command'.format(ip=pjlink.name, cmd=test_data))]

            # WHEN: get_error_status is called
            pjlink.get_error_status()

            # THEN: log data and send_command should have been called
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_send_command.assert_called_once_with(cmd=test_data)

    def test_projector_get_input_source(self):
        """
        Test sending command to retrieve current input
        """
        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            test_data = 'INPT'
            log_debug_calls = [call('({ip}) reset_information() connect status is '
                                    '{state}'.format(ip=pjlink.name, state=STATUS_CODE[S_NOT_CONNECTED])),
                               call('({ip}) Sending {cmd} command'.format(ip=pjlink.name, cmd=test_data))]

            # WHEN: get_input_source is called
            pjlink.get_input_source()

            # THEN: log data and send_command should have been called
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_send_command.assert_called_once_with(cmd=test_data)

    def test_projector_get_lamp_status(self):
        """
        Test sending command to retrieve lamp(s) status
        """
        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            test_data = 'LAMP'
            log_debug_calls = [call('({ip}) reset_information() connect status is '
                                    '{state}'.format(ip=pjlink.name, state=STATUS_CODE[S_NOT_CONNECTED])),
                               call('({ip}) Sending {cmd} command'.format(ip=pjlink.name, cmd=test_data))]

            # WHEN: get_input_source is called
            pjlink.get_lamp_status()

            # THEN: log data and send_command should have been called
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_send_command.assert_called_once_with(cmd=test_data)

    def test_projector_get_manufacturer(self):
        """
        Test sending command to retrieve manufacturer name
        """
        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            test_data = 'INF1'
            log_debug_calls = [call('({ip}) reset_information() connect status is '
                                    '{state}'.format(ip=pjlink.name, state=STATUS_CODE[S_NOT_CONNECTED])),
                               call('({ip}) Sending {cmd} command'.format(ip=pjlink.name, cmd=test_data))]

            # WHEN: get_input_source is called
            pjlink.get_manufacturer()

            # THEN: log data and send_command should have been called
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_send_command.assert_called_once_with(cmd=test_data)

    def test_projector_get_model(self):
        """
        Test sending command to get model information
        """
        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            test_data = 'INF2'
            log_debug_calls = [call('({ip}) reset_information() connect status is '
                                    '{state}'.format(ip=pjlink.name, state=STATUS_CODE[S_NOT_CONNECTED])),
                               call('({ip}) Sending {cmd} command'.format(ip=pjlink.name, cmd=test_data))]

            # WHEN: get_input_source is called
            pjlink.get_model()

            # THEN: log data and send_command should have been called
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_send_command.assert_called_once_with(cmd=test_data)

    def test_projector_get_name(self):
        """
        Test sending command to get user-assigned name
        """
        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            test_data = 'NAME'
            log_debug_calls = [call('({ip}) reset_information() connect status is '
                                    '{state}'.format(ip=pjlink.name, state=STATUS_CODE[S_NOT_CONNECTED])),
                               call('({ip}) Sending {cmd} command'.format(ip=pjlink.name, cmd=test_data))]

            # WHEN: get_input_source is called
            pjlink.get_name()

            # THEN: log data and send_command should have been called
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_send_command.assert_called_once_with(cmd=test_data)

    def test_projector_get_other_info(self):
        """
        Test sending command to retrieve other information
        """
        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            test_data = 'INFO'
            log_debug_calls = [call('({ip}) reset_information() connect status is '
                                    '{state}'.format(ip=pjlink.name, state=STATUS_CODE[S_NOT_CONNECTED])),
                               call('({ip}) Sending {cmd} command'.format(ip=pjlink.name, cmd=test_data))]

            # WHEN: get_input_source is called
            pjlink.get_other_info()

            # THEN: log data and send_command should have been called
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_send_command.assert_called_once_with(cmd=test_data)

    def test_projector_get_power_status(self):
        """
        Test sending command to retrieve current power state
        """
        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            test_data = 'POWR'
            log_debug_calls = [call('({ip}) reset_information() connect status is '
                                    '{state}'.format(ip=pjlink.name, state=STATUS_CODE[S_NOT_CONNECTED])),
                               call('({ip}) Sending {cmd} command'.format(ip=pjlink.name, cmd=test_data))]

            # WHEN: get_input_source is called
            pjlink.get_power_status()

            # THEN: log data and send_command should have been called
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_send_command.assert_called_once_with(cmd=test_data)

    def test_projector_get_status_invalid(self):
        """
        Test to check returned information for error code
        """
        # GIVEN: Test object
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        test_string = 'NaN test'

        # WHEN: get_status called
        code, message = pjlink._get_status(status=test_string)

        # THEN: Proper data should have been returned
        assert code == -1, 'Should have returned -1 as a bad status check'
        assert message is None, 'Invalid code type should have returned None for message'

    def test_projector_get_status_valid(self):
        """
        Test to check returned information for status codes
        """
        # GIVEN: Test object
        test_message = 'Not Connected'
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

        # WHEN: get_status called
        code, message = pjlink._get_status(status=S_NOT_CONNECTED)

        # THEN: Proper strings should have been returned
        assert code == 'S_NOT_CONNECTED', 'Code returned should have been the same code that was sent'
        assert message == test_message, 'Description of code should have been returned'

    def test_projector_get_status_unknown(self):
        """
        Test to check returned information for unknown code
        """
        # GIVEN: Test object
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

        # WHEN: get_status called
        code, message = pjlink._get_status(status=9999)

        # THEN: Proper strings should have been returned
        assert code is None, 'Code returned should have been the same code that was sent'
        assert message is None, 'Should have returned None as message'
