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
Package to test the openlp.core.lib.projector.pjlink commands package.
"""
from unittest import TestCase
from unittest.mock import patch

import openlp.core.lib.projector.pjlink
from openlp.core.lib.projector.pjlink import PJLink
from openlp.core.lib.projector.constants import ERROR_STRING, PJLINK_ERST_DATA, PJLINK_ERST_STATUS, \
    PJLINK_POWR_STATUS, \
    E_ERROR, E_NOT_CONNECTED, E_SOCKET_ADDRESS_NOT_AVAILABLE, E_UNKNOWN_SOCKET_ERROR, E_WARN, \
    S_CONNECTED, S_OFF, S_ON, S_NOT_CONNECTED, S_CONNECTING, S_STANDBY

from tests.resources.projector.data import TEST_PIN

pjlink_test = PJLink(name='test', ip='127.0.0.1', pin=TEST_PIN, no_poll=True)

# Create a list of ERST positional data so we don't have to redo the same buildup multiple times
PJLINK_ERST_POSITIONS = []
for pos in range(0, len(PJLINK_ERST_DATA)):
    if pos in PJLINK_ERST_DATA:
        PJLINK_ERST_POSITIONS.append(PJLINK_ERST_DATA[pos])


class TestPJLinkCommands(TestCase):
    """
    Tests for the PJLink module
    """
    @patch.object(pjlink_test, 'changeStatus')
    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_change_status_connection_error(self, mock_log, mock_change_status):
        """
        Test change_status with connection error
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.projector_status = 0
        pjlink.status_connect = 0
        test_code = E_UNKNOWN_SOCKET_ERROR
        mock_change_status.reset_mock()
        mock_log.reset_mock()

        # WHEN: change_status called with unknown socket error
        pjlink.change_status(status=test_code, msg=None)

        # THEN: Proper settings should change and signals sent
        self.assertEqual(pjlink.projector_status, E_NOT_CONNECTED, 'Projector status should be NOT CONNECTED')
        self.assertEqual(pjlink.status_connect, E_NOT_CONNECTED, 'Status connect should be NOT CONNECTED')
        mock_change_status.emit.assert_called_once_with(pjlink.ip, E_UNKNOWN_SOCKET_ERROR,
                                                        'An unidentified error occurred')
        self.assertEqual(mock_log.debug.call_count, 3, 'Debug log should have been called 3 times')

    @patch.object(pjlink_test, 'changeStatus')
    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_change_status_connection_status_connecting(self, mock_log, mock_change_status):
        """
        Test change_status with connection status
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.projector_status = 0
        pjlink.status_connect = 0
        test_code = S_CONNECTING
        mock_change_status.reset_mock()
        mock_log.reset_mock()

        # WHEN: change_status called with unknown socket error
        pjlink.change_status(status=test_code, msg=None)

        # THEN: Proper settings should change and signals sent
        self.assertEqual(pjlink.projector_status, S_NOT_CONNECTED, 'Projector status should be NOT CONNECTED')
        self.assertEqual(pjlink.status_connect, S_CONNECTING, 'Status connect should be CONNECTING')
        mock_change_status.emit.assert_called_once_with(pjlink.ip, S_CONNECTING, 'Connecting')
        self.assertEqual(mock_log.debug.call_count, 3, 'Debug log should have been called 3 times')

    @patch.object(pjlink_test, 'changeStatus')
    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_change_status_connection_status_connected(self, mock_log, mock_change_status):
        """
        Test change_status with connection status
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.projector_status = 0
        pjlink.status_connect = 0
        test_code = S_ON
        mock_change_status.reset_mock()
        mock_log.reset_mock()

        # WHEN: change_status called with unknown socket error
        pjlink.change_status(status=test_code, msg=None)

        # THEN: Proper settings should change and signals sent
        self.assertEqual(pjlink.projector_status, S_ON, 'Projector status should be ON')
        self.assertEqual(pjlink.status_connect, S_CONNECTED, 'Status connect should be CONNECTED')
        mock_change_status.emit.assert_called_once_with(pjlink.ip, S_ON, 'Power is on')
        self.assertEqual(mock_log.debug.call_count, 3, 'Debug log should have been called 3 times')

    @patch.object(pjlink_test, 'changeStatus')
    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_change_status_connection_status_with_message(self, mock_log, mock_change_status):
        """
        Test change_status with connection status
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.projector_status = 0
        pjlink.status_connect = 0
        test_message = 'Different Status Message than default'
        test_code = S_ON
        mock_change_status.reset_mock()
        mock_log.reset_mock()

        # WHEN: change_status called with unknown socket error
        pjlink.change_status(status=test_code, msg=test_message)

        # THEN: Proper settings should change and signals sent
        self.assertEqual(pjlink.projector_status, S_ON, 'Projector status should be ON')
        self.assertEqual(pjlink.status_connect, S_CONNECTED, 'Status connect should be CONNECTED')
        mock_change_status.emit.assert_called_once_with(pjlink.ip, S_ON, test_message)
        self.assertEqual(mock_log.debug.call_count, 3, 'Debug log should have been called 3 times')

    @patch.object(pjlink_test, 'send_command')
    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_get_av_mute_status(self, mock_log, mock_send_command):
        """
        Test sending command to retrieve shutter/audio state
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        mock_log.reset_mock()
        mock_send_command.reset_mock()
        test_data = 'AVMT'
        test_log = '(127.0.0.1) Sending AVMT command'

        # WHEN: get_av_mute_status is called
        pjlink.get_av_mute_status()

        # THEN: log data and send_command should have been called
        mock_log.debug.assert_called_once_with(test_log)
        mock_send_command.assert_called_once_with(cmd=test_data)

    @patch.object(pjlink_test, 'send_command')
    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_get_available_inputs(self, mock_log, mock_send_command):
        """
        Test sending command to retrieve avaliable inputs
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        mock_log.reset_mock()
        mock_send_command.reset_mock()
        test_data = 'INST'
        test_log = '(127.0.0.1) Sending INST command'

        # WHEN: get_available_inputs is called
        pjlink.get_available_inputs()

        # THEN: log data and send_command should have been called
        mock_log.debug.assert_called_once_with(test_log)
        mock_send_command.assert_called_once_with(cmd=test_data)

    @patch.object(pjlink_test, 'send_command')
    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_get_error_status(self, mock_log, mock_send_command):
        """
        Test sending command to retrieve projector error status
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        mock_log.reset_mock()
        mock_send_command.reset_mock()
        test_data = 'ERST'
        test_log = '(127.0.0.1) Sending ERST command'

        # WHEN: get_error_status is called
        pjlink.get_error_status()

        # THEN: log data and send_command should have been called
        mock_log.debug.assert_called_once_with(test_log)
        mock_send_command.assert_called_once_with(cmd=test_data)

    @patch.object(pjlink_test, 'send_command')
    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_get_input_source(self, mock_log, mock_send_command):
        """
        Test sending command to retrieve current input
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        mock_log.reset_mock()
        mock_send_command.reset_mock()
        test_data = 'INPT'
        test_log = '(127.0.0.1) Sending INPT command'

        # WHEN: get_input_source is called
        pjlink.get_input_source()

        # THEN: log data and send_command should have been called
        mock_log.debug.assert_called_once_with(test_log)
        mock_send_command.assert_called_once_with(cmd=test_data)

    @patch.object(pjlink_test, 'send_command')
    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_get_lamp_status(self, mock_log, mock_send_command):
        """
        Test sending command to retrieve lamp(s) status
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        mock_log.reset_mock()
        mock_send_command.reset_mock()
        test_data = 'LAMP'
        test_log = '(127.0.0.1) Sending LAMP command'

        # WHEN: get_lamp_status is called
        pjlink.get_lamp_status()

        # THEN: log data and send_command should have been called
        mock_log.debug.assert_called_once_with(test_log)
        mock_send_command.assert_called_once_with(cmd=test_data)

    @patch.object(pjlink_test, 'send_command')
    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_get_manufacturer(self, mock_log, mock_send_command):
        """
        Test sending command to retrieve manufacturer name
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        mock_log.reset_mock()
        mock_send_command.reset_mock()
        test_data = 'INF1'
        test_log = '(127.0.0.1) Sending INF1 command'

        # WHEN: get_manufacturer is called
        pjlink.get_manufacturer()

        # THEN: log data and send_command should have been called
        mock_log.debug.assert_called_once_with(test_log)
        mock_send_command.assert_called_once_with(cmd=test_data)

    @patch.object(pjlink_test, 'send_command')
    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_get_model(self, mock_log, mock_send_command):
        """
        Test sending command to get model information
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        mock_log.reset_mock()
        mock_send_command.reset_mock()
        test_data = 'INF2'
        test_log = '(127.0.0.1) Sending INF2 command'

        # WHEN: get_model is called
        pjlink.get_model()

        # THEN: log data and send_command should have been called
        mock_log.debug.assert_called_once_with(test_log)
        mock_send_command.assert_called_once_with(cmd=test_data)

    @patch.object(pjlink_test, 'send_command')
    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_get_name(self, mock_log, mock_send_command):
        """
        Test sending command to get user-assigned name
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        mock_log.reset_mock()
        mock_send_command.reset_mock()
        test_data = 'NAME'
        test_log = '(127.0.0.1) Sending NAME command'

        # WHEN: get_name is called
        pjlink.get_name()

        # THEN: log data and send_command should have been called
        mock_log.debug.assert_called_once_with(test_log)
        mock_send_command.assert_called_once_with(cmd=test_data)

    @patch.object(pjlink_test, 'send_command')
    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_get_other_info(self, mock_log, mock_send_command):
        """
        Test sending command to retrieve other information
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        mock_log.reset_mock()
        mock_send_command.reset_mock()
        test_data = 'INFO'
        test_log = '(127.0.0.1) Sending INFO command'

        # WHEN: get_other_info is called
        pjlink.get_other_info()

        # THEN: log data and send_command should have been called
        mock_log.debug.assert_called_once_with(test_log)
        mock_send_command.assert_called_once_with(cmd=test_data)

    @patch.object(pjlink_test, 'send_command')
    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_get_power_status(self, mock_log, mock_send_command):
        """
        Test sending command to retrieve current power state
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        mock_log.reset_mock()
        mock_send_command.reset_mock()
        test_data = 'POWR'
        test_log = '(127.0.0.1) Sending POWR command'

        # WHEN: get_power_status called
        pjlink.get_power_status()

        # THEN: log data and send_command should have been called
        mock_log.debug.assert_called_once_with(test_log)
        mock_send_command.assert_called_once_with(cmd=test_data)

    def test_projector_get_status_error(self):
        """
        Test to check returned information for error code
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        test_string = 'E_SOCKET_ADDRESS_NOT_AVAILABLE'
        test_message = 'The address specified to socket.bind() does not belong to the host'

        # WHEN: get_status called
        string, message = pjlink._get_status(status=E_SOCKET_ADDRESS_NOT_AVAILABLE)

        # THEN: Proper strings should have been returned
        self.assertEqual(string, test_string, 'Code as string should have been returned')
        self.assertEqual(message, test_message, 'Description of code should have been returned')

    def test_projector_get_status_invalid(self):
        """
        Test to check returned information for error code
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        test_string = 'Test string since get_status will only work with int'
        test_message = 'Invalid status code'

        # WHEN: get_status called
        string, message = pjlink._get_status(status=test_string)

        # THEN: Proper strings should have been returned
        self.assertEqual(string, -1, 'Should have returned -1 as a bad status check')
        self.assertEqual(message, test_message, 'Error message should have been returned')

    def test_projector_get_status_status(self):
        """
        Test to check returned information for status codes
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        test_string = 'S_NOT_CONNECTED'
        test_message = 'Not connected'

        # WHEN: get_status called
        string, message = pjlink._get_status(status=S_NOT_CONNECTED)

        # THEN: Proper strings should have been returned
        self.assertEqual(string, test_string, 'Code as string should have been returned')
        self.assertEqual(message, test_message, 'Description of code should have been returned')

    def test_projector_get_status_unknown(self):
        """
        Test to check returned information for unknown code
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        test_string = 999999
        test_message = 'Unknown status'

        # WHEN: get_status called
        string, message = pjlink._get_status(status=test_string)

        # THEN: Proper strings should have been returned
        self.assertEqual(string, test_string, 'Received code should have been returned')
        self.assertEqual(message, test_message, 'Unknown status string should have been returned')

    def test_projector_process_inf1(self):
        """
        Test saving INF1 data (manufacturer)
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.manufacturer = None
        test_data = 'TEst INformation MultiCase'

        # WHEN: process_inf called with test data
        pjlink.process_inf1(data=test_data)

        # THEN: Data should be saved
        self.assertEqual(pjlink.manufacturer, test_data, 'Test data should have been saved')

    def test_projector_process_inf2(self):
        """
        Test saving INF2 data (model)
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.model = None
        test_data = 'TEst moDEl MultiCase'

        # WHEN: process_inf called with test data
        pjlink.process_inf2(data=test_data)

        # THEN: Data should be saved
        self.assertEqual(pjlink.model, test_data, 'Test data should have been saved')

    def test_projector_process_info(self):
        """
        Test saving INFO data (other information)
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.other_info = None
        test_data = 'TEst ExtrANEous MultiCase INformatoin that MFGR might Set'

        # WHEN: process_inf called with test data
        pjlink.process_info(data=test_data)

        # THEN: Data should be saved
        self.assertEqual(pjlink.other_info, test_data, 'Test data should have been saved')

    @patch.object(pjlink_test, 'projectorUpdateIcons')
    def test_projector_process_avmt_bad_data(self, mock_UpdateIcons):
        """
        Test avmt bad data fail
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.shutter = True
        pjlink.mute = True

        # WHEN: Called with an invalid setting
        pjlink.process_avmt('36')

        # THEN: Shutter should be closed and mute should be True
        self.assertTrue(pjlink.shutter, 'Shutter should changed')
        self.assertTrue(pjlink.mute, 'Audio should not have changed')
        self.assertFalse(mock_UpdateIcons.emit.called, 'Update icons should NOT have been called')

    @patch.object(pjlink_test, 'projectorUpdateIcons')
    def test_projector_process_avmt_closed_muted(self, mock_UpdateIcons):
        """
        Test avmt status shutter closed and mute off
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.shutter = False
        pjlink.mute = False

        # WHEN: Called with setting shutter to closed and mute on
        pjlink.process_avmt('31')

        # THEN: Shutter should be closed and mute should be True
        self.assertTrue(pjlink.shutter, 'Shutter should have been set to closed')
        self.assertTrue(pjlink.mute, 'Audio should be muted')
        self.assertTrue(mock_UpdateIcons.emit.called, 'Update icons should have been called')

    @patch.object(pjlink_test, 'projectorUpdateIcons')
    def test_projector_process_avmt_shutter_closed(self, mock_UpdateIcons):
        """
        Test avmt status shutter closed and audio unchanged
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.shutter = False
        pjlink.mute = True

        # WHEN: Called with setting shutter closed and mute off
        pjlink.process_avmt('11')

        # THEN: Shutter should be True and mute should be False
        self.assertTrue(pjlink.shutter, 'Shutter should have been set to closed')
        self.assertTrue(pjlink.mute, 'Audio should not have changed')
        self.assertTrue(mock_UpdateIcons.emit.called, 'Update icons should have been called')

    @patch.object(pjlink_test, 'projectorUpdateIcons')
    def test_projector_process_avmt_audio_muted(self, mock_UpdateIcons):
        """
        Test avmt status shutter unchanged and mute on
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.shutter = True
        pjlink.mute = False

        # WHEN: Called with setting shutter closed and mute on
        pjlink.process_avmt('21')

        # THEN: Shutter should be closed and mute should be True
        self.assertTrue(pjlink.shutter, 'Shutter should not have changed')
        self.assertTrue(pjlink.mute, 'Audio should be off')
        self.assertTrue(mock_UpdateIcons.emit.called, 'Update icons should have been called')

    @patch.object(pjlink_test, 'projectorUpdateIcons')
    def test_projector_process_avmt_open_unmuted(self, mock_UpdateIcons):
        """
        Test avmt status shutter open and mute off
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.shutter = True
        pjlink.mute = True

        # WHEN: Called with setting shutter to closed and mute on
        pjlink.process_avmt('30')

        # THEN: Shutter should be closed and mute should be True
        self.assertFalse(pjlink.shutter, 'Shutter should have been set to open')
        self.assertFalse(pjlink.mute, 'Audio should be on')
        self.assertTrue(mock_UpdateIcons.emit.called, 'Update icons should have been called')

    def test_projector_process_clss_one(self):
        """
        Test class 1 sent from projector
        """
        # GIVEN: Test object
        pjlink = pjlink_test

        # WHEN: Process class response
        pjlink.process_clss('1')

        # THEN: Projector class should be set to 1
        self.assertEqual(pjlink.pjlink_class, '1',
                         'Projector should have set class=1')

    def test_projector_process_clss_two(self):
        """
        Test class 2 sent from projector
        """
        # GIVEN: Test object
        pjlink = pjlink_test

        # WHEN: Process class response
        pjlink.process_clss('2')

        # THEN: Projector class should be set to 1
        self.assertEqual(pjlink.pjlink_class, '2',
                         'Projector should have set class=2')

    def test_projector_process_clss_nonstandard_reply_optoma(self):
        """
        Bugfix 1550891: CLSS request returns non-standard reply with Optoma projector
        """
        # GIVEN: Test object
        pjlink = pjlink_test

        # WHEN: Process non-standard reply
        pjlink.process_clss('Class 1')

        # THEN: Projector class should be set with proper value
        self.assertEqual(pjlink.pjlink_class, '1',
                         'Non-standard class reply should have set class=1')

    def test_projector_process_clss_nonstandard_reply_benq(self):
        """
        Bugfix 1550891: CLSS request returns non-standard reply with BenQ projector
        """
        # GIVEN: Test object
        pjlink = pjlink_test

        # WHEN: Process non-standard reply
        pjlink.process_clss('Version2')

        # THEN: Projector class should be set with proper value
        # NOTE: At this time BenQ is Class 1, but we're trying a different value to verify
        self.assertEqual(pjlink.pjlink_class, '2',
                         'Non-standard class reply should have set class=2')

    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_process_clss_invalid_nan(self, mock_log):
        """
        Test CLSS reply has no class number
        """
        # GIVEN: Test object
        pjlink = pjlink_test

        # WHEN: Process invalid reply
        pjlink.process_clss('Z')
        log_text = "(127.0.0.1) NAN clss version reply 'Z' - defaulting to class '1'"

        # THEN: Projector class should be set with default value
        self.assertEqual(pjlink.pjlink_class, '1',
                         'Non-standard class reply should have set class=1')
        mock_log.error.assert_called_once_with(log_text)

    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_process_clss_invalid_no_version(self, mock_log):
        """
        Test CLSS reply has no class number
        """
        # GIVEN: Test object
        pjlink = pjlink_test

        # WHEN: Process invalid reply
        pjlink.process_clss('Invalid')
        log_text = "(127.0.0.1) No numbers found in class version reply 'Invalid' - defaulting to class '1'"

        # THEN: Projector class should be set with default value
        self.assertEqual(pjlink.pjlink_class, '1',
                         'Non-standard class reply should have set class=1')
        mock_log.error.assert_called_once_with(log_text)

    def test_projector_process_erst_all_ok(self):
        """
        Test test_projector_process_erst_all_ok
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        chk_test = PJLINK_ERST_STATUS['OK']
        chk_param = chk_test * len(PJLINK_ERST_POSITIONS)

        # WHEN: process_erst with no errors
        pjlink.process_erst(chk_param)

        # THEN: PJLink instance errors should be None
        self.assertIsNone(pjlink.projector_errors, 'projector_errors should have been set to None')

    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_process_erst_data_invalid_length(self, mock_log):
        """
        Test test_projector_process_erst_data_invalid_length
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.projector_errors = None
        log_text = "127.0.0.1) Invalid error status response '11111111': length != 6"

        # WHEN: process_erst called with invalid data (too many values
        pjlink.process_erst('11111111')

        # THEN: pjlink.projector_errors should be empty and warning logged
        self.assertIsNone(pjlink.projector_errors, 'There should be no errors')
        self.assertTrue(mock_log.warning.called, 'Warning should have been logged')
        mock_log.warning.assert_called_once_with(log_text)

    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_process_erst_data_invalid_nan(self, mock_log):
        """
        Test test_projector_process_erst_data_invalid_nan
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.projector_errors = None
        log_text = "(127.0.0.1) Invalid error status response '1111Z1'"

        # WHEN: process_erst called with invalid data (too many values
        pjlink.process_erst('1111Z1')

        # THEN: pjlink.projector_errors should be empty and warning logged
        self.assertIsNone(pjlink.projector_errors, 'There should be no errors')
        self.assertTrue(mock_log.warning.called, 'Warning should have been logged')
        mock_log.warning.assert_called_once_with(log_text)

    def test_projector_process_erst_all_warn(self):
        """
        Test test_projector_process_erst_all_warn
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        chk_test = PJLINK_ERST_STATUS[E_WARN]
        chk_string = ERROR_STRING[E_WARN]
        chk_param = chk_test * len(PJLINK_ERST_POSITIONS)

        # WHEN: process_erst with status set to WARN
        pjlink.process_erst(chk_param)

        # THEN: PJLink instance errors should match chk_value
        for chk in pjlink.projector_errors:
            self.assertEqual(pjlink.projector_errors[chk], chk_string,
                             "projector_errors['{chk}'] should have been set to {err}".format(chk=chk,
                                                                                              err=chk_string))

    def test_projector_process_erst_all_error(self):
        """
        Test test_projector_process_erst_all_error
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        chk_test = PJLINK_ERST_STATUS[E_ERROR]
        chk_string = ERROR_STRING[E_ERROR]
        chk_param = chk_test * len(PJLINK_ERST_POSITIONS)

        # WHEN: process_erst with status set to WARN
        pjlink.process_erst(chk_param)

        # THEN: PJLink instance errors should match chk_value
        for chk in pjlink.projector_errors:
            self.assertEqual(pjlink.projector_errors[chk], chk_string,
                             "projector_errors['{chk}'] should have been set to {err}".format(chk=chk,
                                                                                              err=chk_string))

    def test_projector_process_erst_warn_cover_only(self):
        """
        Test test_projector_process_erst_warn_cover_only
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        chk_test = PJLINK_ERST_STATUS[E_WARN]
        chk_string = ERROR_STRING[E_WARN]
        pos = PJLINK_ERST_DATA['COVER']
        build_chk = []
        for check in range(0, len(PJLINK_ERST_POSITIONS)):
            if check == pos:
                build_chk.append(chk_test)
            else:
                build_chk.append(PJLINK_ERST_STATUS['OK'])
        chk_param = ''.join(build_chk)

        # WHEN: process_erst with cover only set to WARN and all others set to OK
        pjlink.process_erst(chk_param)

        # THEN: Only COVER should have an error
        self.assertEqual(len(pjlink.projector_errors), 1, 'projector_errors should only have 1 error')
        self.assertTrue(('Cover' in pjlink.projector_errors), 'projector_errors should have an error for "Cover"')
        self.assertEqual(pjlink.projector_errors['Cover'],
                         chk_string,
                         'projector_errors["Cover"] should have error "{err}"'.format(err=chk_string))

    def test_projector_process_inpt(self):
        """
        Test input source status shows current input
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.source = '0'

        # WHEN: Called with input source
        pjlink.process_inpt('1')

        # THEN: Input selected should reflect current input
        self.assertEqual(pjlink.source, '1', 'Input source should be set to "1"')

    @patch.object(pjlink_test, 'projectorUpdateIcons')
    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_process_inst(self, mock_log, mock_UpdateIcons):
        """
        Test saving video source available information
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.source_available = []
        test_data = '21 10 30 31 11 20'
        test_saved = ['10', '11', '20', '21', '30', '31']
        log_data = '(127.0.0.1) Setting projector sources_available to ' \
            '"[\'10\', \'11\', \'20\', \'21\', \'30\', \'31\']"'
        mock_UpdateIcons.reset_mock()
        mock_log.reset_mock()

        # WHEN: process_inst called with test data
        pjlink.process_inst(data=test_data)

        # THEN: Data should have been sorted and saved properly
        self.assertEqual(pjlink.source_available, test_saved, "Sources should have been sorted and saved")
        mock_log.debug.assert_called_once_with(log_data)
        self.assertTrue(mock_UpdateIcons.emit.called, 'Update Icons should have been called')

    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_process_lamp_invalid(self, mock_log):
        """
        Test status multiple lamp on/off and hours
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.lamp = [{'Hours': 00000, 'On': True},
                       {'Hours': 11111, 'On': False}]
        log_data = '(127.0.0.1) process_lamp(): Invalid data "11111 1 22222 0 333A3 1"'

        # WHEN: Call process_command with invalid lamp data
        pjlink.process_lamp('11111 1 22222 0 333A3 1')

        # THEN: lamps should not have changed
        self.assertEqual(len(pjlink.lamp), 2,
                         'Projector should have kept 2 lamps specified')
        self.assertEqual(pjlink.lamp[0]['On'], True,
                         'Lamp 1 power status should have been set to TRUE')
        self.assertEqual(pjlink.lamp[0]['Hours'], 00000,
                         'Lamp 1 hours should have been left at 00000')
        self.assertEqual(pjlink.lamp[1]['On'], False,
                         'Lamp 2 power status should have been set to FALSE')
        self.assertEqual(pjlink.lamp[1]['Hours'], 11111,
                         'Lamp 2 hours should have been left at 11111')
        mock_log.warning.assert_called_once_with(log_data)

    def test_projector_process_lamp_multiple(self):
        """
        Test status multiple lamp on/off and hours
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.lamps = []

        # WHEN: Call process_command with lamp data
        pjlink.process_lamp('11111 1 22222 0 33333 1')

        # THEN: Lamp should have been set with proper lamp status
        self.assertEqual(len(pjlink.lamp), 3,
                         'Projector should have 3 lamps specified')
        self.assertEqual(pjlink.lamp[0]['On'], True,
                         'Lamp 1 power status should have been set to TRUE')
        self.assertEqual(pjlink.lamp[0]['Hours'], 11111,
                         'Lamp 1 hours should have been set to 11111')
        self.assertEqual(pjlink.lamp[1]['On'], False,
                         'Lamp 2 power status should have been set to FALSE')
        self.assertEqual(pjlink.lamp[1]['Hours'], 22222,
                         'Lamp 2 hours should have been set to 22222')
        self.assertEqual(pjlink.lamp[2]['On'], True,
                         'Lamp 3 power status should have been set to TRUE')
        self.assertEqual(pjlink.lamp[2]['Hours'], 33333,
                         'Lamp 3 hours should have been set to 33333')

    def test_projector_process_lamp_single(self):
        """
        Test status lamp on/off and hours
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.lamps = []

        # WHEN: Call process_command with lamp data
        pjlink.process_lamp('22222 1')

        # THEN: Lamp should have been set with status=ON and hours=22222
        self.assertEqual(pjlink.lamp[0]['On'], True,
                         'Lamp power status should have been set to TRUE')
        self.assertEqual(pjlink.lamp[0]['Hours'], 22222,
                         'Lamp hours should have been set to 22222')

    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_process_name(self, mock_log):
        """
        Test saving NAME data from projector
        """
        # GIVEN: Test data
        pjlink = pjlink_test
        test_data = "Some Name the End-User Set IN Projector"
        test_log = '(127.0.0.1) Setting projector PJLink name to "Some Name the End-User Set IN Projector"'
        mock_log.reset_mock()

        # WHEN: process_name called with test data
        pjlink.process_name(data=test_data)

        # THEN: name should be set and logged
        self.assertEqual(pjlink.pjlink_name, test_data, 'Name test data should have been saved')
        mock_log.debug.assert_called_once_with(test_log)

    @patch.object(pjlink_test, 'projectorUpdateIcons')
    @patch.object(pjlink_test, 'send_command')
    @patch.object(pjlink_test, 'change_status')
    def test_projector_process_powr_on(self,
                                       mock_change_status,
                                       mock_send_command,
                                       mock_UpdateIcons):
        """
        Test status power to ON
        """
        # GIVEN: Test object and preset
        pjlink = pjlink_test
        pjlink.power = S_STANDBY
        test_data = PJLINK_POWR_STATUS[S_ON]

        # WHEN: Call process_command with turn power on command
        pjlink.process_command(cmd='POWR', data=test_data)

        # THEN: Power should be set to ON
        self.assertEqual(pjlink.power, S_ON, 'Power should have been set to ON')
        mock_send_command.assert_called_once_with('INST')
        mock_change_status.assert_called_once_with(PJLINK_POWR_STATUS[test_data])
        self.assertEqual(mock_UpdateIcons.emit.called, True, 'projectorUpdateIcons should have been called')

    @patch.object(pjlink_test, 'projectorUpdateIcons')
    @patch.object(pjlink_test, 'send_command')
    @patch.object(pjlink_test, 'change_status')
    def test_projector_process_powr_invalid(self,
                                            mock_change_status,
                                            mock_send_command,
                                            mock_UpdateIcons):
        """
        Test process_powr invalid call
        """
        # GIVEN: Test object and preset
        pjlink = pjlink_test
        pjlink.power = S_STANDBY
        test_data = '99'

        # WHEN: Call process_command with turn power on command
        pjlink.process_command(cmd='POWR', data=test_data)

        # THEN: Power should be set to ON
        self.assertEqual(pjlink.power, S_STANDBY, 'Power should not have changed')
        self.assertFalse(mock_change_status.called, 'Change status should not have been called')
        self.assertFalse(mock_send_command.called, 'send_command("INST") should not have been called')
        self.assertFalse(mock_UpdateIcons.emit.called, 'projectorUpdateIcons should not have been called')

    @patch.object(pjlink_test, 'projectorUpdateIcons')
    @patch.object(pjlink_test, 'send_command')
    @patch.object(pjlink_test, 'change_status')
    def test_projector_process_powr_off(self,
                                        mock_change_status,
                                        mock_send_command,
                                        mock_UpdateIcons):
        """
        Test status power to STANDBY
        """
        # GIVEN: Test object and preset
        pjlink = pjlink_test
        pjlink.power = S_ON
        test_data = PJLINK_POWR_STATUS[S_STANDBY]

        # WHEN: Call process_command with turn power on command
        pjlink.process_command(cmd='POWR', data=test_data)

        # THEN: Power should be set to STANDBY
        self.assertEqual(pjlink.power, S_STANDBY, 'Power should have been set to STANDBY')
        self.assertEqual(mock_UpdateIcons.emit.called, True, 'projectorUpdateIcons should have been called')
        mock_change_status.assert_called_once_with(PJLINK_POWR_STATUS[test_data])
        self.assertFalse(mock_send_command.called, "send_command['INST'] should not have been called")

    def test_projector_process_rfil_save(self):
        """
        Test saving filter type
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.model_filter = None
        filter_model = 'Filter Type Test'

        # WHEN: Filter model is received
        pjlink.process_rfil(data=filter_model)

        # THEN: Filter model number should be saved
        self.assertEqual(pjlink.model_filter, filter_model, 'Filter type should have been saved')

    def test_projector_process_rfil_nosave(self):
        """
        Test saving filter type previously saved
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.model_filter = 'Old filter type'
        filter_model = 'Filter Type Test'

        # WHEN: Filter model is received
        pjlink.process_rfil(data=filter_model)

        # THEN: Filter model number should be saved
        self.assertNotEquals(pjlink.model_filter, filter_model, 'Filter type should NOT have been saved')

    def test_projector_process_rlmp_save(self):
        """
        Test saving lamp type
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.model_lamp = None
        lamp_model = 'Lamp Type Test'

        # WHEN: Filter model is received
        pjlink.process_rlmp(data=lamp_model)

        # THEN: Filter model number should be saved
        self.assertEqual(pjlink.model_lamp, lamp_model, 'Lamp type should have been saved')

    def test_projector_process_rlmp_nosave(self):
        """
        Test saving lamp type previously saved
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.model_lamp = 'Old lamp type'
        lamp_model = 'Filter Type Test'

        # WHEN: Filter model is received
        pjlink.process_rlmp(data=lamp_model)

        # THEN: Filter model number should be saved
        self.assertNotEquals(pjlink.model_lamp, lamp_model, 'Lamp type should NOT have been saved')

    def test_projector_process_snum_set(self):
        """
        Test saving serial number from projector
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.serial_no = None
        test_number = 'Test Serial Number'

        # WHEN: No serial number is set and we receive serial number command
        pjlink.process_snum(data=test_number)

        # THEN: Serial number should be set
        self.assertEqual(pjlink.serial_no, test_number,
                         'Projector serial number should have been set')

    def test_projector_process_snum_different(self):
        """
        Test projector serial number different than saved serial number
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.serial_no = 'Previous serial number'
        test_number = 'Test Serial Number'

        # WHEN: No serial number is set and we receive serial number command
        pjlink.process_snum(data=test_number)

        # THEN: Serial number should be set
        self.assertNotEquals(pjlink.serial_no, test_number,
                             'Projector serial number should NOT have been set')

    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_process_sver(self, mock_log):
        """
        Test invalid software version information - too long
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.sw_version = None
        pjlink.sw_version_received = None
        test_data = 'Test 1 Subtest 1'
        test_log = "(127.0.0.1) Setting projector software version to 'Test 1 Subtest 1'"
        mock_log.reset_mock()

        # WHEN: process_sver called with invalid data
        pjlink.process_sver(data=test_data)

        # THEN: Version information should not change
        self.assertEqual(pjlink.sw_version, test_data, 'Software version should have been updated')
        self.assertIsNone(pjlink.sw_version_received, 'Received software version should not have changed')
        mock_log.debug.assert_called_once_with(test_log)

    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_process_sver_changed(self, mock_log):
        """
        Test invalid software version information - Received different than saved
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        test_data_new = 'Test 1 Subtest 2'
        test_data_old = 'Test 1 Subtest 1'
        pjlink.sw_version = test_data_old
        pjlink.sw_version_received = None
        test_log = '(127.0.0.1) Saving new serial number as sw_version_received'
        mock_log.reset_mock()

        # WHEN: process_sver called with invalid data
        pjlink.process_sver(data=test_data_new)

        # THEN: Version information should not change
        self.assertEqual(pjlink.sw_version, test_data_old, 'Software version should not have been updated')
        self.assertEqual(pjlink.sw_version_received, test_data_new,
                         'Received software version should have been changed')
        self.assertEqual(mock_log.warning.call_count, 4, 'log.warn should have been called 4 times')
        # There was 4 calls, but only the last one is checked with this method
        mock_log.warning.assert_called_with(test_log)

    @patch.object(openlp.core.lib.projector.pjlink, 'log')
    def test_projector_process_sver_invalid(self, mock_log):
        """
        Test invalid software version information - too long
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.sw_version = None
        pjlink.sw_version_received = None
        test_data = 'This is a test software version line that is too long based on PJLink version 2 specs'
        test_log = "Invalid software version - too long"
        mock_log.reset_mock()

        # WHEN: process_sver called with invalid data
        pjlink.process_sver(data=test_data)

        # THEN: Version information should not change
        self.assertIsNone(pjlink.sw_version, 'Software version should not have changed')
        self.assertIsNone(pjlink.sw_version_received, 'Received software version should not have changed')
        mock_log.warning.assert_called_once_with(test_log)

    def test_projector_reset_information(self):
        """
        Test reset_information() resets all information and stops timers
        """
        # GIVEN: Test object and test data
        pjlink = pjlink_test
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
        with patch.object(pjlink, 'timer') as mock_timer:
            with patch.object(pjlink, 'socket_timer') as mock_socket_timer:
                pjlink.reset_information()

        # THEN: All information should be reset and timers stopped
        self.assertEqual(pjlink.power, S_OFF, 'Projector power should be OFF')
        self.assertIsNone(pjlink.pjlink_name, 'Projector pjlink_name should be None')
        self.assertIsNone(pjlink.manufacturer, 'Projector manufacturer should be None')
        self.assertIsNone(pjlink.model, 'Projector model should be None')
        self.assertIsNone(pjlink.shutter, 'Projector shutter should be None')
        self.assertIsNone(pjlink.mute, 'Projector shuttter should be None')
        self.assertIsNone(pjlink.lamp, 'Projector lamp should be None')
        self.assertIsNone(pjlink.fan, 'Projector fan should be None')
        self.assertIsNone(pjlink.source_available, 'Projector source_available should be None')
        self.assertIsNone(pjlink.source, 'Projector source should be None')
        self.assertIsNone(pjlink.other_info, 'Projector other_info should be None')
        self.assertEqual(pjlink.send_queue, [], 'Projector send_queue should be an empty list')
        self.assertFalse(pjlink.send_busy, 'Projector send_busy should be False')
        self.assertTrue(mock_timer.stop.called, 'Projector timer.stop()  should have been called')
        self.assertTrue(mock_socket_timer.stop.called, 'Projector socket_timer.stop() should have been called')
