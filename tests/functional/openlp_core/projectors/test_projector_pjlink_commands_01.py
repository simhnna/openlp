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
Package to test the openlp.core.projectors.pjlink commands package.
"""
from unittest import TestCase
from unittest.mock import call, patch

import openlp.core.projectors.pjlink
from openlp.core.projectors.constants import PJLINK_ERST_DATA, PJLINK_ERST_STATUS, PJLINK_POWR_STATUS, \
    STATUS_CODE, STATUS_MSG, E_ERROR, E_NOT_CONNECTED, E_UNKNOWN_SOCKET_ERROR, E_WARN, \
    S_CONNECTED, S_CONNECTING, S_OFF, S_OK, S_ON, S_NOT_CONNECTED, S_STANDBY
from openlp.core.projectors.db import Projector
from openlp.core.projectors.pjlink import PJLink

from tests.resources.projector.data import TEST1_DATA


class TestPJLinkCommands(TestCase):
    """
    Tests for the PJLinkCommands class part 1
    """
    def test_projector_change_status_unknown_socket_error(self):
        """
        Test change_status with connection error
        """
        log_debug_calls = [
            call('(111.111.111.111) Changing status to '
                 '{status} "{msg}"'.format(status=STATUS_CODE[E_UNKNOWN_SOCKET_ERROR],
                                           msg=STATUS_MSG[E_UNKNOWN_SOCKET_ERROR])),
            call('(111.111.111.111) status_connect: '
                 '{code}: "{msg}"'.format(code=STATUS_CODE[E_NOT_CONNECTED],
                                          msg=STATUS_MSG[E_NOT_CONNECTED])),
            call('(111.111.111.111) projector_status: '
                 '{code}: "{msg}"'.format(code=STATUS_CODE[S_OK],
                                          msg=STATUS_MSG[S_OK])),
            call('(111.111.111.111) error_status: '
                 '{code}: "{msg}"'.format(code=STATUS_CODE[E_UNKNOWN_SOCKET_ERROR],
                                          msg=STATUS_MSG[E_UNKNOWN_SOCKET_ERROR]))]

        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'changeStatus') as mock_changeStatus, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons') as mock_UpdateIcons:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.projector_status = 0
            pjlink.status_connect = 0

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
        log_debug_calls = [
            call('(111.111.111.111) Changing status to '
                 '{status} "{msg}"'.format(status=STATUS_CODE[S_CONNECTING],
                                           msg=STATUS_MSG[S_CONNECTING])),
            call('(111.111.111.111) status_connect: '
                 '{code}: "{msg}"'.format(code=STATUS_CODE[S_CONNECTING],
                                          msg=STATUS_MSG[S_CONNECTING])),
            call('(111.111.111.111) projector_status: '
                 '{code}: "{msg}"'.format(code=STATUS_CODE[S_OK],
                                          msg=STATUS_MSG[S_OK])),
            call('(111.111.111.111) error_status: '
                 '{code}: "{msg}"'.format(code=STATUS_CODE[S_OK],
                                          msg=STATUS_MSG[S_OK]))]

        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'changeStatus') as mock_changeStatus, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons') as mock_UpdateIcons:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.projector_status = 0
            pjlink.status_connect = 0

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
        log_debug_calls = [
            call('(111.111.111.111) Changing status to '
                 '{status} "{msg}"'.format(status=STATUS_CODE[S_CONNECTED],
                                           msg=STATUS_MSG[S_CONNECTED])),
            call('(111.111.111.111) status_connect: '
                 '{code}: "{msg}"'.format(code=STATUS_CODE[S_CONNECTED],
                                          msg=STATUS_MSG[S_CONNECTED])),
            call('(111.111.111.111) projector_status: '
                 '{code}: "{msg}"'.format(code=STATUS_CODE[S_OK],
                                          msg=STATUS_MSG[S_OK])),
            call('(111.111.111.111) error_status: '
                 '{code}: "{msg}"'.format(code=STATUS_CODE[S_OK],
                                          msg=STATUS_MSG[S_OK]))]

        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'changeStatus') as mock_changeStatus:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.projector_status = 0
            pjlink.status_connect = 0

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
        test_message = 'Different Status Message than default'
        log_debug_calls = [
            call('(111.111.111.111) Changing status to {status} "{msg}"'.format(status=STATUS_CODE[S_ON],
                                                                                msg=test_message)),
            call('(111.111.111.111) status_connect: {code}: "{msg}"'.format(code=STATUS_CODE[S_OK],
                                                                            msg=test_message)),
            call('(111.111.111.111) projector_status: {code}: "{msg}"'.format(code=STATUS_CODE[S_ON],
                                                                              msg=test_message)),
            call('(111.111.111.111) error_status: {code}: "{msg}"'.format(code=STATUS_CODE[S_OK],
                                                                          msg=test_message))]

        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'changeStatus') as mock_changeStatus:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.projector_status = 0
            pjlink.status_connect = 0

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
        test_data = 'AVMT'
        log_debug_calls = [call('(111.111.111.111) reset_information() connect status is '
                                '{state}'.format(state=STATUS_CODE[S_NOT_CONNECTED])),
                           call('(111.111.111.111) Sending {cmd} command'.format(cmd=test_data))]

        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

            # WHEN: get_av_mute_status is called
            pjlink.get_av_mute_status()

            # THEN: log data and send_command should have been called
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_send_command.assert_called_once_with(cmd=test_data)

    def test_projector_get_available_inputs(self):
        """
        Test sending command to retrieve avaliable inputs
        """
        test_data = 'INST'
        log_debug_calls = [call('(111.111.111.111) reset_information() connect status is '
                                '{state}'.format(state=STATUS_CODE[S_NOT_CONNECTED])),
                           call('(111.111.111.111) Sending {cmd} command'.format(cmd=test_data))]

        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

            # WHEN: get_available_inputs is called
            pjlink.get_available_inputs()

            # THEN: log data and send_command should have been called
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_send_command.assert_called_once_with(cmd=test_data)

    def test_projector_get_error_status(self):
        """
        Test sending command to retrieve projector error status
        """
        test_data = 'ERST'
        log_debug_calls = [call('(111.111.111.111) reset_information() connect status is '
                                '{state}'.format(state=STATUS_CODE[S_NOT_CONNECTED])),
                           call('(111.111.111.111) Sending {cmd} command'.format(cmd=test_data))]
        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

            # WHEN: get_error_status is called
            pjlink.get_error_status()

            # THEN: log data and send_command should have been called
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_send_command.assert_called_once_with(cmd=test_data)

    def test_projector_get_input_source(self):
        """
        Test sending command to retrieve current input
        """
        test_data = 'INPT'
        log_debug_calls = [call('(111.111.111.111) reset_information() connect status is '
                                '{state}'.format(state=STATUS_CODE[S_NOT_CONNECTED])),
                           call('(111.111.111.111) Sending {cmd} command'.format(cmd=test_data))]

        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

            # WHEN: get_input_source is called
            pjlink.get_input_source()

            # THEN: log data and send_command should have been called
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_send_command.assert_called_once_with(cmd=test_data)

    def test_projector_get_lamp_status(self):
        """
        Test sending command to retrieve lamp(s) status
        """
        test_data = 'LAMP'
        log_debug_calls = [call('(111.111.111.111) reset_information() connect status is '
                                '{state}'.format(state=STATUS_CODE[S_NOT_CONNECTED])),
                           call('(111.111.111.111) Sending {cmd} command'.format(cmd=test_data))]

        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

            # WHEN: get_input_source is called
            pjlink.get_lamp_status()

            # THEN: log data and send_command should have been called
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_send_command.assert_called_once_with(cmd=test_data)

    def test_projector_get_manufacturer(self):
        """
        Test sending command to retrieve manufacturer name
        """
        test_data = 'INF1'
        log_debug_calls = [call('(111.111.111.111) reset_information() connect status is '
                                '{state}'.format(state=STATUS_CODE[S_NOT_CONNECTED])),
                           call('(111.111.111.111) Sending {cmd} command'.format(cmd=test_data))]

        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

            # WHEN: get_input_source is called
            pjlink.get_manufacturer()

            # THEN: log data and send_command should have been called
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_send_command.assert_called_once_with(cmd=test_data)

    def test_projector_get_model(self):
        """
        Test sending command to get model information
        """
        test_data = 'INF2'
        log_debug_calls = [call('(111.111.111.111) reset_information() connect status is '
                                '{state}'.format(state=STATUS_CODE[S_NOT_CONNECTED])),
                           call('(111.111.111.111) Sending {cmd} command'.format(cmd=test_data))]

        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

            # WHEN: get_input_source is called
            pjlink.get_model()

            # THEN: log data and send_command should have been called
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_send_command.assert_called_once_with(cmd=test_data)

    def test_projector_get_name(self):
        """
        Test sending command to get user-assigned name
        """
        test_data = 'NAME'
        log_debug_calls = [call('(111.111.111.111) reset_information() connect status is '
                                '{state}'.format(state=STATUS_CODE[S_NOT_CONNECTED])),
                           call('(111.111.111.111) Sending {cmd} command'.format(cmd=test_data))]

        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

            # WHEN: get_input_source is called
            pjlink.get_name()

            # THEN: log data and send_command should have been called
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_send_command.assert_called_once_with(cmd=test_data)

    def test_projector_get_other_info(self):
        """
        Test sending command to retrieve other information
        """
        test_data = 'INFO'
        log_debug_calls = [call('(111.111.111.111) reset_information() connect status is '
                                '{state}'.format(state=STATUS_CODE[S_NOT_CONNECTED])),
                           call('(111.111.111.111) Sending {cmd} command'.format(cmd=test_data))]

        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

            # WHEN: get_input_source is called
            pjlink.get_other_info()

            # THEN: log data and send_command should have been called
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_send_command.assert_called_once_with(cmd=test_data)

    def test_projector_get_power_status(self):
        """
        Test sending command to retrieve current power state
        """
        test_data = 'POWR'
        log_debug_calls = [call('(111.111.111.111) reset_information() connect status is '
                                '{state}'.format(state=STATUS_CODE[S_NOT_CONNECTED])),
                           call('(111.111.111.111) Sending {cmd} command'.format(cmd=test_data))]

        # GIVEN: Test object and mocks
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

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

    def test_projector_process_inf1(self):
        """
        Test saving INF1 data (manufacturer)
        """
        test_data = 'TEst INformation MultiCase'

        # GIVEN: Test object
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.manufacturer = None

        # WHEN: process_inf called with test data
        pjlink.process_inf1(data=test_data)

        # THEN: Data should be saved
        assert pjlink.manufacturer == test_data, 'Test data should have been saved'

    def test_projector_process_inf2(self):
        """
        Test saving INF2 data (model)
        """
        test_data = 'TEst moDEl MultiCase'

        # GIVEN: Test object
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.model = None

        # WHEN: process_inf called with test data
        pjlink.process_inf2(data=test_data)

        # THEN: Data should be saved
        assert pjlink.model == test_data, 'Test data should have been saved'

    def test_projector_process_info(self):
        """
        Test saving INFO data (other information)
        """
        test_data = 'TEst ExtrANEous MultiCase INformatoin that MFGR might Set'

        # GIVEN: Test object
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.other_info = None

        # WHEN: process_inf called with test data
        pjlink.process_info(data=test_data)

        # THEN: Data should be saved
        assert pjlink.other_info == test_data, 'Test data should have been saved'

    def test_projector_process_avmt_bad_data(self):
        """
        Test avmt bad data fail
        """
        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons') as mock_UpdateIcons:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.shutter = True
            pjlink.mute = True

            # WHEN: Called with an invalid setting
            pjlink.process_avmt('36')

            # THEN: Shutter should be closed and mute should be True
            assert pjlink.shutter is True, 'Shutter should changed'
            assert pjlink.mute is True, 'Audio should not have changed'
            assert mock_UpdateIcons.emit.called is False, 'Update icons should NOT have been called'

    def test_projector_process_avmt_closed_muted(self):
        """
        Test avmt status shutter closed and mute off
        """
        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons') as mock_UpdateIcons:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.shutter = False
            pjlink.mute = False

            # WHEN: Called with setting shutter to closed and mute on
            pjlink.process_avmt('31')

            # THEN: Shutter should be closed and mute should be True
            assert pjlink.shutter is True, 'Shutter should have been set to closed'
            assert pjlink.mute is True, 'Audio should be muted'
            assert mock_UpdateIcons.emit.called is True, 'Update icons should have been called'

    def test_projector_process_avmt_shutter_closed(self):
        """
        Test avmt status shutter closed and audio unchanged
        """
        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons') as mock_UpdateIcons:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.shutter = False
            pjlink.mute = True

            # WHEN: Called with setting shutter closed and mute off
            pjlink.process_avmt('11')

            # THEN: Shutter should be True and mute should be False
            assert pjlink.shutter is True, 'Shutter should have been set to closed'
            assert pjlink.mute is True, 'Audio should not have changed'
            assert mock_UpdateIcons.emit.called is True, 'Update icons should have been called'

    def test_projector_process_avmt_audio_muted(self):
        """
        Test avmt status shutter unchanged and mute on
        """
        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons') as mock_UpdateIcons:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.shutter = True
            pjlink.mute = False

            # WHEN: Called with setting shutter closed and mute on
            pjlink.process_avmt('21')

            # THEN: Shutter should be closed and mute should be True
            assert pjlink.shutter is True, 'Shutter should not have changed'
            assert pjlink.mute is True, 'Audio should be off'
            assert mock_UpdateIcons.emit.called is True, 'Update icons should have been called'

    def test_projector_process_avmt_open_unmuted(self):
        """
        Test avmt status shutter open and mute off
        """
        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons') as mock_UpdateIcons:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.shutter = True
            pjlink.mute = True

            # WHEN: Called with setting shutter to closed and mute on
            pjlink.process_avmt('30')

            # THEN: Shutter should be closed and mute should be True
            assert pjlink.shutter is False, 'Shutter should have been set to open'
            assert pjlink.mute is False, 'Audio should be on'
            assert mock_UpdateIcons.emit.called is True, 'Update icons should have been called'

    def test_projector_process_clss_one(self):
        """
        Test class 1 sent from projector
        """
        # GIVEN: Test object
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

        # WHEN: Process class response
        pjlink.process_clss('1')

        # THEN: Projector class should be set to 1
        assert pjlink.pjlink_class == '1', 'Projector should have set class=1'

    def test_projector_process_clss_two(self):
        """
        Test class 2 sent from projector
        """
        # GIVEN: Test object
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

        # WHEN: Process class response
        pjlink.process_clss('2')

        # THEN: Projector class should be set to 1
        assert pjlink.pjlink_class == '2', 'Projector should have set class=2'

    def test_projector_process_clss_invalid_nan(self):
        """
        Test CLSS reply has no class number
        """
        log_debug_calls = [call('(111.111.111.111) reset_information() connect status is '
                                '{state}'.format(state=STATUS_CODE[S_NOT_CONNECTED])),
                           call('(111.111.111.111) Setting pjlink_class for this projector to "1"')]
        log_error_calls = [call('(111.111.111.111) NAN CLSS version reply "Z" - defaulting to class "1"')]

        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

            # WHEN: Process invalid reply
            pjlink.process_clss('Z')

            # THEN: Projector class should be set with default value
            assert pjlink.pjlink_class == '1', 'Invalid NaN class reply should have set class=1'
            mock_log.error.assert_has_calls(log_error_calls)
            mock_log.debug.assert_has_calls(log_debug_calls)

    def test_projector_process_clss_invalid_no_version(self):
        """
        Test CLSS reply has no class number
        """
        log_debug_calls = [call('(111.111.111.111) reset_information() connect status is '
                                '{state}'.format(state=STATUS_CODE[S_NOT_CONNECTED])),
                           call('(111.111.111.111) Setting pjlink_class for this projector to "1"')]
        log_error_calls = [call('(111.111.111.111) No numbers found in class version reply "Invalid" '
                                '- defaulting to class "1"')]

        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

            # WHEN: Process invalid reply
            pjlink.process_clss('Invalid')

            # THEN: Projector class should be set with default value
            assert pjlink.pjlink_class == '1', 'Invalid class reply should have set class=1'
            mock_log.error.assert_has_calls(log_error_calls)
            mock_log.debug.assert_has_calls(log_debug_calls)

    def test_projector_process_erst_all_ok(self):
        """
        Test to verify pjlink.projector_errors is set to None when no errors
        """
        chk_data = '0' * PJLINK_ERST_DATA['DATA_LENGTH']

        # GIVEN: Test object
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

        # WHEN: process_erst with no errors
        pjlink.process_erst(chk_data)

        # THEN: PJLink instance errors should be None
        assert pjlink.projector_errors is None, 'projector_errors should have been set to None'

    def test_projector_process_erst_data_invalid_length(self):
        """
        Test test_projector_process_erst_data_invalid_length
        """
        chk_data = '0' * (PJLINK_ERST_DATA['DATA_LENGTH'] + 1)
        log_debug_calls = [call('(111.111.111.111) reset_information() connect status is '
                                '{state}'.format(state=STATUS_CODE[S_NOT_CONNECTED]))]
        log_warn_calls = [call('111.111.111.111) Invalid error status response "0000000": '
                               'length != {chk}'.format(chk=PJLINK_ERST_DATA['DATA_LENGTH']))]

        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.projector_errors = None

            # WHEN: process_erst called with invalid data (too many values
            pjlink.process_erst(chk_data)

            # THEN: pjlink.projector_errors should be empty and warning logged
            assert pjlink.projector_errors is None, 'There should be no errors'
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_log.warning.assert_has_calls(log_warn_calls)

    def test_projector_process_erst_data_invalid_nan(self):
        """
        Test test_projector_process_erst_data_invalid_nan
        """
        chk_data = 'Z' + ('0' * (PJLINK_ERST_DATA['DATA_LENGTH'] - 1))
        log_debug_calls = [call('(111.111.111.111) reset_information() connect status is '
                                '{state}'.format(state=STATUS_CODE[S_NOT_CONNECTED]))]
        log_warn_calls = [call('(111.111.111.111) Invalid error status response "Z00000"')]

        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.projector_errors = None

            # WHEN: process_erst called with invalid data (too many values
            pjlink.process_erst(chk_data)

            # THEN: pjlink.projector_errors should be empty and warning logged
            assert pjlink.projector_errors is None, 'There should be no errors'
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_log.warning.assert_has_calls(log_warn_calls)

    def test_projector_process_erst_all_warn(self):
        """
        Test test_projector_process_erst_all_warn
        """
        chk_data = '{fan}{lamp}{temp}{cover}{filt}{other}'.format(fan=PJLINK_ERST_STATUS[E_WARN],
                                                                  lamp=PJLINK_ERST_STATUS[E_WARN],
                                                                  temp=PJLINK_ERST_STATUS[E_WARN],
                                                                  cover=PJLINK_ERST_STATUS[E_WARN],
                                                                  filt=PJLINK_ERST_STATUS[E_WARN],
                                                                  other=PJLINK_ERST_STATUS[E_WARN])
        chk_test = {'Fan': E_WARN,
                    'Lamp': E_WARN,
                    'Temperature': E_WARN,
                    'Cover': E_WARN,
                    'Filter': E_WARN,
                    'Other': E_WARN}

        # GIVEN: Test object
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.projector_errors = None

        # WHEN: process_erst with status set to WARN
        pjlink.process_erst(chk_data)

        # THEN: PJLink instance errors should match chk_value
        assert pjlink.projector_errors == chk_test, 'Projector errors should be all E_WARN'

    def test_projector_process_erst_all_error(self):
        """
        Test test_projector_process_erst_all_error
        """
        chk_data = '{fan}{lamp}{temp}{cover}{filt}{other}'.format(fan=PJLINK_ERST_STATUS[E_ERROR],
                                                                  lamp=PJLINK_ERST_STATUS[E_ERROR],
                                                                  temp=PJLINK_ERST_STATUS[E_ERROR],
                                                                  cover=PJLINK_ERST_STATUS[E_ERROR],
                                                                  filt=PJLINK_ERST_STATUS[E_ERROR],
                                                                  other=PJLINK_ERST_STATUS[E_ERROR])
        chk_test = {'Fan': E_ERROR,
                    'Lamp': E_ERROR,
                    'Temperature': E_ERROR,
                    'Cover': E_ERROR,
                    'Filter': E_ERROR,
                    'Other': E_ERROR}

        # GIVEN: Test object
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.projector_errors = None

        # WHEN: process_erst with status set to WARN
        pjlink.process_erst(chk_data)

        # THEN: PJLink instance errors should match chk_value
        assert pjlink.projector_errors == chk_test, 'Projector errors should be all E_ERROR'

    def test_projector_process_erst_warn_cover_only(self):
        """
        Test test_projector_process_erst_warn_cover_only
        """
        chk_data = '{fan}{lamp}{temp}{cover}{filt}{other}'.format(fan=PJLINK_ERST_STATUS[S_OK],
                                                                  lamp=PJLINK_ERST_STATUS[S_OK],
                                                                  temp=PJLINK_ERST_STATUS[S_OK],
                                                                  cover=PJLINK_ERST_STATUS[E_WARN],
                                                                  filt=PJLINK_ERST_STATUS[S_OK],
                                                                  other=PJLINK_ERST_STATUS[S_OK])
        chk_test = {'Cover': E_WARN}

        # GIVEN: Test object
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.projector_errors = None

        # WHEN: process_erst with status set to WARN
        pjlink.process_erst(chk_data)

        # THEN: PJLink instance errors should match only cover warning
        assert 1 == len(pjlink.projector_errors), 'There should only be 1 error listed in projector_errors'
        assert 'Cover' in pjlink.projector_errors, '"Cover" should be the only error listed'
        assert pjlink.projector_errors['Cover'] == E_WARN, '"Cover" should have E_WARN listed as error'
        assert chk_test == pjlink.projector_errors, 'projector_errors should match test errors'

    def test_projector_process_inpt_valid(self):
        """
        Test input source status shows current input
        """
        log_debug_calls = [call('(111.111.111.111) reset_information() connect status is S_NOT_CONNECTED')]
        chk_source_available = ['11', '12', '21', '22', '31', '32']

        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.source_available = chk_source_available
            pjlink.source = '11'

            # WHEN: Called with input source
            pjlink.process_inpt('21')

            # THEN: Input selected should reflect current input
            assert pjlink.source == '21', 'Input source should be set to "21"'
            mock_log.debug.assert_has_calls(log_debug_calls)

    def test_projector_process_input_not_in_list(self):
        """
        Test setting input outside of available inputs

        TODO: Future test
        """
        pass

    def test_projector_process_input_not_in_default(self):
        """
        Test setting input with no sources available
        TODO: Future test
        """
        pass

    def test_projector_process_input_invalid(self):
        """
        Test setting input with an invalid value

        TODO: Future test
        """

    def test_projector_process_inst_class_1(self):
        """
        Test saving video source available information
        """
        log_debug_calls = [call('(111.111.111.111) Setting projector sources_available to '
                                '"[\'11\', \'12\', \'21\', \'22\', \'31\', \'32\']"')]
        chk_data = '21 12 11 22 32 31'  # Although they should already be sorted, use unsorted to verify method
        chk_test = ['11', '12', '21', '22', '31', '32']

        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.source_available = []

            # WHEN: process_inst called with test data
            pjlink.process_inst(data=chk_data)

            # THEN: Data should have been sorted and saved properly
            assert pjlink.source_available == chk_test, "Sources should have been sorted and saved"
            mock_log.debug.assert_has_calls(log_debug_calls)

    def test_projector_process_lamp_invalid(self):
        """
        Test status multiple lamp on/off and hours
        """
        log_data = [call('(111.111.111.111) process_lamp(): Invalid data "11111 1 22222 0 333A3 1"')]

        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.lamp = [{'Hours': 00000, 'On': True},
                           {'Hours': 11111, 'On': False}]

            # WHEN: Call process_command with invalid lamp data
            pjlink.process_lamp('11111 1 22222 0 333A3 1')

            # THEN: lamps should not have changed
            assert 2 == len(pjlink.lamp), 'Projector should have kept 2 lamps specified'
            assert pjlink.lamp[0]['On'] is True, 'Lamp 1 power status should have stayed TRUE'
            assert 00000 == pjlink.lamp[0]['Hours'], 'Lamp 1 hours should have been left at 00000'
            assert pjlink.lamp[1]['On'] is False, 'Lamp 2 power status should have stayed FALSE'
            assert 11111 == pjlink.lamp[1]['Hours'], 'Lamp 2 hours should have been left at 11111'
            mock_log.warning.assert_has_calls(log_data)

    def test_projector_process_lamp_multiple(self):
        """
        Test status multiple lamp on/off and hours
        """
        # GIVEN: Test object
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.lamp = []

        # WHEN: Call process_command with invalid lamp data
        pjlink.process_lamp('11111 1 22222 0 33333 1')

        # THEN: Lamp should have been set with proper lamp status
        assert 3 == len(pjlink.lamp), 'Projector should have 3 lamps specified'
        assert pjlink.lamp[0]['On'] is True, 'Lamp 1 power status should have been set to TRUE'
        assert 11111 == pjlink.lamp[0]['Hours'], 'Lamp 1 hours should have been set to 11111'
        assert pjlink.lamp[1]['On'] is False, 'Lamp 2 power status should have been set to FALSE'
        assert 22222 == pjlink.lamp[1]['Hours'], 'Lamp 2 hours should have been set to 22222'
        assert pjlink.lamp[2]['On'] is True, 'Lamp 3 power status should have been set to TRUE'
        assert 33333 == pjlink.lamp[2]['Hours'], 'Lamp 3 hours should have been set to 33333'

    def test_projector_process_lamp_single(self):
        """
        Test status lamp on/off and hours
        """

        # GIVEN: Test object
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.lamp = []

        # WHEN: Call process_command with invalid lamp data
        pjlink.process_lamp('22222 1')

        # THEN: Lamp should have been set with status=ON and hours=22222
        assert 1 == len(pjlink.lamp), 'Projector should have only 1 lamp'
        assert pjlink.lamp[0]['On'] is True, 'Lamp power status should have been set to TRUE'
        assert 22222 == pjlink.lamp[0]['Hours'], 'Lamp hours should have been set to 22222'

    def test_projector_process_name(self):
        """
        Test saving NAME data from projector
        """
        chk_data = "Some Name the End-User Set IN Projector"
        log_debug_calls = [call('(111.111.111.111) Setting projector PJLink name to '
                                '"Some Name the End-User Set IN Projector"')]

        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

            # WHEN: process_name called with test data
            pjlink.process_name(data=chk_data)

            # THEN: name should be set and logged
            assert pjlink.pjlink_name == chk_data, 'Name test data should have been saved'
            mock_log.debug.assert_has_calls(log_debug_calls)

    def test_projector_process_powr_on(self):
        """
        Test status power to ON
        """
        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'change_status') as mock_change_status, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons') as mock_UpdateIcons:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.power = S_STANDBY

            # WHEN: process_name called with test data
            pjlink.process_powr(data=PJLINK_POWR_STATUS[S_ON])

            # THEN: Power should be set to ON
            assert pjlink.power == S_ON, 'Power should have been set to ON'
            assert mock_UpdateIcons.emit.called is True, 'projectorUpdateIcons should have been called'
            mock_send_command.assert_called_once_with('INST')
            mock_change_status.assert_called_once_with(S_ON)

    def test_projector_process_powr_invalid(self):
        """
        Test process_powr invalid call
        """
        log_warn_calls = [call('(111.111.111.111) Unknown power response: "99"')]

        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'change_status') as mock_change_status, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons') as mock_UpdateIcons:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.power = S_STANDBY

            # WHEN: process_name called with test data
            pjlink.process_powr(data='99')

            # THEN: Power should be set to ON
            assert pjlink.power == S_STANDBY, 'Power should not have changed'
            assert mock_UpdateIcons.emit.called is False, 'projectorUpdateIcons() should not have been called'
            mock_change_status.called is False, 'change_status() should not have been called'
            mock_send_command.called is False, 'send_command() should not have been called'
            mock_log.warning.assert_has_calls(log_warn_calls)

    def test_projector_process_powr_off(self):
        """
        Test status power to STANDBY
        """
        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'change_status') as mock_change_status, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons') as mock_UpdateIcons:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.power = S_ON

            # WHEN: process_name called with test data
            pjlink.process_powr(data=PJLINK_POWR_STATUS[S_STANDBY])

            # THEN: Power should be set to ON
            assert pjlink.power == S_STANDBY, 'Power should have changed to S_STANDBY'
            assert mock_UpdateIcons.emit.called is True, 'projectorUpdateIcons should have been called'
            mock_change_status.called is True, 'change_status should have been called'
            mock_send_command.called is False, 'send_command should not have been called'

    def test_projector_process_rfil_save(self):
        """
        Test saving filter type
        """
        filter_model = 'Filter Type Test'

        # GIVEN: Test object
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.model_filter = None

        # WHEN: Filter model is received
        pjlink.process_rfil(data=filter_model)

        # THEN: Filter model number should be saved
        assert pjlink.model_filter == filter_model, 'Filter type should have been saved'

    def test_projector_process_rfil_nosave(self):
        """
        Test saving filter type previously saved
        """
        filter_model = 'Filter Type Test'
        log_warn_calls = [call('(111.111.111.111) Filter model already set'),
                          call('(111.111.111.111) Saved model: "Old filter type"'),
                          call('(111.111.111.111) New model: "Filter Type Test"')]

        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.model_filter = 'Old filter type'

            # WHEN: Filter model is received
            pjlink.process_rfil(data=filter_model)

            # THEN: Filter model number should be saved
            assert pjlink.model_filter != filter_model, 'Filter type should NOT have been saved'
            mock_log.warning.assert_has_calls(log_warn_calls)

    def test_projector_process_rlmp_save(self):
        """
        Test saving lamp type
        """
        # GIVEN: Test object
        # GIVEN: Test object
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.model_lamp = None
        lamp_model = 'Lamp Type Test'

        # WHEN: Filter model is received
        pjlink.process_rlmp(data=lamp_model)

        # THEN: Filter model number should be saved
        assert pjlink.model_lamp == lamp_model, 'Lamp type should have been saved'

    def test_projector_process_rlmp_nosave(self):
        """
        Test saving lamp type previously saved
        """
        lamp_model = 'Lamp Type Test'
        log_warn_calls = [call('(111.111.111.111) Lamp model already set'),
                          call('(111.111.111.111) Saved lamp: "Old lamp type"'),
                          call('(111.111.111.111) New lamp: "Lamp Type Test"')]

        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.model_lamp = 'Old lamp type'

            # WHEN: Filter model is received
            pjlink.process_rlmp(data=lamp_model)

            # THEN: Filter model number should be saved
            assert pjlink.model_lamp != lamp_model, 'Lamp type should NOT have been saved'
            mock_log.warning.assert_has_calls(log_warn_calls)

    def test_projector_process_snum_set(self):
        """
        Test saving serial number from projector
        """
        log_debug_calls = [call('(111.111.111.111) Setting projector serial number to "Test Serial Number"')]
        test_number = 'Test Serial Number'

        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.serial_no = None

            # WHEN: No serial number is set and we receive serial number command
            pjlink.process_snum(data=test_number)

            # THEN: Serial number should be set
            assert pjlink.serial_no == test_number, 'Projector serial number should have been set'
            mock_log.debug.assert_has_calls(log_debug_calls)

    def test_projector_process_snum_different(self):
        """
        Test projector serial number different than saved serial number
        """
        log_warn_calls = [call('(111.111.111.111) Projector serial number does not match saved serial number'),
                          call('(111.111.111.111) Saved:    "Previous serial number"'),
                          call('(111.111.111.111) Received: "Test Serial Number"'),
                          call('(111.111.111.111) NOT saving serial number')]
        test_number = 'Test Serial Number'

        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.serial_no = 'Previous serial number'

            # WHEN: No serial number is set and we receive serial number command
            pjlink.process_snum(data=test_number)

            # THEN: Serial number should be set
            assert pjlink.serial_no != test_number, 'Projector serial number should NOT have been set'
            mock_log.warning.assert_has_calls(log_warn_calls)

    def test_projector_process_sver(self):
        """
        Test invalid software version information - too long
        """
        test_data = 'Test 1 Subtest 1'
        log_debug_calls = [call('(111.111.111.111) Setting projector software version to "Test 1 Subtest 1"')]

        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.sw_version = None
            pjlink.sw_version_received = None

            # WHEN: process_sver called with invalid data
            pjlink.process_sver(data=test_data)

            # THEN: Version information should not change
            assert pjlink.sw_version == test_data, 'Software version should have been updated'
            mock_log.debug.assert_has_calls(log_debug_calls)

    def test_projector_process_sver_changed(self):
        """
        Test invalid software version information - Received different than saved
        """
        test_data_old = 'Test 1 Subtest 1'
        test_data_new = 'Test 1 Subtest 2'
        log_warn_calls = [call('(111.111.111.111) Projector software version does not match saved software version'),
                          call('(111.111.111.111) Saved:    "Test 1 Subtest 1"'),
                          call('(111.111.111.111) Received: "Test 1 Subtest 2"'),
                          call('(111.111.111.111) Updating software version')]

        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.sw_version = test_data_old

            # WHEN: process_sver called with invalid data
            pjlink.process_sver(data=test_data_new)

            # THEN: Version information should not change
            assert pjlink.sw_version == test_data_new, 'Software version should have changed'
            mock_log.warning.assert_has_calls(log_warn_calls)

    def test_projector_process_sver_invalid(self):
        """
        Test invalid software version information - too long
        """
        test_data = 'This is a test software version line that is too long based on PJLink version 2 specs'
        log_warn_calls = [call('Invalid software version - too long')]

        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.sw_version = None

            # WHEN: process_sver called with invalid data
            pjlink.process_sver(data=test_data)

            # THEN: Version information should not change
            assert pjlink.sw_version is None, 'Software version should not have changed'
            assert pjlink.sw_version_received is None, 'Received software version should not have changed'
            mock_log.warning.assert_has_calls(log_warn_calls)

    def test_projector_reset_information(self):
        """
        Test reset_information() resets all information and stops timers
        """
        log_debug_calls = [call('(111.111.111.111): Calling timer.stop()'),
                           call('(111.111.111.111): Calling socket_timer.stop()')]

        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            # timer and socket_timer not available until instantiation, so mock here
            with patch.object(pjlink, 'socket_timer') as mock_socket_timer, \
                    patch.object(pjlink, 'timer') as mock_timer:

                pjlink.power = S_ON
                pjlink.pjlink_name = 'OPENLPTEST'
                pjlink.manufacturer = 'PJLINK'
                pjlink.model = '1'
                pjlink.shutter = True
                pjlink.mute = True
                pjlink.lamp = True
                pjlink.fan = True
                pjlink.source_available = True
                pjlink.other_info = 'ANOTHER TEST'
                pjlink.send_queue = True
                pjlink.send_busy = True

                # WHEN: reset_information() is called
                pjlink.reset_information()

                # THEN: All information should be reset and timers stopped
                assert pjlink.power == S_OFF, 'Projector power should be OFF'
                assert pjlink.pjlink_name is None, 'Projector pjlink_name should be None'
                assert pjlink.manufacturer is None, 'Projector manufacturer should be None'
                assert pjlink.model is None, 'Projector model should be None'
                assert pjlink.shutter is None, 'Projector shutter should be None'
                assert pjlink.mute is None, 'Projector shuttter should be None'
                assert pjlink.lamp is None, 'Projector lamp should be None'
                assert pjlink.fan is None, 'Projector fan should be None'
                assert pjlink.source_available is None, 'Projector source_available should be None'
                assert pjlink.source is None, 'Projector source should be None'
                assert pjlink.other_info is None, 'Projector other_info should be None'
                assert pjlink.send_queue == [], 'Projector send_queue should be an empty list'
                assert pjlink.send_busy is False, 'Projector send_busy should be False'
                assert mock_timer.stop.called is True, 'Projector timer.stop()  should have been called'
                assert mock_socket_timer.stop.called is True, 'Projector socket_timer.stop() should have been called'
                mock_log.debug.assert_has_calls(log_debug_calls)
