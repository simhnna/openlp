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
    :mod:`openlp.core.lib.projector.pjlink` module
    Provides the necessary functions for connecting to a PJLink-capable projector.

    PJLink Class 1 Specifications.
    http://pjlink.jbmia.or.jp/english/dl_class1.html
        Section 5-1 PJLink Specifications
        Section 5-5 Guidelines for Input Terminals

    PJLink Class 2 Specifications.
    http://pjlink.jbmia.or.jp/english/dl_class2.html
        Section 5-1 PJLink Specifications
        Section 5-5 Guidelines for Input Terminals

    NOTE:
      Function names follow  the following syntax:
            def process_CCCC(...):
      WHERE:
            CCCC = PJLink command being processed.
"""

import logging
log = logging.getLogger(__name__)

log.debug('pjlink loaded')

__all__ = ['PJLink']

import re
from codecs import decode

from PyQt5 import QtCore, QtNetwork

from openlp.core.common import translate, qmd5_hash
from openlp.core.lib.projector.constants import CONNECTION_ERRORS, CR, ERROR_MSG, ERROR_STRING, \
    E_AUTHENTICATION, E_CONNECTION_REFUSED, E_GENERAL, E_INVALID_DATA, E_NETWORK, E_NOT_CONNECTED, E_OK, \
    E_PARAMETER, E_PROJECTOR, E_SOCKET_TIMEOUT, E_UNAVAILABLE, E_UNDEFINED, PJLINK_ERRORS, PJLINK_ERST_DATA, \
    PJLINK_ERST_STATUS, PJLINK_MAX_PACKET, PJLINK_PORT, PJLINK_POWR_STATUS, PJLINK_VALID_CMD, \
    STATUS_STRING, S_CONNECTED, S_CONNECTING, S_NETWORK_RECEIVED, S_NETWORK_SENDING, \
    S_NOT_CONNECTED, S_OFF, S_OK, S_ON, S_STATUS

# Shortcuts
SocketError = QtNetwork.QAbstractSocket.SocketError
SocketSTate = QtNetwork.QAbstractSocket.SocketState

PJLINK_PREFIX = '%'
PJLINK_CLASS = '1'  # Default to class 1 until we query the projector
# Add prefix here, but defer linkclass expansion until later when we have the actual
# PJLink class for the command
PJLINK_HEADER = '{prefix}{{linkclass}}'.format(prefix=PJLINK_PREFIX)
PJLINK_SUFFIX = CR


class PJLinkCommands(object):
    """
    Process replies from PJLink projector.
    """

    def __init__(self, *args, **kwargs):
        """
        Setup for the process commands
        """
        log.debug('PJlinkCommands(args={args} kwargs={kwargs})'.format(args=args, kwargs=kwargs))
        super().__init__()
        # Map command to function
        self.pjlink_functions = {
            'AVMT': self.process_avmt,
            'CLSS': self.process_clss,
            'ERST': self.process_erst,
            'INFO': self.process_info,
            'INF1': self.process_inf1,
            'INF2': self.process_inf2,
            'INPT': self.process_inpt,
            'INST': self.process_inst,
            'LAMP': self.process_lamp,
            'NAME': self.process_name,
            'PJLINK': self.check_login,
            'POWR': self.process_powr,
            'SNUM': self.process_snum,
            'SVER': self.process_sver,
            'RFIL': self.process_rfil,
            'RLMP': self.process_rlmp
        }

    def reset_information(self):
        """
        Initialize instance variables. Also used to reset projector-specific information to default.
        """
        log.debug('({ip}) reset_information() connect status is {state}'.format(ip=self.ip, state=self.state()))
        self.fan = None  # ERST
        self.filter_time = None  # FILT
        self.lamp = None  # LAMP
        self.mac_adx_received = None  # ACKN
        self.manufacturer = None  # INF1
        self.model = None  # INF2
        self.model_filter = None  # RFIL
        self.model_lamp = None  # RLMP
        self.mute = None  # AVMT
        self.other_info = None  # INFO
        self.pjlink_class = PJLINK_CLASS  # Default class
        self.pjlink_name = None  # NAME
        self.power = S_OFF  # POWR
        self.serial_no = None  # SNUM
        self.serial_no_received = None
        self.sw_version = None  # SVER
        self.sw_version_received = None
        self.shutter = None  # AVMT
        self.source_available = None  # INST
        self.source = None  # INPT
        # These should be part of PJLink() class, but set here for convenience
        if hasattr(self, 'timer'):
            log.debug('({ip}): Calling timer.stop()'.format(ip=self.ip))
            self.timer.stop()
        if hasattr(self, 'socket_timer'):
            log.debug('({ip}): Calling socket_timer.stop()'.format(ip=self.ip))
            self.socket_timer.stop()
        self.send_busy = False
        self.send_queue = []

    def process_command(self, cmd, data):
        """
        Verifies any return error code. Calls the appropriate command handler.

        :param cmd: Command to process
        :param data: Data being processed
        """
        log.debug('({ip}) Processing command "{cmd}" with data "{data}"'.format(ip=self.ip,
                                                                                cmd=cmd,
                                                                                data=data))
        # Check if we have a future command not available yet
        _cmd = cmd.upper()
        _data = data.upper()
        if _cmd not in PJLINK_VALID_CMD:
            log.error("({ip}) Ignoring command='{cmd}' (Invalid/Unknown)".format(ip=self.ip, cmd=cmd))
            return
        elif _data == 'OK':
            log.debug('({ip}) Command "{cmd}" returned OK'.format(ip=self.ip, cmd=cmd))
            # A command returned successfully, no further processing needed
            return
        elif _cmd not in self.pjlink_functions:
            log.warn("({ip}) Unable to process command='{cmd}' (Future option)".format(ip=self.ip, cmd=cmd))
            return
        elif _data in PJLINK_ERRORS:
            # Oops - projector error
            log.error('({ip}) Projector returned error "{data}"'.format(ip=self.ip, data=data))
            if _data == PJLINK_ERRORS[E_AUTHENTICATION]:
                # Authentication error
                self.disconnect_from_host()
                self.change_status(E_AUTHENTICATION)
                log.debug('({ip}) emitting projectorAuthentication() signal'.format(ip=self.ip))
                self.projectorAuthentication.emit(self.name)
            elif _data == PJLINK_ERRORS[E_UNDEFINED]:
                # Projector does not recognize command
                self.change_status(E_UNDEFINED, '{error}: "{data}"'.format(error=ERROR_MSG[E_UNDEFINED],
                                                                           data=cmd))
            elif _data == PJLINK_ERRORS[E_PARAMETER]:
                # Invalid parameter
                self.change_status(E_PARAMETER)
            elif _data == PJLINK_ERRORS[E_UNAVAILABLE]:
                # Projector busy
                self.change_status(E_UNAVAILABLE)
            elif _data == PJLINK_ERRORS[E_PROJECTOR]:
                # Projector/display error
                self.change_status(E_PROJECTOR)
            self.receive_data_signal()
            return
        # Command checks already passed
        log.debug('({ip}) Calling function for {cmd}'.format(ip=self.ip, cmd=cmd))
        self.receive_data_signal()
        self.pjlink_functions[_cmd](data)

    def process_avmt(self, data):
        """
        Process shutter and speaker status. See PJLink specification for format.
        Update self.mute (audio) and self.shutter (video shutter).
        11 = Shutter closed, audio unchanged
        21 = Shutter unchanged, Audio muted
        30 = Shutter closed, audio muted
        31 = Shutter open,  audio normal

        :param data: Shutter and audio status
        """
        settings = {'11': {'shutter': True, 'mute': self.mute},
                    '21': {'shutter': self.shutter, 'mute': True},
                    '30': {'shutter': False, 'mute': False},
                    '31': {'shutter': True, 'mute': True}
                    }
        if data not in settings:
            log.warning('({ip}) Invalid shutter response: {data}'.format(ip=self.ip, data=data))
            return
        shutter = settings[data]['shutter']
        mute = settings[data]['mute']
        # Check if we need to update the icons
        update_icons = (shutter != self.shutter) or (mute != self.mute)
        self.shutter = shutter
        self.mute = mute
        if update_icons:
            self.projectorUpdateIcons.emit()
        return

    def process_clss(self, data):
        """
        PJLink class that this projector supports. See PJLink specification for format.
        Updates self.class.

        :param data: Class that projector supports.
        """
        # bug 1550891: Projector returns non-standard class response:
        #            : Expected: '%1CLSS=1'
        #            : Received: '%1CLSS=Class 1'  (Optoma)
        #            : Received: '%1CLSS=Version1'  (BenQ)
        if len(data) > 1:
            log.warn("({ip}) Non-standard CLSS reply: '{data}'".format(ip=self.ip, data=data))
            # Due to stupid projectors not following standards (Optoma, BenQ comes to mind),
            # AND the different responses that can be received, the semi-permanent way to
            # fix the class reply is to just remove all non-digit characters.
            try:
                clss = re.findall('\d', data)[0]  # Should only be the first match
            except IndexError:
                log.error("({ip}) No numbers found in class version reply '{data}' - "
                          "defaulting to class '1'".format(ip=self.ip, data=data))
                clss = '1'
        elif not data.isdigit():
            log.error("({ip}) NAN clss version reply '{data}' - "
                      "defaulting to class '1'".format(ip=self.ip, data=data))
            clss = '1'
        else:
            clss = data
        self.pjlink_class = clss
        log.debug('({ip}) Setting pjlink_class for this projector to "{data}"'.format(ip=self.ip,
                                                                                      data=self.pjlink_class))
        return

    def process_erst(self, data):
        """
        Error status. See PJLink Specifications for format.
        Updates self.projector_errors

        :param data: Error status
        """
        if len(data) != PJLINK_ERST_DATA['DATA_LENGTH']:
            count = PJLINK_ERST_DATA['DATA_LENGTH']
            log.warn("{ip}) Invalid error status response '{data}': length != {count}".format(ip=self.ip,
                                                                                              data=data,
                                                                                              count=count))
            return
        try:
            datacheck = int(data)
        except ValueError:
            # Bad data - ignore
            log.warn("({ip}) Invalid error status response '{data}'".format(ip=self.ip, data=data))
            return
        if datacheck == 0:
            self.projector_errors = None
            # No errors
            return
        # We have some sort of status error, so check out what it/they are
        self.projector_errors = {}
        fan, lamp, temp, cover, filt, other = (data[PJLINK_ERST_DATA['FAN']],
                                               data[PJLINK_ERST_DATA['LAMP']],
                                               data[PJLINK_ERST_DATA['TEMP']],
                                               data[PJLINK_ERST_DATA['COVER']],
                                               data[PJLINK_ERST_DATA['FILTER']],
                                               data[PJLINK_ERST_DATA['OTHER']])
        if fan != PJLINK_ERST_STATUS[E_OK]:
            self.projector_errors[translate('OpenLP.ProjectorPJLink', 'Fan')] = \
                PJLINK_ERST_STATUS[fan]
        if lamp != PJLINK_ERST_STATUS[E_OK]:
            self.projector_errors[translate('OpenLP.ProjectorPJLink', 'Lamp')] =  \
                PJLINK_ERST_STATUS[lamp]
        if temp != PJLINK_ERST_STATUS[E_OK]:
            self.projector_errors[translate('OpenLP.ProjectorPJLink', 'Temperature')] =  \
                PJLINK_ERST_STATUS[temp]
        if cover != PJLINK_ERST_STATUS[E_OK]:
            self.projector_errors[translate('OpenLP.ProjectorPJLink', 'Cover')] =  \
                PJLINK_ERST_STATUS[cover]
        if filt != PJLINK_ERST_STATUS[E_OK]:
            self.projector_errors[translate('OpenLP.ProjectorPJLink', 'Filter')] =  \
                PJLINK_ERST_STATUS[filt]
        if other != PJLINK_ERST_STATUS[E_OK]:
            self.projector_errors[translate('OpenLP.ProjectorPJLink', 'Other')] =  \
                PJLINK_ERST_STATUS[other]
        return

    def process_inf1(self, data):
        """
        Manufacturer name set in projector.
        Updates self.manufacturer

        :param data: Projector manufacturer
        """
        self.manufacturer = data
        log.debug('({ip}) Setting projector manufacturer data to "{data}"'.format(ip=self.ip, data=self.manufacturer))
        return

    def process_inf2(self, data):
        """
        Projector Model set in projector.
        Updates self.model.

        :param data: Model name
        """
        self.model = data
        log.debug('({ip}) Setting projector model to "{data}"'.format(ip=self.ip, data=self.model))
        return

    def process_info(self, data):
        """
        Any extra info set in projector.
        Updates self.other_info.

        :param data: Projector other info
        """
        self.other_info = data
        log.debug('({ip}) Setting projector other_info to "{data}"'.format(ip=self.ip, data=self.other_info))
        return

    def process_inpt(self, data):
        """
        Current source input selected. See PJLink specification for format.
        Update self.source

        :param data: Currently selected source
        """
        self.source = data
        log.info('({ip}) Setting data source to "{data}"'.format(ip=self.ip, data=self.source))
        return

    def process_inst(self, data):
        """
        Available source inputs. See PJLink specification for format.
        Updates self.source_available

        :param data: Sources list
        """
        sources = []
        check = data.split()
        for source in check:
            sources.append(source)
        sources.sort()
        self.source_available = sources
        self.projectorUpdateIcons.emit()
        log.debug('({ip}) Setting projector sources_available to "{data}"'.format(ip=self.ip,
                                                                                  data=self.source_available))
        return

    def process_lamp(self, data):
        """
        Lamp(s) status. See PJLink Specifications for format.
        Data may have more than 1 lamp to process.
        Update self.lamp dictionary with lamp status.

        :param data: Lamp(s) status.
        """
        lamps = []
        data_dict = data.split()
        while data_dict:
            try:
                fill = {'Hours': int(data_dict[0]), 'On': False if data_dict[1] == '0' else True}
            except ValueError:
                # In case of invalid entry
                log.warning('({ip}) process_lamp(): Invalid data "{data}"'.format(ip=self.ip, data=data))
                return
            lamps.append(fill)
            data_dict.pop(0)  # Remove lamp hours
            data_dict.pop(0)  # Remove lamp on/off
        self.lamp = lamps
        return

    def process_name(self, data):
        """
        Projector name set in projector.
        Updates self.pjlink_name

        :param data: Projector name
        """
        self.pjlink_name = data
        log.debug('({ip}) Setting projector PJLink name to "{data}"'.format(ip=self.ip, data=self.pjlink_name))
        return

    def process_powr(self, data):
        """
        Power status. See PJLink specification for format.
        Update self.power with status. Update icons if change from previous setting.

        :param data: Power status
        """
        log.debug('({ip}: Processing POWR command'.format(ip=self.ip))
        if data in PJLINK_POWR_STATUS:
            power = PJLINK_POWR_STATUS[data]
            update_icons = self.power != power
            self.power = power
            self.change_status(PJLINK_POWR_STATUS[data])
            if update_icons:
                self.projectorUpdateIcons.emit()
                # Update the input sources available
                if power == S_ON:
                    self.send_command('INST')
        else:
            # Log unknown status response
            log.warning('({ip}) Unknown power response: {data}'.format(ip=self.ip, data=data))
        return

    def process_rfil(self, data):
        """
        Process replacement filter type
        """
        if self.model_filter is None:
            self.model_filter = data
        else:
            log.warn("({ip}) Filter model already set".format(ip=self.ip))
            log.warn("({ip}) Saved model: '{old}'".format(ip=self.ip, old=self.model_filter))
            log.warn("({ip}) New model: '{new}'".format(ip=self.ip, new=data))

    def process_rlmp(self, data):
        """
        Process replacement lamp type
        """
        if self.model_lamp is None:
            self.model_lamp = data
        else:
            log.warn("({ip}) Lamp model already set".format(ip=self.ip))
            log.warn("({ip}) Saved lamp: '{old}'".format(ip=self.ip, old=self.model_lamp))
            log.warn("({ip}) New lamp: '{new}'".format(ip=self.ip, new=data))

    def process_snum(self, data):
        """
        Serial number of projector.

        :param data: Serial number from projector.
        """
        if self.serial_no is None:
            log.debug("({ip}) Setting projector serial number to '{data}'".format(ip=self.ip, data=data))
            self.serial_no = data
            self.db_update = False
        else:
            # Compare serial numbers and see if we got the same projector
            if self.serial_no != data:
                log.warn("({ip}) Projector serial number does not match saved serial number".format(ip=self.ip))
                log.warn("({ip}) Saved:    '{old}'".format(ip=self.ip, old=self.serial_no))
                log.warn("({ip}) Received: '{new}'".format(ip=self.ip, new=data))
                log.warn("({ip}) NOT saving serial number".format(ip=self.ip))
                self.serial_no_received = data

    def process_sver(self, data):
        """
        Software version of projector
        """
        if self.sw_version is None:
            log.debug("({ip}) Setting projector software version to '{data}'".format(ip=self.ip, data=data))
            self.sw_version = data
            self.db_update = True
        else:
            # Compare software version and see if we got the same projector
            if self.serial_no != data:
                log.warn("({ip}) Projector software version does not match saved software version".format(ip=self.ip))
                log.warn("({ip}) Saved:    '{old}'".format(ip=self.ip, old=self.sw_version))
                log.warn("({ip}) Received: '{new}'".format(ip=self.ip, new=data))
                log.warn("({ip}) NOT saving serial number".format(ip=self.ip))
                self.sw_version_received = data


class PJLink(PJLinkCommands, QtNetwork.QTcpSocket):
    """
    Socket service for connecting to a PJLink-capable projector.
    """
    # Signals sent by this module
    changeStatus = QtCore.pyqtSignal(str, int, str)
    projectorNetwork = QtCore.pyqtSignal(int)  # Projector network activity
    projectorStatus = QtCore.pyqtSignal(int)  # Status update
    projectorAuthentication = QtCore.pyqtSignal(str)  # Authentication error
    projectorNoAuthentication = QtCore.pyqtSignal(str)  # PIN set and no authentication needed
    projectorReceivedData = QtCore.pyqtSignal()  # Notify when received data finished processing
    projectorUpdateIcons = QtCore.pyqtSignal()  # Update the status icons on toolbar

    # New commands available in PJLink Class 2
    pjlink_udp_commands = [
        'ACKN',  # Class 2
        'ERST',  # Class 1 or 2
        'INPT',  # Class 1 or 2
        'LKUP',  # Class 2
        'POWR',  # Class 1 or 2
        'SRCH'   # Class 2
    ]

    def __init__(self, port=PJLINK_PORT, *args, **kwargs):
        """
        Setup for instance.
        Options should be in kwargs except for port which does have a default.

        :param name: Display name
        :param ip: IP address to connect to
        :param port: Port to use. Default to PJLINK_PORT
        :param pin: Access pin (if needed)

        Optional parameters
        :param dbid: Database ID number
        :param location: Location where projector is physically located
        :param notes: Extra notes about the projector
        :param poll_time: Time (in seconds) to poll connected projector
        :param socket_timeout: Time (in seconds) to abort the connection if no response
        """
        log.debug('PJlink(args={args} kwargs={kwargs})'.format(args=args, kwargs=kwargs))
        super().__init__()
        self.dbid = kwargs.get('dbid')
        self.ip = kwargs.get('ip')
        self.location = kwargs.get('location')
        self.mac_adx = kwargs.get('mac_adx')
        self.name = kwargs.get('name')
        self.notes = kwargs.get('notes')
        self.pin = kwargs.get('pin')
        self.port = port
        self.db_update = False  # Use to check if db needs to be updated prior to exiting
        # Poll time 20 seconds unless called with something else
        self.poll_time = 20000 if 'poll_time' not in kwargs else kwargs['poll_time'] * 1000
        # Timeout 5 seconds unless called with something else
        self.socket_timeout = 5000 if 'socket_timeout' not in kwargs else kwargs['socket_timeout'] * 1000
        # In case we're called from somewhere that only wants information
        self.no_poll = 'no_poll' in kwargs
        self.i_am_running = False
        self.status_connect = S_NOT_CONNECTED
        self.last_command = ''
        self.projector_status = S_NOT_CONNECTED
        self.error_status = S_OK
        # Socket information
        # Add enough space to input buffer for extraneous \n \r
        self.max_size = PJLINK_MAX_PACKET + 2
        self.setReadBufferSize(self.max_size)
        self.reset_information()
        # Set from ProjectorManager.add_projector()
        self.widget = None  # QListBox entry
        self.timer = None  # Timer that calls the poll_loop
        self.send_queue = []
        self.send_busy = False
        # Socket timer for some possible brain-dead projectors or network cable pulled
        self.socket_timer = None

    def thread_started(self):
        """
        Connects signals to methods when thread is started.
        """
        log.debug('({ip}) Thread starting'.format(ip=self.ip))
        self.i_am_running = True
        self.connected.connect(self.check_login)
        self.disconnected.connect(self.disconnect_from_host)
        self.error.connect(self.get_error)

    def thread_stopped(self):
        """
        Cleanups when thread is stopped.
        """
        log.debug('({ip}) Thread stopped'.format(ip=self.ip))
        try:
            self.connected.disconnect(self.check_login)
        except TypeError:
            pass
        try:
            self.disconnected.disconnect(self.disconnect_from_host)
        except TypeError:
            pass
        try:
            self.error.disconnect(self.get_error)
        except TypeError:
            pass
        try:
            self.projectorReceivedData.disconnect(self._send_command)
        except TypeError:
            pass
        self.disconnect_from_host()
        self.deleteLater()
        self.i_am_running = False

    def socket_abort(self):
        """
        Aborts connection and closes socket in case of brain-dead projectors.
        Should normally be called by socket_timer().
        """
        log.debug('({ip}) socket_abort() - Killing connection'.format(ip=self.ip))
        self.disconnect_from_host(abort=True)

    def poll_loop(self):
        """
        Retrieve information from projector that changes.
        Normally called by timer().
        """
        if self.state() != self.ConnectedState:
            log.warn("({ip}) poll_loop(): Not connected - returning".format(ip=self.ip))
            return
        log.debug('({ip}) Updating projector status'.format(ip=self.ip))
        # Reset timer in case we were called from a set command
        if self.timer.interval() < self.poll_time:
            # Reset timer to 5 seconds
            self.timer.setInterval(self.poll_time)
        # Restart timer
        self.timer.start()
        # These commands may change during connection
        check_list = ['POWR', 'ERST', 'LAMP', 'AVMT', 'INPT']
        if self.pjlink_class == '2':
            check_list.extend(['FILT', 'FREZ'])
        for command in check_list:
            self.send_command(command, queue=True)
        # The following commands do not change, so only check them once
        if self.power == S_ON and self.source_available is None:
            self.send_command('INST', queue=True)
        if self.other_info is None:
            self.send_command('INFO', queue=True)
        if self.manufacturer is None:
            self.send_command('INF1', queue=True)
        if self.model is None:
            self.send_command('INF2', queue=True)
        if self.pjlink_name is None:
            self.send_command('NAME', queue=True)
        if self.pjlink_class == '2':
            # Class 2 specific checks
            if self.serial_no is None:
                self.send_command('SNUM', queue=True)
            if self.sw_version is None:
                self.send_command('SVER', queue=True)
            if self.model_filter is None:
                self.send_command('RFIL', queue=True)
            if self.model_lamp is None:
                self.send_command('RLMP', queue=True)

    def _get_status(self, status):
        """
        Helper to retrieve status/error codes and convert to strings.

        :param status: Status/Error code
        :returns: (Status/Error code, String)
        """
        if status in ERROR_STRING:
            return ERROR_STRING[status], ERROR_MSG[status]
        elif status in STATUS_STRING:
            return STATUS_STRING[status], ERROR_MSG[status]
        else:
            return status, translate('OpenLP.PJLink', 'Unknown status')

    def change_status(self, status, msg=None):
        """
        Check connection/error status, set status for projector, then emit status change signal
        for gui to allow changing the icons.

        :param status: Status code
        :param msg: Optional message
        """
        message = translate('OpenLP.PJLink', 'No message') if msg is None else msg
        (code, message) = self._get_status(status)
        if msg is not None:
            message = msg
        if status in CONNECTION_ERRORS:
            # Projector, connection state
            self.projector_status = self.error_status = self.status_connect = E_NOT_CONNECTED
        elif status >= S_NOT_CONNECTED and status < S_STATUS:
            self.status_connect = status
            self.projector_status = S_NOT_CONNECTED
        elif status < S_NETWORK_SENDING:
            self.status_connect = S_CONNECTED
            self.projector_status = status
        (status_code, status_message) = self._get_status(self.status_connect)
        log.debug('({ip}) status_connect: {code}: "{message}"'.format(ip=self.ip,
                                                                      code=status_code,
                                                                      message=status_message if msg is None else msg))
        (status_code, status_message) = self._get_status(self.projector_status)
        log.debug('({ip}) projector_status: {code}: "{message}"'.format(ip=self.ip,
                                                                        code=status_code,
                                                                        message=status_message if msg is None else msg))
        (status_code, status_message) = self._get_status(self.error_status)
        log.debug('({ip}) error_status: {code}: "{message}"'.format(ip=self.ip,
                                                                    code=status_code,
                                                                    message=status_message if msg is None else msg))
        self.changeStatus.emit(self.ip, status, message)

    @QtCore.pyqtSlot()
    def check_login(self, data=None):
        """
        Processes the initial connection and authentication (if needed).
        Starts poll timer if connection is established.

        NOTE: Qt md5 hash function doesn't work with projector authentication. Use the python md5 hash function.

        :param data: Optional data if called from another routine
        """
        log.debug('({ip}) check_login(data="{data}")'.format(ip=self.ip, data=data))
        if data is None:
            # Reconnected setup?
            if not self.waitForReadyRead(2000):
                # Possible timeout issue
                log.error('({ip}) Socket timeout waiting for login'.format(ip=self.ip))
                self.change_status(E_SOCKET_TIMEOUT)
                return
            read = self.readLine(self.max_size)
            self.readLine(self.max_size)  # Clean out the trailing \r\n
            if read is None:
                log.warning('({ip}) read is None - socket error?'.format(ip=self.ip))
                return
            elif len(read) < 8:
                log.warning('({ip}) Not enough data read)'.format(ip=self.ip))
                return
            data = decode(read, 'utf-8')
            # Possibility of extraneous data on input when reading.
            # Clean out extraneous characters in buffer.
            self.readLine(self.max_size)
            log.debug('({ip}) check_login() read "{data}"'.format(ip=self.ip, data=data.strip()))
        # At this point, we should only have the initial login prompt with
        # possible authentication
        # PJLink initial login will be:
        # 'PJLink 0' - Unauthenticated login - no extra steps required.
        # 'PJLink 1 XXXXXX' Authenticated login - extra processing required.
        if not data.upper().startswith('PJLINK'):
            # Invalid response
            return self.disconnect_from_host()
        if '=' in data:
            # Processing a login reply
            data_check = data.strip().split('=')
        else:
            # Process initial connection
            data_check = data.strip().split(' ')
        log.debug('({ip}) data_check="{data}"'.format(ip=self.ip, data=data_check))
        # Check for projector reporting an error
        if data_check[1].upper() == 'ERRA':
            # Authentication error
            self.disconnect_from_host()
            self.change_status(E_AUTHENTICATION)
            log.debug('({ip}) emitting projectorAuthentication() signal'.format(ip=self.ip))
            return
        elif data_check[1] == '0' and self.pin is not None:
            # Pin set and no authentication needed
            log.warning('({ip}) Regular connection but PIN set'.format(ip=self.name))
            self.disconnect_from_host()
            self.change_status(E_AUTHENTICATION)
            log.debug('({ip}) Emitting projectorNoAuthentication() signal'.format(ip=self.ip))
            self.projectorNoAuthentication.emit(self.name)
            return
        elif data_check[1] == '1':
            # Authenticated login with salt
            if self.pin is None:
                log.warning('({ip}) Authenticated connection but no pin set'.format(ip=self.ip))
                self.disconnect_from_host()
                self.change_status(E_AUTHENTICATION)
                log.debug('({ip}) Emitting projectorAuthentication() signal'.format(ip=self.ip))
                self.projectorAuthentication.emit(self.ip)
                return
            else:
                log.debug('({ip}) Setting hash with salt="{data}"'.format(ip=self.ip, data=data_check[2]))
                log.debug('({ip}) pin="{data}"'.format(ip=self.ip, data=self.pin))
                data_hash = str(qmd5_hash(salt=data_check[2].encode('utf-8'), data=self.pin.encode('utf-8')),
                                encoding='ascii')
        else:
            data_hash = None
        # We're connected at this point, so go ahead and setup regular I/O
        self.readyRead.connect(self.get_data)
        self.projectorReceivedData.connect(self._send_command)
        # Initial data we should know about
        self.send_command(cmd='CLSS', salt=data_hash)
        self.waitForReadyRead()
        if (not self.no_poll) and (self.state() == self.ConnectedState):
            log.debug('({ip}) Starting timer'.format(ip=self.ip))
            self.timer.setInterval(2000)  # Set 2 seconds for initial information
            self.timer.start()

    def _trash_buffer(self, msg=None):
        """
        Clean out extraneous stuff in the buffer.
        """
        log.warning("({ip}) {message}".format(ip=self.ip, message='Invalid packet' if msg is None else msg))
        self.send_busy = False
        trash_count = 0
        while self.bytesAvailable() > 0:
            trash = self.read(self.max_size)
            trash_count += len(trash)
        log.debug("({ip}) Finished cleaning buffer - {count} bytes dropped".format(ip=self.ip,
                                                                                   count=trash_count))
        return

    @QtCore.pyqtSlot()
    def get_data(self):
        """
        Socket interface to retrieve data.
        """
        log.debug('({ip}) get_data(): Reading data'.format(ip=self.ip))
        if self.state() != self.ConnectedState:
            log.debug('({ip}) get_data(): Not connected - returning'.format(ip=self.ip))
            self.send_busy = False
            return
        read = self.readLine(self.max_size)
        log.debug("({ip}) get_data(): '{buff}'".format(ip=self.ip, buff=read))
        if read == -1:
            # No data available
            log.debug('({ip}) get_data(): No data available (-1)'.format(ip=self.ip))
            return self.receive_data_signal()
        self.socket_timer.stop()
        self.projectorNetwork.emit(S_NETWORK_RECEIVED)
        # NOTE: Class2 has changed to some values being UTF-8
        data_in = decode(read, 'utf-8')
        data = data_in.strip()
        if (len(data) < 7) or (not data.startswith(PJLINK_PREFIX)):
            return self._trash_buffer(msg='get_data(): Invalid packet - length or prefix')
        elif '=' not in data:
            return self._trash_buffer(msg='get_data(): Invalid packet does not have equal')
        log.debug('({ip}) get_data(): Checking new data "{data}"'.format(ip=self.ip, data=data))
        header, data = data.split('=')
        try:
            version, cmd = header[1], header[2:]
        except ValueError as e:
            self.change_status(E_INVALID_DATA)
            log.warning('({ip}) get_data(): Received data: "{data}"'.format(ip=self.ip, data=data_in.strip()))
            return self._trash_buffer('get_data(): Expected header + command + data')
        if cmd not in PJLINK_VALID_CMD:
            log.warning('({ip}) get_data(): Invalid packet - unknown command "{data}"'.format(ip=self.ip, data=cmd))
            return self._trash_buffer(msg='get_data(): Unknown command "{data}"'.format(data=cmd))
        if int(self.pjlink_class) < int(version):
            log.warn('({ip}) get_data(): Projector returned class reply higher '
                     'than projector stated class'.format(ip=self.ip))
        return self.process_command(cmd, data)

    @QtCore.pyqtSlot(QtNetwork.QAbstractSocket.SocketError)
    def get_error(self, err):
        """
        Process error from SocketError signal.
        Remaps system error codes to projector error codes.

        :param err: Error code
        """
        log.debug('({ip}) get_error(err={error}): {data}'.format(ip=self.ip, error=err, data=self.errorString()))
        if err <= 18:
            # QSocket errors. Redefined in projector.constants so we don't mistake
            # them for system errors
            check = err + E_CONNECTION_REFUSED
            self.timer.stop()
        else:
            check = err
        if check < E_GENERAL:
            # Some system error?
            self.change_status(err, self.errorString())
        else:
            self.change_status(E_NETWORK, self.errorString())
        self.projectorUpdateIcons.emit()
        if self.status_connect == E_NOT_CONNECTED:
            self.abort()
            self.reset_information()
        return

    def send_command(self, cmd, opts='?', salt=None, queue=False):
        """
        Add command to output queue if not already in queue.

        :param cmd: Command to send
        :param opts: Command option (if any) - defaults to '?' (get information)
        :param salt: Optional  salt for md5 hash initial authentication
        :param queue: Option to force add to queue rather than sending directly
        """
        if self.state() != self.ConnectedState:
            log.warning('({ip}) send_command(): Not connected - returning'.format(ip=self.ip))
            self.send_queue = []
            return
        if cmd not in PJLINK_VALID_CMD:
            log.error('({ip}) send_command(): Invalid command requested - ignoring.'.format(ip=self.ip))
            return
        self.projectorNetwork.emit(S_NETWORK_SENDING)
        log.debug('({ip}) send_command(): Building cmd="{command}" opts="{data}"{salt}'.format(ip=self.ip,
                                                                                               command=cmd,
                                                                                               data=opts,
                                                                                               salt='' if salt is None
                                                                                               else ' with hash'))
        cmd_ver = PJLINK_VALID_CMD[cmd]['version']
        if self.pjlink_class in PJLINK_VALID_CMD[cmd]['version']:
            header = PJLINK_HEADER.format(linkclass=self.pjlink_class)
        elif len(cmd_ver) == 1 and (int(cmd_ver[0]) < int(self.pjlink_class)):
            # Typically a class 1 only command
            header = PJLINK_HEADER.format(linkclass=cmd_ver[0])
        else:
            # NOTE: Once we get to version 3 then think about looping
            log.error('({ip}): send_command(): PJLink class check issue? aborting'.format(ip=self.ip))
            return
        out = '{salt}{header}{command} {options}{suffix}'.format(salt="" if salt is None else salt,
                                                                 header=header,
                                                                 command=cmd,
                                                                 options=opts,
                                                                 suffix=CR)
        if out in self.send_queue:
            # Already there, so don't add
            log.debug('({ip}) send_command(out="{data}") Already in queue - skipping'.format(ip=self.ip,
                                                                                             data=out.strip()))
        elif not queue and len(self.send_queue) == 0:
            # Nothing waiting to send, so just send it
            log.debug('({ip}) send_command(out="{data}") Sending data'.format(ip=self.ip, data=out.strip()))
            return self._send_command(data=out)
        else:
            log.debug('({ip}) send_command(out="{data}") adding to queue'.format(ip=self.ip, data=out.strip()))
            self.send_queue.append(out)
            self.projectorReceivedData.emit()
        log.debug('({ip}) send_command(): send_busy is {data}'.format(ip=self.ip, data=self.send_busy))
        if not self.send_busy:
            log.debug('({ip}) send_command() calling _send_string()'.format(ip=self.ip))
            self._send_command()

    @QtCore.pyqtSlot()
    def _send_command(self, data=None, utf8=False):
        """
        Socket interface to send data. If data=None, then check queue.

        :param data: Immediate data to send
        :param utf8: Send as UTF-8 string otherwise send as ASCII string
        """
        log.debug('({ip}) _send_string()'.format(ip=self.ip))
        log.debug('({ip}) _send_string(): Connection status: {data}'.format(ip=self.ip, data=self.state()))
        if self.state() != self.ConnectedState:
            log.debug('({ip}) _send_string() Not connected - abort'.format(ip=self.ip))
            self.send_queue = []
            self.send_busy = False
            return
        if self.send_busy:
            # Still waiting for response from last command sent
            return
        if data is not None:
            out = data
            log.debug('({ip}) _send_string(data="{data}")'.format(ip=self.ip, data=out.strip()))
        elif len(self.send_queue) != 0:
            out = self.send_queue.pop(0)
            log.debug('({ip}) _send_string(queued data="{data}"%s)'.format(ip=self.ip, data=out.strip()))
        else:
            # No data to send
            log.debug('({ip}) _send_string(): No data to send'.format(ip=self.ip))
            self.send_busy = False
            return
        self.send_busy = True
        log.debug('({ip}) _send_string(): Sending "{data}"'.format(ip=self.ip, data=out.strip()))
        log.debug('({ip}) _send_string(): Queue = {data}'.format(ip=self.ip, data=self.send_queue))
        self.socket_timer.start()
        self.projectorNetwork.emit(S_NETWORK_SENDING)
        sent = self.write(out.encode('{string_encoding}'.format(string_encoding='utf-8' if utf8 else 'ascii')))
        self.waitForBytesWritten(2000)  # 2 seconds should be enough
        if sent == -1:
            # Network error?
            log.warning("({ip}) _send_command(): -1 received".format(ip=self.ip))
            self.change_status(E_NETWORK,
                               translate('OpenLP.PJLink', 'Error while sending data to projector'))

    def connect_to_host(self):
        """
        Initiate connection to projector.
        """
        if self.state() == self.ConnectedState:
            log.warning('({ip}) connect_to_host(): Already connected - returning'.format(ip=self.ip))
            return
        self.change_status(S_CONNECTING)
        self.connectToHost(self.ip, self.port if isinstance(self.port, int) else int(self.port))

    @QtCore.pyqtSlot()
    def disconnect_from_host(self, abort=False):
        """
        Close socket and cleanup.
        """
        if abort or self.state() != self.ConnectedState:
            if abort:
                log.warning('({ip}) disconnect_from_host(): Aborting connection'.format(ip=self.ip))
            else:
                log.warning('({ip}) disconnect_from_host(): Not connected - returning'.format(ip=self.ip))
            self.reset_information()
        self.disconnectFromHost()
        try:
            self.readyRead.disconnect(self.get_data)
        except TypeError:
            pass
        if abort:
            self.change_status(E_NOT_CONNECTED)
        else:
            log.debug('({ip}) disconnect_from_host() '
                      'Current status {data}'.format(ip=self.ip, data=self._get_status(self.status_connect)[0]))
            if self.status_connect != E_NOT_CONNECTED:
                self.change_status(S_NOT_CONNECTED)
        self.reset_information()
        self.projectorUpdateIcons.emit()

    def get_available_inputs(self):
        """
        Send command to retrieve available source inputs.
        """
        log.debug('({ip}) Sending INST command'.format(ip=self.ip))
        return self.send_command(cmd='INST')

    def get_error_status(self):
        """
        Send command to retrieve currently known errors.
        """
        log.debug('({ip}) Sending ERST command'.format(ip=self.ip))
        return self.send_command(cmd='ERST')

    def get_input_source(self):
        """
        Send command to retrieve currently selected source input.
        """
        log.debug('({ip}) Sending INPT command'.format(ip=self.ip))
        return self.send_command(cmd='INPT')

    def get_lamp_status(self):
        """
        Send command to return the lap status.
        """
        log.debug('({ip}) Sending LAMP command'.format(ip=self.ip))
        return self.send_command(cmd='LAMP')

    def get_manufacturer(self):
        """
        Send command to retrieve manufacturer name.
        """
        log.debug('({ip}) Sending INF1 command'.format(ip=self.ip))
        return self.send_command(cmd='INF1')

    def get_model(self):
        """
        Send command to retrieve the model name.
        """
        log.debug('({ip}) Sending INF2 command'.format(ip=self.ip))
        return self.send_command(cmd='INF2')

    def get_name(self):
        """
        Send command to retrieve name as set by end-user (if set).
        """
        log.debug('({ip}) Sending NAME command'.format(ip=self.ip))
        return self.send_command(cmd='NAME')

    def get_other_info(self):
        """
        Send command to retrieve extra info set by manufacturer.
        """
        log.debug('({ip}) Sending INFO command'.format(ip=self.ip))
        return self.send_command(cmd='INFO')

    def get_power_status(self):
        """
        Send command to retrieve power status.
        """
        log.debug('({ip}) Sending POWR command'.format(ip=self.ip))
        return self.send_command(cmd='POWR')

    def get_shutter_status(self):
        """
        Send command to retrieve shutter status.
        """
        log.debug('({ip}) Sending AVMT command'.format(ip=self.ip))
        return self.send_command(cmd='AVMT')

    def set_input_source(self, src=None):
        """
        Verify input source available as listed in 'INST' command,
        then send the command to select the input source.

        :param src: Video source to select in projector
        """
        log.debug('({ip}) set_input_source(src="{data}")'.format(ip=self.ip, data=src))
        if self.source_available is None:
            return
        elif src not in self.source_available:
            return
        log.debug('({ip}) Setting input source to "{data}"'.format(ip=self.ip, data=src))
        self.send_command(cmd='INPT', opts=src)
        self.poll_loop()

    def set_power_on(self):
        """
        Send command to turn power to on.
        """
        log.debug('({ip}) Setting POWR to 1 (on)'.format(ip=self.ip))
        self.send_command(cmd='POWR', opts='1')
        self.poll_loop()

    def set_power_off(self):
        """
        Send command to turn power to standby.
        """
        log.debug('({ip}) Setting POWR to 0 (standby)'.format(ip=self.ip))
        self.send_command(cmd='POWR', opts='0')
        self.poll_loop()

    def set_shutter_closed(self):
        """
        Send command to set shutter to closed position.
        """
        log.debug('({ip}) Setting AVMT to 11 (shutter closed)'.format(ip=self.ip))
        self.send_command(cmd='AVMT', opts='11')
        self.poll_loop()

    def set_shutter_open(self):
        """
        Send command to set shutter to open position.
        """
        log.debug('({ip}) Setting AVMT to "10" (shutter open)'.format(ip=self.ip))
        self.send_command(cmd='AVMT', opts='10')
        self.poll_loop()

    def receive_data_signal(self):
        """
        Clear any busy flags and send data received signal
        """
        self.send_busy = False
        self.projectorReceivedData.emit()
        return
