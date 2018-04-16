# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2018 OpenLP Developers                                   #
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
The :mod:`common` module contains most of the components and libraries that make
OpenLP work.
"""
import hashlib
import importlib
import logging
import os
import re
import sys
import traceback
from ipaddress import IPv4Address, IPv6Address, AddressValueError
from shutil import which
from subprocess import check_output, CalledProcessError, STDOUT

from PyQt5 import QtGui
from PyQt5.QtCore import QCryptographicHash as QHash
from PyQt5.QtNetwork import QAbstractSocket, QHostAddress, QNetworkInterface
from chardet.universaldetector import UniversalDetector

log = logging.getLogger(__name__ + '.__init__')


FIRST_CAMEL_REGEX = re.compile('(.)([A-Z][a-z]+)')
SECOND_CAMEL_REGEX = re.compile('([a-z0-9])([A-Z])')
CONTROL_CHARS = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]')
INVALID_FILE_CHARS = re.compile(r'[\\/:\*\?"<>\|\+\[\]%]')
IMAGES_FILTER = None
REPLACMENT_CHARS_MAP = str.maketrans({'\u2018': '\'', '\u2019': '\'', '\u201c': '"', '\u201d': '"', '\u2026': '...',
                                      '\u2013': '-', '\u2014': '-', '\v': '\n\n', '\f': '\n\n'})
NEW_LINE_REGEX = re.compile(r' ?(\r\n?|\n) ?')
WHITESPACE_REGEX = re.compile(r'[ \t]+')


def get_local_ip4():
    """
    Creates a dictionary of local IPv4 interfaces on local machine.
    If no active interfaces available, returns a dict of localhost IPv4 information

    :returns: Dict of interfaces
    """
    # Get the local IPv4 active address(es) that are NOT localhost (lo or '127.0.0.1')
    log.debug('Getting local IPv4 interface(es) information')
    my_ip4 = {}
    for iface in QNetworkInterface.allInterfaces():
        if not iface.isValid() or not (iface.flags() & (QNetworkInterface.IsUp | QNetworkInterface.IsRunning)):
            continue
        for address in iface.addressEntries():
            ip = address.ip()
            # NOTE: Next line will skip if interface is localhost - keep for now until we decide about it later
            # if (ip.protocol() == QAbstractSocket.IPv4Protocol) and (ip != QHostAddress.LocalHost):
            if ip.protocol() == QAbstractSocket.IPv4Protocol:
                my_ip4[iface.name()] = {'ip': ip.toString(),
                                        'broadcast': address.broadcast().toString(),
                                        'netmask': address.netmask().toString(),
                                        'prefix': address.prefixLength(),
                                        'localnet': QHostAddress(address.netmask().toIPv4Address() &
                                                                 ip.toIPv4Address()).toString()
                                        }
                log.debug('Adding {iface} to active list'.format(iface=iface.name()))
    if len(my_ip4) == 1:
        if 'lo' in my_ip4:
            # No active interfaces - so leave localhost in there
            log.warning('No active IPv4 interfaces found except localhost')
    else:
        # Since we have a valid IP4 interface, remove localhost
        log.debug('Found at least one IPv4 interface, removing localhost')
        my_ip4.pop('lo')

    return my_ip4


def trace_error_handler(logger):
    """
    Log the calling path of an exception

    :param logger: logger to use so traceback is logged to correct class
    """
    log_string = "OpenLP Error trace"
    for tb in traceback.extract_stack():
        log_string += '\n   File {file} at line {line} \n\t called {data}'.format(file=tb[0], line=tb[1], data=tb[3])
    logger.error(log_string)


def extension_loader(glob_pattern, excluded_files=[]):
    """
    A utility function to find and load OpenLP extensions, such as plugins, presentation and media controllers and
    importers.

    :param str glob_pattern: A glob pattern used to find the extension(s) to be imported. Should be relative to the
        application directory. i.e. plugins/*/*plugin.py
    :param list[str] excluded_files: A list of file names to exclude that the glob pattern may find.
    :rtype: None
    """
    from openlp.core.common.applocation import AppLocation
    app_dir = AppLocation.get_directory(AppLocation.AppDir)
    for extension_path in app_dir.glob(glob_pattern):
        extension_path = extension_path.relative_to(app_dir)
        if extension_path.name in excluded_files:
            continue
        log.debug('Attempting to import %s', extension_path)
        module_name = path_to_module(extension_path)
        try:
            importlib.import_module(module_name)
        except (ImportError, OSError):
            # On some platforms importing vlc.py might cause OSError exceptions. (e.g. Mac OS X)
            log.warning('Failed to import {module_name} on path {extension_path}'
                        .format(module_name=module_name, extension_path=extension_path))


def path_to_module(path):
    """
    Convert a path to a module name (i.e openlp.core.common)

    :param openlp.core.common.path.Path path: The path to convert to a module name.
    :return: The module name.
    :rtype: str
    """
    module_path = path.with_suffix('')
    return 'openlp.' + '.'.join(module_path.parts)


def get_frozen_path(frozen_option, non_frozen_option):
    """
    Return a path based on the system status.

    :param frozen_option:
    :param non_frozen_option:
    """
    if hasattr(sys, 'frozen') and sys.frozen == 1:
        return frozen_option
    return non_frozen_option


class ThemeLevel(object):
    """
    Provides an enumeration for the level a theme applies to
    """
    Global = 1
    Service = 2
    Song = 3


class SlideLimits(object):
    """
    Provides an enumeration for behaviour of OpenLP at the end limits of each service item when pressing the up/down
    arrow keys
    """
    End = 1
    Wrap = 2
    Next = 3


def de_hump(name):
    """
    Change any Camel Case string to python string
    """
    sub_name = FIRST_CAMEL_REGEX.sub(r'\1_\2', name)
    return SECOND_CAMEL_REGEX.sub(r'\1_\2', sub_name).lower()


def is_win():
    """
    Returns true if running on a system with a nt kernel e.g. Windows, Wine

    :return: True if system is running a nt kernel false otherwise
    """
    return os.name.startswith('nt')


def is_macosx():
    """
    Returns true if running on a system with a darwin kernel e.g. Mac OS X

    :return: True if system is running a darwin kernel false otherwise
    """
    return sys.platform.startswith('darwin')


def is_linux():
    """
    Returns true if running on a system with a linux kernel e.g. Ubuntu, Debian, etc

    :return: True if system is running a linux kernel false otherwise
    """
    return sys.platform.startswith('linux')


def verify_ipv4(addr):
    """
    Validate an IPv4 address

    :param addr: Address to validate
    :returns: bool
    """
    try:
        IPv4Address(addr)
        return True
    except AddressValueError:
        return False


def verify_ipv6(addr):
    """
    Validate an IPv6 address

    :param addr: Address to validate
    :returns: bool
    """
    try:
        IPv6Address(addr)
        return True
    except AddressValueError:
        return False


def verify_ip_address(addr):
    """
    Validate an IP address as either IPv4 or IPv6

    :param addr: Address to validate
    :returns: bool
    """
    return True if verify_ipv4(addr) else verify_ipv6(addr)


def md5_hash(salt=None, data=None):
    """
    Returns the hashed output of md5sum on salt,data
    using Python3 hashlib

    :param salt: Initial salt
    :param data: OPTIONAL Data to hash
    :returns: str
    """
    log.debug('md5_hash(salt="{text}")'.format(text=salt))
    if not salt and not data:
        return None
    hash_obj = hashlib.new('md5')
    if salt:
        hash_obj.update(salt)
    if data:
        hash_obj.update(data)
    hash_value = hash_obj.hexdigest()
    log.debug('md5_hash() returning "{text}"'.format(text=hash_value))
    return hash_value


def qmd5_hash(salt=None, data=None):
    """
    Returns the hashed output of MD5Sum on salt, data
    using PyQt5.QCryptographicHash. Function returns a
    QByteArray instead of a text string.
    If you need a string instead, call with

        result = str(qmd5_hash(salt=..., data=...), encoding='ascii')

    :param salt: Initial salt
    :param data: OPTIONAL Data to hash
    :returns: QByteArray
    """
    log.debug('qmd5_hash(salt="{text}"'.format(text=salt))
    if salt is None and data is None:
        return None
    hash_obj = QHash(QHash.Md5)
    if salt:
        hash_obj.addData(salt)
    if data:
        hash_obj.addData(data)
    hash_value = hash_obj.result().toHex()
    log.debug('qmd5_hash() returning "{hash}"'.format(hash=hash_value))
    return hash_value


def clean_button_text(button_text):
    """
    Clean the & and other characters out of button text

    :param button_text: The text to clean
    """
    return button_text.replace('&', '').replace('< ', '').replace(' >', '')


def add_actions(target, actions):
    """
    Adds multiple actions to a menu or toolbar in one command.

    :param target: The menu or toolbar to add actions to
    :param actions: The actions to be added. An action consisting of the keyword ``None``
        will result in a separator being inserted into the target.
    """
    for action in actions:
        if action is None:
            target.addSeparator()
        else:
            target.addAction(action)


def get_uno_command(connection_type='pipe'):
    """
    Returns the UNO command to launch an libreoffice.org instance.
    """
    for command in ['libreoffice', 'soffice']:
        if which(command):
            break
    else:
        raise FileNotFoundError('Command not found')

    OPTIONS = '--nologo --norestore --minimized --nodefault --nofirststartwizard'
    if connection_type == 'pipe':
        CONNECTION = '"--accept=pipe,name=openlp_pipe;urp;"'
    else:
        CONNECTION = '"--accept=socket,host=localhost,port=2002;urp;"'
    return '{cmd} {opt} {conn}'.format(cmd=command, opt=OPTIONS, conn=CONNECTION)


def get_uno_instance(resolver, connection_type='pipe'):
    """
    Returns a running libreoffice.org instance.

    :param resolver: The UNO resolver to use to find a running instance.
    """
    log.debug('get UNO Desktop Openoffice - resolve')
    if connection_type == 'pipe':
        return resolver.resolve('uno:pipe,name=openlp_pipe;urp;StarOffice.ComponentContext')
    else:
        return resolver.resolve('uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext')


def get_filesystem_encoding():
    """
    Returns the name of the encoding used to convert Unicode filenames into system file names.
    """
    encoding = sys.getfilesystemencoding()
    if encoding is None:
        encoding = sys.getdefaultencoding()
    return encoding


def delete_file(file_path):
    """
    Deletes a file from the system.

    :param openlp.core.common.path.Path file_path: The file, including path, to delete.
    :return: True if the deletion was successful, or the file never existed. False otherwise.
    :rtype: bool
    """
    if not file_path:
        return False
    try:
        if file_path.exists():
            file_path.unlink()
        return True
    except OSError:
        log.exception('Unable to delete file {file_path}'.format(file_path=file_path))
        return False


def get_images_filter():
    """
    Returns a filter string for a file dialog containing all the supported image formats.
    """
    from openlp.core.common.i18n import translate
    global IMAGES_FILTER
    if not IMAGES_FILTER:
        log.debug('Generating images filter.')
        formats = list(map(bytes.decode, list(map(bytes, QtGui.QImageReader.supportedImageFormats()))))
        visible_formats = '(*.{text})'.format(text='; *.'.join(formats))
        actual_formats = '(*.{text})'.format(text=' *.'.join(formats))
        IMAGES_FILTER = '{text} {visible} {actual}'.format(text=translate('OpenLP', 'Image Files'),
                                                           visible=visible_formats,
                                                           actual=actual_formats)
    return IMAGES_FILTER


def is_not_image_file(file_path):
    """
    Validate that the file is not an image file.

    :param openlp.core.common.path.Path file_path: The file to be checked.
    :return: If the file is not an image
    :rtype: bool
    """
    if not (file_path and file_path.exists()):
        return True
    else:
        formats = [bytes(fmt).decode().lower() for fmt in QtGui.QImageReader.supportedImageFormats()]
        if file_path.suffix[1:].lower() in formats:
            return False
        return True


def clean_filename(filename):
    """
    Removes invalid characters from the given ``filename``.

    :param str filename:  The "dirty" file name to clean.
    :return: The cleaned string
    :rtype: str
    """
    return INVALID_FILE_CHARS.sub('_', CONTROL_CHARS.sub('', filename))


def check_binary_exists(program_path):
    """
    Function that checks whether a binary exists.

    :param openlp.core.common.path.Path program_path: The full path to the binary to check.
    :return: program output to be parsed
    :rtype: bytes
    """
    log.debug('testing program_path: {text}'.format(text=program_path))
    try:
        # Setup startupinfo options for check_output to avoid console popping up on windows
        if is_win():
            from subprocess import STARTUPINFO, STARTF_USESHOWWINDOW
            startupinfo = STARTUPINFO()
            startupinfo.dwFlags |= STARTF_USESHOWWINDOW
        else:
            startupinfo = None
        run_log = check_output([str(program_path), '--help'], stderr=STDOUT, startupinfo=startupinfo)
    except CalledProcessError as e:
        run_log = e.output
    except Exception:
        trace_error_handler(log)
        run_log = ''
    log.debug('check_output returned: {text}'.format(text=run_log))
    return run_log


def get_file_encoding(file_path):
    """
    Utility function to incrementally detect the file encoding.

    :param openlp.core.common.path.Path file_path: Filename for the file to determine the encoding for.
    :return: A dict with the keys 'encoding' and 'confidence'
    :rtype: dict[str, float]
    """
    detector = UniversalDetector()
    try:
        with file_path.open('rb') as detect_file:
            while not detector.done:
                chunk = detect_file.read(1024)
                if not chunk:
                    break
                detector.feed(chunk)
            detector.close()
        return detector.result
    except OSError:
        log.exception('Error detecting file encoding')


def normalize_str(string):
    """
    Normalize the supplied string. Remove unicode control chars and tidy up white space.

    :param str string: The string to normalize.
    :return: The normalized string
    :rtype: str
    """
    string = string.translate(REPLACMENT_CHARS_MAP)
    string = CONTROL_CHARS.sub('', string)
    string = NEW_LINE_REGEX.sub('\n', string)
    return WHITESPACE_REGEX.sub(' ', string)
