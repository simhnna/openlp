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
The :mod:`openlp.core.lib.projector.constants` module provides the constants used for projector errors/status/defaults
"""
import logging

from openlp.core.common.i18n import translate

log = logging.getLogger(__name__)
log.debug('projector_constants loaded')

# Set common constants.
CR = chr(0x0D)  # \r
LF = chr(0x0A)  # \n
PJLINK_PORT = 4352
TIMEOUT = 30.0
PJLINK_MAX_PACKET = 136
# NOTE: Changed format to account for some commands are both class 1 and 2
PJLINK_VALID_CMD = {
    'ACKN': {'version': ['2', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'Acknowledge a PJLink SRCH command - returns MAC address.')
             },
    'AVMT': {'version': ['1', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'Blank/unblank video and/or mute audio.')
             },
    'CLSS': {'version': ['1', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query projector PJLink class support.')
             },
    'ERST': {'version': ['1', '2'],
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query error status from projector. '
                                      'Returns fan/lamp/temp/cover/filter/other error status.')
             },
    'FILT': {'version': ['2', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query number of hours on filter.')
             },
    'FREZ': {'version': ['2', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'Freeze or unfreeze current image being projected.')
             },
    'INF1': {'version': ['1', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query projector manufacturer name.')
             },
    'INF2': {'version': ['1', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query projector product name.')
             },
    'INFO': {'version': ['1', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query projector for other information set by manufacturer.')
             },
    'INNM': {'version': ['2', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query specified input source name')
             },
    'INPT': {'version': ['1', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'Switch to specified video source.')
             },
    'INST': {'version': ['1', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query available input sources.')
             },
    'IRES': {'version:': ['2', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query current input resolution.')
             },
    'LAMP': {'version': ['1', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query lamp time and on/off status. Multiple lamps supported.')
             },
    'LKUP': {'version': ['2', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'UDP Status - Projector is now available on network. Includes MAC address.')
             },
    'MVOL': {'version': ['2', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'Adjust microphone volume by 1 step.')
             },
    'NAME': {'version': ['1', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query customer-set projector name.')
             },
    'PJLINK': {'version': ['1', ],
               'description': translate('OpenLP.PJLinkConstants',
                                        'Initial connection with authentication/no authentication request.')
               },
    'POWR': {'version': ['1', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'Turn lamp on or off/standby.')
             },
    'RFIL': {'version': ['2', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query replacement air filter model number.')
             },
    'RLMP': {'version': ['2', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query replacement lamp model number.')
             },
    'RRES': {'version': ['2', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query recommended resolution.')
             },
    'SNUM': {'version': ['2', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query projector serial number.')
             },
    'SRCH': {'version': ['2', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'UDP broadcast search request for available projectors. Reply is ACKN.')
             },
    'SVER': {'version': ['2', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query projector software version number.')
             },
    'SVOL': {'version': ['2', ],
             'description': translate('OpenLP.PJLinkConstants',
                                      'Adjust speaker volume by 1 step.')
             }
}

# QAbstractSocketState enums converted to string
S_QSOCKET_STATE = {
    0: 'QSocketState - UnconnectedState',
    1: 'QSocketState - HostLookupState',
    2: 'QSocketState - ConnectingState',
    3: 'QSocketState - ConnectedState',
    4: 'QSocketState - BoundState',
    5: 'QSocketState - ListeningState (internal use only)',
    6: 'QSocketState - ClosingState',
    'UnconnectedState': 0,
    'HostLookupState': 1,
    'ConnectingState': 2,
    'ConnectedState': 3,
    'BoundState': 4,
    'ListeningState': 5,
    'ClosingState': 6
}

# Error and status codes
S_OK = E_OK = 0  # E_OK included since I sometimes forget
# Error codes. Start at 200 so we don't duplicate system error codes.
E_GENERAL = 200  # Unknown error
E_NOT_CONNECTED = 201
E_FAN = 202
E_LAMP = 203
E_TEMP = 204
E_COVER = 205
E_FILTER = 206
E_NO_AUTHENTICATION = 207  # PIN set and no authentication set on projector
E_UNDEFINED = 208       # ERR1
E_PARAMETER = 209       # ERR2
E_UNAVAILABLE = 210     # ERR3
E_PROJECTOR = 211       # ERR4
E_INVALID_DATA = 212
E_WARN = 213
E_ERROR = 214
E_AUTHENTICATION = 215  # ERRA
E_CLASS = 216
E_PREFIX = 217

# Remap Qt socket error codes to projector error codes
E_CONNECTION_REFUSED = 230
E_REMOTE_HOST_CLOSED_CONNECTION = 231
E_HOST_NOT_FOUND = 232
E_SOCKET_ACCESS = 233
E_SOCKET_RESOURCE = 234
E_SOCKET_TIMEOUT = 235
E_DATAGRAM_TOO_LARGE = 236
E_NETWORK = 237
E_ADDRESS_IN_USE = 238
E_SOCKET_ADDRESS_NOT_AVAILABLE = 239
E_UNSUPPORTED_SOCKET_OPERATION = 240
E_PROXY_AUTHENTICATION_REQUIRED = 241
E_SLS_HANDSHAKE_FAILED = 242
E_UNFINISHED_SOCKET_OPERATION = 243
E_PROXY_CONNECTION_REFUSED = 244
E_PROXY_CONNECTION_CLOSED = 245
E_PROXY_CONNECTION_TIMEOUT = 246
E_PROXY_NOT_FOUND = 247
E_PROXY_PROTOCOL = 248
E_UNKNOWN_SOCKET_ERROR = -1

# Status codes start at 300
S_NOT_CONNECTED = 300
S_CONNECTING = 301
S_CONNECTED = 302
S_INITIALIZE = 303
S_STATUS = 304
S_OFF = 305
S_STANDBY = 306
S_WARMUP = 307
S_ON = 308
S_COOLDOWN = 309
S_INFO = 310

# Information that does not affect status
S_NETWORK_SENDING = 400
S_NETWORK_RECEIVED = 401

CONNECTION_ERRORS = {
    E_NOT_CONNECTED, E_NO_AUTHENTICATION, E_AUTHENTICATION, E_CLASS,
    E_PREFIX, E_CONNECTION_REFUSED, E_REMOTE_HOST_CLOSED_CONNECTION,
    E_HOST_NOT_FOUND, E_SOCKET_ACCESS, E_SOCKET_RESOURCE, E_SOCKET_TIMEOUT,
    E_DATAGRAM_TOO_LARGE, E_NETWORK, E_ADDRESS_IN_USE, E_SOCKET_ADDRESS_NOT_AVAILABLE,
    E_UNSUPPORTED_SOCKET_OPERATION, E_PROXY_AUTHENTICATION_REQUIRED,
    E_SLS_HANDSHAKE_FAILED, E_UNFINISHED_SOCKET_OPERATION, E_PROXY_CONNECTION_REFUSED,
    E_PROXY_CONNECTION_CLOSED, E_PROXY_CONNECTION_TIMEOUT, E_PROXY_NOT_FOUND,
    E_PROXY_PROTOCOL, E_UNKNOWN_SOCKET_ERROR
}

PJLINK_ERRORS = {
    'ERRA': E_AUTHENTICATION,   # Authentication error
    'ERR1': E_UNDEFINED,        # Undefined command error
    'ERR2': E_PARAMETER,        # Invalid parameter error
    'ERR3': E_UNAVAILABLE,      # Projector busy
    'ERR4': E_PROJECTOR,        # Projector or display failure
    E_AUTHENTICATION: 'ERRA',
    E_UNDEFINED: 'ERR1',
    E_PARAMETER: 'ERR2',
    E_UNAVAILABLE: 'ERR3',
    E_PROJECTOR: 'ERR4'
}

# Map error/status codes to string
ERROR_STRING = {
    0: 'S_OK',
    E_GENERAL: 'E_GENERAL',
    E_NOT_CONNECTED: 'E_NOT_CONNECTED',
    E_FAN: 'E_FAN',
    E_LAMP: 'E_LAMP',
    E_TEMP: 'E_TEMP',
    E_COVER: 'E_COVER',
    E_FILTER: 'E_FILTER',
    E_AUTHENTICATION: 'E_AUTHENTICATION',
    E_NO_AUTHENTICATION: 'E_NO_AUTHENTICATION',
    E_UNDEFINED: 'E_UNDEFINED',
    E_PARAMETER: 'E_PARAMETER',
    E_UNAVAILABLE: 'E_UNAVAILABLE',
    E_PROJECTOR: 'E_PROJECTOR',
    E_INVALID_DATA: 'E_INVALID_DATA',
    E_WARN: 'E_WARN',
    E_ERROR: 'E_ERROR',
    E_CLASS: 'E_CLASS',
    E_PREFIX: 'E_PREFIX',  # Last projector error
    E_CONNECTION_REFUSED: 'E_CONNECTION_REFUSED',  # First QtSocket error
    E_REMOTE_HOST_CLOSED_CONNECTION: 'E_REMOTE_HOST_CLOSED_CONNECTION',
    E_HOST_NOT_FOUND: 'E_HOST_NOT_FOUND',
    E_SOCKET_ACCESS: 'E_SOCKET_ACCESS',
    E_SOCKET_RESOURCE: 'E_SOCKET_RESOURCE',
    E_SOCKET_TIMEOUT: 'E_SOCKET_TIMEOUT',
    E_DATAGRAM_TOO_LARGE: 'E_DATAGRAM_TOO_LARGE',
    E_NETWORK: 'E_NETWORK',
    E_ADDRESS_IN_USE: 'E_ADDRESS_IN_USE',
    E_SOCKET_ADDRESS_NOT_AVAILABLE: 'E_SOCKET_ADDRESS_NOT_AVAILABLE',
    E_UNSUPPORTED_SOCKET_OPERATION: 'E_UNSUPPORTED_SOCKET_OPERATION',
    E_PROXY_AUTHENTICATION_REQUIRED: 'E_PROXY_AUTHENTICATION_REQUIRED',
    E_SLS_HANDSHAKE_FAILED: 'E_SLS_HANDSHAKE_FAILED',
    E_UNFINISHED_SOCKET_OPERATION: 'E_UNFINISHED_SOCKET_OPERATION',
    E_PROXY_CONNECTION_REFUSED: 'E_PROXY_CONNECTION_REFUSED',
    E_PROXY_CONNECTION_CLOSED: 'E_PROXY_CONNECTION_CLOSED',
    E_PROXY_CONNECTION_TIMEOUT: 'E_PROXY_CONNECTION_TIMEOUT',
    E_PROXY_NOT_FOUND: 'E_PROXY_NOT_FOUND',
    E_PROXY_PROTOCOL: 'E_PROXY_PROTOCOL',
    E_UNKNOWN_SOCKET_ERROR: 'E_UNKNOWN_SOCKET_ERROR'
}

STATUS_STRING = {
    S_NOT_CONNECTED: 'S_NOT_CONNECTED',
    S_CONNECTING: 'S_CONNECTING',
    S_CONNECTED: 'S_CONNECTED',
    S_STATUS: 'S_STATUS',
    S_OFF: 'S_OFF',
    S_INITIALIZE: 'S_INITIALIZE',
    S_STANDBY: 'S_STANDBY',
    S_WARMUP: 'S_WARMUP',
    S_ON: 'S_ON',
    S_COOLDOWN: 'S_COOLDOWN',
    S_INFO: 'S_INFO',
    S_NETWORK_SENDING: 'S_NETWORK_SENDING',
    S_NETWORK_RECEIVED: 'S_NETWORK_RECEIVED'
}

# Map error/status codes to message strings
ERROR_MSG = {
    E_OK: translate('OpenLP.ProjectorConstants', 'OK'),  # E_OK | S_OK
    E_GENERAL: translate('OpenLP.ProjectorConstants', 'General projector error'),
    E_NOT_CONNECTED: translate('OpenLP.ProjectorConstants', 'Not connected error'),
    E_LAMP: translate('OpenLP.ProjectorConstants', 'Lamp error'),
    E_FAN: translate('OpenLP.ProjectorConstants', 'Fan error'),
    E_TEMP: translate('OpenLP.ProjectorConstants', 'High temperature detected'),
    E_COVER: translate('OpenLP.ProjectorConstants', 'Cover open detected'),
    E_FILTER: translate('OpenLP.ProjectorConstants', 'Check filter'),
    E_AUTHENTICATION: translate('OpenLP.ProjectorConstants', 'Authentication Error'),
    E_UNDEFINED: translate('OpenLP.ProjectorConstants', 'Undefined Command'),
    E_PARAMETER: translate('OpenLP.ProjectorConstants', 'Invalid Parameter'),
    E_UNAVAILABLE: translate('OpenLP.ProjectorConstants', 'Projector Busy'),
    E_PROJECTOR: translate('OpenLP.ProjectorConstants', 'Projector/Display Error'),
    E_INVALID_DATA: translate('OpenLP.ProjectorConstants', 'Invalid packet received'),
    E_WARN: translate('OpenLP.ProjectorConstants', 'Warning condition detected'),
    E_ERROR: translate('OpenLP.ProjectorConstants', 'Error condition detected'),
    E_CLASS: translate('OpenLP.ProjectorConstants', 'PJLink class not supported'),
    E_PREFIX: translate('OpenLP.ProjectorConstants', 'Invalid prefix character'),
    E_CONNECTION_REFUSED: translate('OpenLP.ProjectorConstants',
                                    'The connection was refused by the peer (or timed out)'),
    E_REMOTE_HOST_CLOSED_CONNECTION: translate('OpenLP.ProjectorConstants',
                                               'The remote host closed the connection'),
    E_HOST_NOT_FOUND: translate('OpenLP.ProjectorConstants', 'The host address was not found'),
    E_SOCKET_ACCESS: translate('OpenLP.ProjectorConstants',
                               'The socket operation failed because the application '
                               'lacked the required privileges'),
    E_SOCKET_RESOURCE: translate('OpenLP.ProjectorConstants',
                                 'The local system ran out of resources (e.g., too many sockets)'),
    E_SOCKET_TIMEOUT: translate('OpenLP.ProjectorConstants',
                                'The socket operation timed out'),
    E_DATAGRAM_TOO_LARGE: translate('OpenLP.ProjectorConstants',
                                    'The datagram was larger than the operating system\'s limit'),
    E_NETWORK: translate('OpenLP.ProjectorConstants',
                         'An error occurred with the network (Possibly someone pulled the plug?)'),
    E_ADDRESS_IN_USE: translate('OpenLP.ProjectorConstants',
                                'The address specified with socket.bind() '
                                'is already in use and was set to be exclusive'),
    E_SOCKET_ADDRESS_NOT_AVAILABLE: translate('OpenLP.ProjectorConstants',
                                              'The address specified to socket.bind() '
                                              'does not belong to the host'),
    E_UNSUPPORTED_SOCKET_OPERATION: translate('OpenLP.ProjectorConstants',
                                              'The requested socket operation is not supported by the local '
                                              'operating system (e.g., lack of IPv6 support)'),
    E_PROXY_AUTHENTICATION_REQUIRED: translate('OpenLP.ProjectorConstants',
                                               'The socket is using a proxy, '
                                               'and the proxy requires authentication'),
    E_SLS_HANDSHAKE_FAILED: translate('OpenLP.ProjectorConstants',
                                      'The SSL/TLS handshake failed'),
    E_UNFINISHED_SOCKET_OPERATION: translate('OpenLP.ProjectorConstants',
                                             'The last operation attempted has not finished yet '
                                             '(still in progress in the background)'),
    E_PROXY_CONNECTION_REFUSED: translate('OpenLP.ProjectorConstants',
                                          'Could not contact the proxy server because the connection '
                                          'to that server was denied'),
    E_PROXY_CONNECTION_CLOSED: translate('OpenLP.ProjectorConstants',
                                         'The connection to the proxy server was closed unexpectedly '
                                         '(before the connection to the final peer was established)'),
    E_PROXY_CONNECTION_TIMEOUT: translate('OpenLP.ProjectorConstants',
                                          'The connection to the proxy server timed out or the proxy '
                                          'server stopped responding in the authentication phase.'),
    E_PROXY_NOT_FOUND: translate('OpenLP.ProjectorConstants',
                                 'The proxy address set with setProxy() was not found'),
    E_PROXY_PROTOCOL: translate('OpenLP.ProjectorConstants',
                                'The connection negotiation with the proxy server failed because the '
                                'response from the proxy server could not be understood'),
    E_UNKNOWN_SOCKET_ERROR: translate('OpenLP.ProjectorConstants', 'An unidentified error occurred'),
    S_NOT_CONNECTED: translate('OpenLP.ProjectorConstants', 'Not connected'),
    S_CONNECTING: translate('OpenLP.ProjectorConstants', 'Connecting'),
    S_CONNECTED: translate('OpenLP.ProjectorConstants', 'Connected'),
    S_STATUS: translate('OpenLP.ProjectorConstants', 'Getting status'),
    S_OFF: translate('OpenLP.ProjectorConstants', 'Off'),
    S_INITIALIZE: translate('OpenLP.ProjectorConstants', 'Initialize in progress'),
    S_STANDBY: translate('OpenLP.ProjectorConstants', 'Power in standby'),
    S_WARMUP: translate('OpenLP.ProjectorConstants', 'Warmup in progress'),
    S_ON: translate('OpenLP.ProjectorConstants', 'Power is on'),
    S_COOLDOWN: translate('OpenLP.ProjectorConstants', 'Cooldown in progress'),
    S_INFO: translate('OpenLP.ProjectorConstants', 'Projector Information available'),
    S_NETWORK_SENDING: translate('OpenLP.ProjectorConstants', 'Sending data'),
    S_NETWORK_RECEIVED: translate('OpenLP.ProjectorConstants', 'Received data')
}

# Map ERST return code positions to equipment
PJLINK_ERST_DATA = {
    'DATA_LENGTH': 6,
    0: 'FAN',
    1: 'LAMP',
    2: 'TEMP',
    3: 'COVER',
    4: 'FILTER',
    5: 'OTHER',
    'FAN': 0,
    'LAMP': 1,
    'TEMP': 2,
    'COVER': 3,
    'FILTER': 4,
    'OTHER': 5
}

# Map for ERST return codes to string
PJLINK_ERST_STATUS = {
    '0': 'OK',
    '1': ERROR_STRING[E_WARN],
    '2': ERROR_STRING[E_ERROR],
    'OK': '0',
    E_OK: '0',
    E_WARN: '1',
    E_ERROR: '2'
}

# Map for POWR return codes to status code
PJLINK_POWR_STATUS = {
    '0': S_STANDBY,
    '1': S_ON,
    '2': S_COOLDOWN,
    '3': S_WARMUP,
    S_STANDBY: '0',
    S_ON: '1',
    S_COOLDOWN: '2',
    S_WARMUP: '3'
}

PJLINK_DEFAULT_SOURCES = {
    '1': translate('OpenLP.DB', 'RGB'),
    '2': translate('OpenLP.DB', 'Video'),
    '3': translate('OpenLP.DB', 'Digital'),
    '4': translate('OpenLP.DB', 'Storage'),
    '5': translate('OpenLP.DB', 'Network'),
    '6': translate('OpenLP.DB', 'Internal')
}

PJLINK_DEFAULT_ITEMS = {
    '1': translate('OpenLP.DB', '1'),
    '2': translate('OpenLP.DB', '2'),
    '3': translate('OpenLP.DB', '3'),
    '4': translate('OpenLP.DB', '4'),
    '5': translate('OpenLP.DB', '5'),
    '6': translate('OpenLP.DB', '6'),
    '7': translate('OpenLP.DB', '7'),
    '8': translate('OpenLP.DB', '8'),
    '9': translate('OpenLP.DB', '9'),
    'A': translate('OpenLP.DB', 'A'),
    'B': translate('OpenLP.DB', 'B'),
    'C': translate('OpenLP.DB', 'C'),
    'D': translate('OpenLP.DB', 'D'),
    'E': translate('OpenLP.DB', 'E'),
    'F': translate('OpenLP.DB', 'F'),
    'G': translate('OpenLP.DB', 'G'),
    'H': translate('OpenLP.DB', 'H'),
    'I': translate('OpenLP.DB', 'I'),
    'J': translate('OpenLP.DB', 'J'),
    'K': translate('OpenLP.DB', 'K'),
    'L': translate('OpenLP.DB', 'L'),
    'M': translate('OpenLP.DB', 'M'),
    'N': translate('OpenLP.DB', 'N'),
    'O': translate('OpenLP.DB', 'O'),
    'P': translate('OpenLP.DB', 'P'),
    'Q': translate('OpenLP.DB', 'Q'),
    'R': translate('OpenLP.DB', 'R'),
    'S': translate('OpenLP.DB', 'S'),
    'T': translate('OpenLP.DB', 'T'),
    'U': translate('OpenLP.DB', 'U'),
    'V': translate('OpenLP.DB', 'V'),
    'W': translate('OpenLP.DB', 'W'),
    'X': translate('OpenLP.DB', 'X'),
    'Y': translate('OpenLP.DB', 'Y'),
    'Z': translate('OpenLP.DB', 'Z')
}

# Due to the expanded nature of PJLink class 2 video sources,
# translate the individual types then build the video source
# dictionary from the translations.
PJLINK_DEFAULT_CODES = dict()
for source in PJLINK_DEFAULT_SOURCES:
    for item in PJLINK_DEFAULT_ITEMS:
        label = "{source}{item}".format(source=source, item=item)
        PJLINK_DEFAULT_CODES[label] = "{source} {item}".format(source=PJLINK_DEFAULT_SOURCES[source],
                                                               item=PJLINK_DEFAULT_ITEMS[item])
