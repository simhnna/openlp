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
from unittest.mock import patch, call

import openlp.core.projectors.pjlink
from openlp.core.projectors.constants import S_CONNECTED, S_OFF, S_ON
from openlp.core.projectors.db import Projector
from openlp.core.projectors.pjlink import PJLink
from tests.resources.projector.data import TEST_HASH, TEST_PIN, TEST_SALT, TEST1_DATA


class TestPJLinkCommands(TestCase):
    """
    Tests for the PJLinkCommands class part 2
    """
    def test_projector_reset_information(self):
        """
        Test reset_information() resets all information and stops timers
        """
        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            log_debug_calls = [call('({ip}): Calling poll_timer.stop()'.format(ip=pjlink.name)),
                               call('({ip}): Calling socket_timer.stop()'.format(ip=pjlink.name))]
            # timer and socket_timer not available until instantiation, so mock here
            with patch.object(pjlink, 'socket_timer') as mock_socket_timer, \
                    patch.object(pjlink, 'poll_timer') as mock_timer:

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

    def test_process_pjlink_normal(self):
        """
        Test initial connection prompt with no authentication
        """
        # GIVEN: Initial mocks and data
        mock_log = patch.object(openlp.core.projectors.pjlink, "log").start()
        mock_disconnect_from_host = patch('openlp.core.projectors.pjlink.PJLink.disconnect_from_host').start()
        mock_send_command = patch('openlp.core.projectors.pjlink.PJLink.send_command').start()
        mock_readyRead = patch('openlp.core.projectors.pjlink.PJLink.readyRead').start()
        mock_change_status = patch('openlp.core.projectors.pjlink.PJLink.change_status').start()

        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.pin = None
        log_check = [call('({ip}) process_pjlink(): Sending "CLSS" initial command'.format(ip=pjlink.name)), ]

        # WHEN: process_pjlink called with no authentication required
        pjlink.process_pjlink(data="0")

        # THEN: proper processing should have occured
        mock_log.debug.has_calls(log_check)
        mock_disconnect_from_host.assert_not_called()
        assert 1 == mock_readyRead.connect.call_count, 'Should have only been called once'
        mock_change_status.assert_called_once_with(S_CONNECTED)
        mock_send_command.assert_called_with(cmd='CLSS', priority=True, salt=None)

    def test_process_pjlink_authenticate(self):
        """
        Test initial connection prompt with authentication
        """
        # GIVEN: Initial mocks and data
        mock_log = patch.object(openlp.core.projectors.pjlink, "log").start()
        mock_disconnect_from_host = patch('openlp.core.projectors.pjlink.PJLink.disconnect_from_host').start()
        mock_send_command = patch('openlp.core.projectors.pjlink.PJLink.send_command').start()
        mock_readyRead = patch('openlp.core.projectors.pjlink.PJLink.readyRead').start()
        mock_change_status = patch('openlp.core.projectors.pjlink.PJLink.change_status').start()

        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.pin = TEST_PIN
        log_check = [call('({ip}) process_pjlink(): Sending "CLSS" initial command'.format(ip=pjlink.name)), ]

        # WHEN: process_pjlink called with no authentication required
        pjlink.process_pjlink(data='1 {salt}'.format(salt=TEST_SALT))

        # THEN: proper processing should have occured
        mock_log.debug.has_calls(log_check)
        mock_disconnect_from_host.assert_not_called()
        assert 1 == mock_readyRead.connect.call_count, 'Should have only been called once'
        mock_change_status.assert_called_once_with(S_CONNECTED)
        mock_send_command.assert_called_with(cmd='CLSS', priority=True, salt=TEST_HASH)

    def test_process_pjlink_normal_pin_set_error(self):
        """
        Test process_pjlinnk called with no authentication but pin is set
        """
        # GIVEN: Initial mocks and data
        mock_log = patch.object(openlp.core.projectors.pjlink, 'log').start()
        mock_disconnect_from_host = patch('openlp.core.projectors.pjlink.PJLink.disconnect_from_host').start()
        mock_send_command = patch('openlp.core.projectors.pjlink.PJLink.send_command').start()

        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.pin = TEST_PIN
        log_check = [call('({ip}) Normal connection but PIN set - aborting'.format(ip=pjlink.name)), ]

        # WHEN: process_pjlink called with invalid authentication scheme
        pjlink.process_pjlink(data='0')

        # THEN: Proper calls should be made
        mock_log.error.assert_has_calls(log_check)
        assert 1 == mock_disconnect_from_host.call_count, 'Should have only been called once'
        mock_send_command.assert_not_called()

    def test_process_pjlink_normal_with_salt_error(self):
        """
        Test process_pjlinnk called with no authentication but pin is set
        """
        # GIVEN: Initial mocks and data
        mock_log = patch.object(openlp.core.projectors.pjlink, 'log').start()
        mock_disconnect_from_host = patch('openlp.core.projectors.pjlink.PJLink.disconnect_from_host').start()
        mock_send_command = patch('openlp.core.projectors.pjlink.PJLink.send_command').start()

        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.pin = TEST_PIN
        log_check = [call('({ip}) Normal connection with extra information - aborting'.format(ip=pjlink.name)), ]

        # WHEN: process_pjlink called with invalid authentication scheme
        pjlink.process_pjlink(data='0 {salt}'.format(salt=TEST_SALT))

        # THEN: Proper calls should be made
        mock_log.error.assert_has_calls(log_check)
        assert 1 == mock_disconnect_from_host.call_count, 'Should have only been called once'
        mock_send_command.assert_not_called()

    def test_process_pjlink_invalid_authentication_scheme_length_error(self):
        """
        Test initial connection prompt with authentication scheme longer than 1 character
        """
        # GIVEN: Initial mocks and data
        mock_log = patch.object(openlp.core.projectors.pjlink, 'log').start()
        mock_disconnect_from_host = patch('openlp.core.projectors.pjlink.PJLink.disconnect_from_host').start()
        mock_send_command = patch('openlp.core.projectors.pjlink.PJLink.send_command').start()

        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        log_check = [call('({ip}) Invalid initial authentication scheme - aborting'.format(ip=pjlink.name)), ]

        # WHEN: process_pjlink called with invalid authentication scheme
        pjlink.process_pjlink(data='01')

        # THEN: socket should be closed and invalid data logged
        mock_log.error.assert_has_calls(log_check)
        assert 1 == mock_disconnect_from_host.call_count, 'Should have only been called once'
        mock_send_command.assert_not_called()

    def test_process_pjlink_invalid_authentication_data_length_error(self):
        """
        Test initial connection prompt with authentication no salt
        """
        # GIVEN: Initial mocks and data
        mock_log = patch.object(openlp.core.projectors.pjlink, 'log').start()
        mock_disconnect_from_host = patch('openlp.core.projectors.pjlink.PJLink.disconnect_from_host').start()
        mock_send_command = patch('openlp.core.projectors.pjlink.PJLink.send_command').start()

        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        log_check = [call('({ip}) Authenticated connection but not enough info - aborting'.format(ip=pjlink.name)), ]

        # WHEN: process_pjlink called with no salt
        pjlink.process_pjlink(data='1')

        # THEN: socket should be closed and invalid data logged
        mock_log.error.assert_has_calls(log_check)
        assert 1 == mock_disconnect_from_host.call_count, 'Should have only been called once'
        mock_send_command.assert_not_called()

    def test_process_pjlink_authenticate_pin_not_set_error(self):
        """
        Test process_pjlink authentication but pin not set
        """
        # GIVEN: Initial mocks and data
        mock_log = patch.object(openlp.core.projectors.pjlink, 'log').start()
        mock_disconnect_from_host = patch('openlp.core.projectors.pjlink.PJLink.disconnect_from_host').start()
        mock_send_command = patch('openlp.core.projectors.pjlink.PJLink.send_command').start()

        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.pin = None
        log_check = [call('({ip}) Authenticate connection but no PIN - aborting'.format(ip=pjlink.name)), ]

        # WHEN: process_pjlink called with no salt
        pjlink.process_pjlink(data='1 {salt}'.format(salt=TEST_SALT))

        # THEN: socket should be closed and invalid data logged
        mock_log.error.assert_has_calls(log_check)
        assert 1 == mock_disconnect_from_host.call_count, 'Should have only been called once'
        mock_send_command.assert_not_called()
