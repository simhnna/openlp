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
Package to test the openlp.core.lib.projector.pjlink1 package.
"""
from unittest import TestCase
from unittest.mock import call, patch, MagicMock

from openlp.core.lib.projector.pjlink1 import PJLink
from openlp.core.lib.projector.constants import E_PARAMETER, ERROR_STRING, S_OFF, S_STANDBY, S_ON, \
    PJLINK_POWR_STATUS, S_CONNECTED

from tests.resources.projector.data import TEST_PIN, TEST_SALT, TEST_CONNECT_AUTHENTICATE, TEST_HASH

pjlink_test = PJLink(name='test', ip='127.0.0.1', pin=TEST_PIN, no_poll=True)


class TestPJLink(TestCase):
    """
    Tests for the PJLink module
    """
    @patch.object(pjlink_test, 'readyRead')
    @patch.object(pjlink_test, 'send_command')
    @patch.object(pjlink_test, 'waitForReadyRead')
    @patch('openlp.core.common.qmd5_hash')
    def test_authenticated_connection_call(self, mock_qmd5_hash, mock_waitForReadyRead, mock_send_command,
                                           mock_readyRead):
        """
        Ticket 92187: Fix for projector connect with PJLink authentication exception.
        """
        # GIVEN: Test object
        pjlink = pjlink_test

        # WHEN: Calling check_login with authentication request:
        pjlink.check_login(data=TEST_CONNECT_AUTHENTICATE)

        # THEN: Should have called qmd5_hash
        self.assertTrue(mock_qmd5_hash.called_with(TEST_SALT,
                                                   "Connection request should have been called with TEST_SALT"))
        self.assertTrue(mock_qmd5_hash.called_with(TEST_PIN,
                                                   "Connection request should have been called with TEST_PIN"))

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

    def test_projector_clss_one(self):
        """
        Test class 1 sent from projector
        """
        # GIVEN: Test object
        pjlink = pjlink_test

        # WHEN: Process class response
        pjlink.process_clss('1')

        # THEN: Projector class should be set to 1
        self.assertEqual(pjlink.pjlink_class, '1',
                         'Projector should have returned class=1')

    def test_projector_clss_two(self):
        """
        Test class 2 sent from projector
        """
        # GIVEN: Test object
        pjlink = pjlink_test

        # WHEN: Process class response
        pjlink.process_clss('2')

        # THEN: Projector class should be set to 1
        self.assertEqual(pjlink.pjlink_class, '2',
                         'Projector should have returned class=2')

    def test_bug_1550891_non_standard_class_reply(self):
        """
        Bugfix 1550891: CLSS request returns non-standard reply
        """
        # GIVEN: Test object
        pjlink = pjlink_test

        # WHEN: Process non-standard reply
        pjlink.process_clss('Class 1')

        # THEN: Projector class should be set with proper value
        self.assertEqual(pjlink.pjlink_class, '1',
                         'Non-standard class reply should have set class=1')

    @patch.object(pjlink_test, 'change_status')
    def test_status_change(self, mock_change_status):
        """
        Test process_command call with ERR2 (Parameter) status
        """
        # GIVEN: Test object
        pjlink = pjlink_test

        # WHEN: process_command is called with "ERR2" status from projector
        pjlink.process_command('POWR', 'ERR2')

        # THEN: change_status should have called change_status with E_UNDEFINED
        #       as first parameter
        mock_change_status.called_with(E_PARAMETER,
                                       'change_status should have been called with "{}"'.format(
                                           ERROR_STRING[E_PARAMETER]))

    @patch.object(pjlink_test, 'process_inpt')
    def test_projector_return_ok(self, mock_process_inpt):
        """
        Test projector calls process_inpt command when process_command is called with INPT option
        """
        # GIVEN: Test object
        pjlink = pjlink_test

        # WHEN: process_command is called with INST command and 31 input:
        pjlink.process_command('INPT', '31')

        # THEN: process_inpt method should have been called with 31
        mock_process_inpt.called_with('31',
                                      "process_inpt should have been called with 31")

    @patch.object(pjlink_test, 'projectorReceivedData')
    def test_projector_process_lamp(self, mock_projectorReceivedData):
        """
        Test status lamp on/off and hours
        """
        # GIVEN: Test object
        pjlink = pjlink_test

        # WHEN: Call process_command with lamp data
        pjlink.process_command('LAMP', '22222 1')

        # THEN: Lamp should have been set with status=ON and hours=22222
        self.assertEqual(pjlink.lamp[0]['On'], True,
                         'Lamp power status should have been set to TRUE')
        self.assertEqual(pjlink.lamp[0]['Hours'], 22222,
                         'Lamp hours should have been set to 22222')

    @patch.object(pjlink_test, 'projectorReceivedData')
    def test_projector_process_multiple_lamp(self, mock_projectorReceivedData):
        """
        Test status multiple lamp on/off and hours
        """
        # GIVEN: Test object
        pjlink = pjlink_test

        # WHEN: Call process_command with lamp data
        pjlink.process_command('LAMP', '11111 1 22222 0 33333 1')

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

    @patch.object(pjlink_test, 'projectorReceivedData')
    @patch.object(pjlink_test, 'projectorUpdateIcons')
    @patch.object(pjlink_test, 'send_command')
    @patch.object(pjlink_test, 'change_status')
    def test_projector_process_power_on(self, mock_change_status,
                                        mock_send_command,
                                        mock_UpdateIcons,
                                        mock_ReceivedData):
        """
        Test status power to ON
        """
        # GIVEN: Test object and preset
        pjlink = pjlink_test
        pjlink.power = S_STANDBY

        # WHEN: Call process_command with turn power on command
        pjlink.process_command('POWR', PJLINK_POWR_STATUS[S_ON])

        # THEN: Power should be set to ON
        self.assertEqual(pjlink.power, S_ON, 'Power should have been set to ON')
        mock_send_command.assert_called_once_with('INST')
        self.assertEqual(mock_UpdateIcons.emit.called, True, 'projectorUpdateIcons should have been called')

    @patch.object(pjlink_test, 'projectorReceivedData')
    @patch.object(pjlink_test, 'projectorUpdateIcons')
    @patch.object(pjlink_test, 'send_command')
    @patch.object(pjlink_test, 'change_status')
    def test_projector_process_power_off(self, mock_change_status,
                                         mock_send_command,
                                         mock_UpdateIcons,
                                         mock_ReceivedData):
        """
        Test status power to STANDBY
        """
        # GIVEN: Test object and preset
        pjlink = pjlink_test
        pjlink.power = S_ON

        # WHEN: Call process_command with turn power on command
        pjlink.process_command('POWR', PJLINK_POWR_STATUS[S_STANDBY])

        # THEN: Power should be set to STANDBY
        self.assertEqual(pjlink.power, S_STANDBY, 'Power should have been set to STANDBY')
        self.assertEqual(mock_send_command.called, False, 'send_command should not have been called')
        self.assertEqual(mock_UpdateIcons.emit.called, True, 'projectorUpdateIcons should have been called')

    @patch.object(pjlink_test, 'projectorUpdateIcons')
    def test_projector_process_avmt_closed_unmuted(self, mock_projectorReceivedData):
        """
        Test avmt status shutter closed and audio muted
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.shutter = False
        pjlink.mute = True

        # WHEN: Called with setting shutter closed and mute off
        pjlink.process_avmt('11')

        # THEN: Shutter should be True and mute should be False
        self.assertTrue(pjlink.shutter, 'Shutter should have been set to closed')
        self.assertFalse(pjlink.mute, 'Audio should be off')

    @patch.object(pjlink_test, 'projectorUpdateIcons')
    def test_projector_process_avmt_open_muted(self, mock_projectorReceivedData):
        """
        Test avmt status shutter open and mute on
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        pjlink.shutter = True
        pjlink.mute = False

        # WHEN: Called with setting shutter closed and mute on
        pjlink.process_avmt('21')

        # THEN: Shutter should be closed and mute should be True
        self.assertFalse(pjlink.shutter, 'Shutter should have been set to closed')
        self.assertTrue(pjlink.mute, 'Audio should be off')

    @patch.object(pjlink_test, 'projectorUpdateIcons')
    def test_projector_process_avmt_open_unmuted(self, mock_projectorReceivedData):
        """
        Test avmt status shutter open and mute off off
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

    @patch.object(pjlink_test, 'projectorUpdateIcons')
    def test_projector_process_avmt_closed_muted(self, mock_projectorReceivedData):
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
        self.assertTrue(pjlink.mute, 'Audio should be on')

    def test_projector_process_input(self):
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
        pjlink.timer = MagicMock()
        pjlink.socket_timer = MagicMock()

        # WHEN: reset_information() is called
        with patch.object(pjlink.timer, 'stop') as mock_timer:
            with patch.object(pjlink.socket_timer, 'stop') as mock_socket_timer:
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
        self.assertTrue(mock_timer.called, 'Projector timer.stop()  should have been called')
        self.assertTrue(mock_socket_timer.called, 'Projector socket_timer.stop() should have been called')

    @patch.object(pjlink_test, 'send_command')
    @patch.object(pjlink_test, 'waitForReadyRead')
    @patch.object(pjlink_test, 'projectorAuthentication')
    @patch.object(pjlink_test, 'timer')
    @patch.object(pjlink_test, 'socket_timer')
    def test_bug_1593882_no_pin_authenticated_connection(self, mock_socket_timer,
                                                         mock_timer,
                                                         mock_authentication,
                                                         mock_ready_read,
                                                         mock_send_command):
        """
        Test bug 1593882 no pin and authenticated request exception
        """
        # GIVEN: Test object and mocks
        pjlink = pjlink_test
        pjlink.pin = None
        mock_ready_read.return_value = True

        # WHEN: call with authentication request and pin not set
        pjlink.check_login(data=TEST_CONNECT_AUTHENTICATE)

        # THEN: 'No Authentication' signal should have been sent
        mock_authentication.emit.assert_called_with(pjlink.ip)

    @patch.object(pjlink_test, 'waitForReadyRead')
    @patch.object(pjlink_test, 'state')
    @patch.object(pjlink_test, '_send_command')
    @patch.object(pjlink_test, 'timer')
    @patch.object(pjlink_test, 'socket_timer')
    def test_bug_1593883_pjlink_authentication(self, mock_socket_timer,
                                               mock_timer,
                                               mock_send_command,
                                               mock_state,
                                               mock_waitForReadyRead):
        """
        Test bugfix 1593883 pjlink authentication
        """
        # GIVEN: Test object and data
        pjlink = pjlink_test
        pjlink.pin = TEST_PIN
        mock_state.return_value = pjlink.ConnectedState
        mock_waitForReadyRead.return_value = True

        # WHEN: Athenticated connection is called
        pjlink.check_login(data=TEST_CONNECT_AUTHENTICATE)

        # THEN: send_command should have the proper authentication
        self.assertEqual("{test}".format(test=mock_send_command.call_args),
                         "call(data='{hash}%1CLSS ?\\r')".format(hash=TEST_HASH))

    @patch.object(pjlink_test, 'disconnect_from_host')
    def socket_abort_test(self, mock_disconnect):
        """
        Test PJLink.socket_abort calls disconnect_from_host
        """
        # GIVEN: Test object
        pjlink = pjlink_test

        # WHEN: Calling socket_abort
        pjlink.socket_abort()

        # THEN: disconnect_from_host should be called
        self.assertTrue(mock_disconnect.called, 'Should have called disconnect_from_host')

    def poll_loop_not_connected_test(self):
        """
        Test PJLink.poll_loop not connected return
        """
        # GIVEN: Test object and mocks
        pjlink = pjlink_test
        pjlink.state = MagicMock()
        pjlink.timer = MagicMock()
        pjlink.state.return_value = False
        pjlink.ConnectedState = True

        # WHEN: PJLink.poll_loop called
        pjlink.poll_loop()

        # THEN: poll_loop should exit without calling any other method
        self.assertFalse(pjlink.timer.called, 'Should have returned without calling any other method')

    @patch.object(pjlink_test, 'send_command')
    def poll_loop_start_test(self, mock_send_command):
        """
        Test PJLink.poll_loop makes correct calls
        """
        # GIVEN: test object and test data
        pjlink = pjlink_test
        pjlink.state = MagicMock()
        pjlink.timer = MagicMock()
        pjlink.timer.interval = MagicMock()
        pjlink.timer.setInterval = MagicMock()
        pjlink.timer.start = MagicMock()
        pjlink.poll_time = 20
        pjlink.power = S_ON
        pjlink.source_available = None
        pjlink.other_info = None
        pjlink.manufacturer = None
        pjlink.model = None
        pjlink.pjlink_name = None
        pjlink.ConnectedState = S_CONNECTED
        pjlink.timer.interval.return_value = 10
        pjlink.state.return_value = S_CONNECTED
        call_list = [
            call('POWR', queue=True),
            call('ERST', queue=True),
            call('LAMP', queue=True),
            call('AVMT', queue=True),
            call('INPT', queue=True),
            call('INST', queue=True),
            call('INFO', queue=True),
            call('INF1', queue=True),
            call('INF2', queue=True),
            call('NAME', queue=True),
        ]

        # WHEN: PJLink.poll_loop is called
        pjlink.poll_loop()

        # THEN: proper calls were made to retrieve projector data
        # First, call to update the timer with the next interval
        self.assertTrue(pjlink.timer.setInterval.called, 'Should have updated the timer')
        # Next, should have called the timer to start
        self.assertTrue(pjlink.timer.start.called, 'Should have started the timer')
        # Finally, should have called send_command with a list of projetctor status checks
        mock_send_command.assert_has_calls(call_list, 'Should have queued projector queries')
