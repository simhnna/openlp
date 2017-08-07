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
from unittest.mock import patch, MagicMock

from openlp.core.lib.projector.pjlink import PJLink
from openlp.core.lib.projector.constants import PJLINK_ERST_STATUS, PJLINK_POWR_STATUS, \
    S_OFF, S_STANDBY, S_ON

from tests.resources.projector.data import TEST_PIN

pjlink_test = PJLink(name='test', ip='127.0.0.1', pin=TEST_PIN, no_poll=True)

# ERST status codes
ERST_OK, ERST_WARN, ERST_ERR = '0', '1', '2'


class TestPJLinkCommands(TestCase):
    """
    Tests for the PJLink module
    """
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
        self.assertTrue(pjlink.mute, 'Audio should be off')

    @patch.object(pjlink_test, 'projectorUpdateIcons')
    def test_projector_process_avmt_shutter_closed(self, mock_projectorReceivedData):
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
        self.assertTrue(pjlink.mute, 'Audio should not have changed')

    @patch.object(pjlink_test, 'projectorUpdateIcons')
    def test_projector_process_avmt_audio_muted(self, mock_projectorReceivedData):
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
        self.assertTrue(pjlink.shutter, 'Shutter should not have changed')
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
                         'Projector should have returned class=1')

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
                         'Projector should have returned class=2')

    def test_projector_process_clss_nonstandard_reply(self):
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

    def test_projector_process_erst_all_ok(self):
        """
        Test test_projector_process_erst_all_ok
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        chk_test = ERST_OK

        # WHEN: process_erst with no errors
        pjlink.process_erst('{fan}{lamp}{temp}{cover}{filter}{other}'.format(fan=chk_test,
                                                                             lamp=chk_test,
                                                                             temp=chk_test,
                                                                             cover=chk_test,
                                                                             filter=chk_test,
                                                                             other=chk_test))

        # PJLink instance errors should be None
        self.assertIsNone(pjlink.projector_errors, 'projector_errors should have been set to None')

    def test_projector_process_erst_all_warn(self):
        """
        Test test_projector_process_erst_all_warn
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        chk_test = ERST_WARN
        chk_code = PJLINK_ERST_STATUS[chk_test]
        chk_value = {'Fan': chk_code,
                     'Lamp': chk_code,
                     'Temperature': chk_code,
                     'Cover': chk_code,
                     'Filter': chk_code,
                     'Other': chk_code
                     }

        # WHEN: process_erst with status set to WARN
        pjlink.process_erst('{fan}{lamp}{temp}{cover}{filter}{other}'.format(fan=chk_test,
                                                                             lamp=chk_test,
                                                                             temp=chk_test,
                                                                             cover=chk_test,
                                                                             filter=chk_test,
                                                                             other=chk_test))

        # PJLink instance errors should match chk_value
        self.assertEqual(pjlink.projector_errors, chk_value,
                         'projector_errors should have been set to all {err}'.format(err=chk_code))

    def test_projector_process_erst_all_error(self):
        """
        Test test_projector_process_erst_all_error
        """
        # GIVEN: Test object
        pjlink = pjlink_test
        chk_test = ERST_ERR
        chk_code = PJLINK_ERST_STATUS[chk_test]
        chk_value = {'Fan': chk_code,
                     'Lamp': chk_code,
                     'Temperature': chk_code,
                     'Cover': chk_code,
                     'Filter': chk_code,
                     'Other': chk_code
                     }

        # WHEN: process_erst with status set to ERROR
        pjlink.process_erst('{fan}{lamp}{temp}{cover}{filter}{other}'.format(fan=chk_test,
                                                                             lamp=chk_test,
                                                                             temp=chk_test,
                                                                             cover=chk_test,
                                                                             filter=chk_test,
                                                                             other=chk_test))

        # PJLink instance errors should be set to chk_value
        self.assertEqual(pjlink.projector_errors, chk_value,
                         'projector_errors should have been set to all {err}'.format(err=chk_code))

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

    @patch.object(pjlink_test, 'projectorReceivedData')
    def test_projector_process_lamp_single(self, mock_projectorReceivedData):
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
    def test_projector_process_lamp_multiple(self, mock_projectorReceivedData):
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
    def test_projector_process_powr_on(self,
                                       mock_change_status,
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
    def test_projector_process_powr_off(self,
                                        mock_change_status,
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
