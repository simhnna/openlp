#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2010 Raoul Snyman                                        #
# Portions copyright (c) 2008-2010 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Meinert Jordan, Andreas Preikschat, Christian      #
# Richter, Philip Ridout, Maikel Stuivenberg, Martin Thompson, Jon Tibble,    #
# Carsten Tinggaard, Frode Woldsund                                           #
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
This script is used to maintain the translation files in OpenLP. It downloads
the latest translation files from the Pootle translation server, updates the
local translation files from both the source code and the files from Pootle,
and can also generate the compiled translation files.

Create New Language
-------------------

To create a new language, simply run this script with the ``-a`` command line
option::

    @:~$ ./translation_utils.py -a

Update Translation Files
------------------------

The best way to update the translations is to download the files from Pootle,
and then update the local files using both the downloaded files and the source.
This is done easily via the ``-d``, ``-p`` and ``-u`` options::

    @:~$ ./translation_utils.py -dpu

"""
import os
import urllib
import re

from optparse import OptionParser
from PyQt4 import QtCore
from BeautifulSoup import BeautifulSoup

SERVER_URL = u'http://pootle.projecthq.biz/export/openlp/'
IGNORED_PATHS = [u'scripts']
IGNORED_FILES = [u'setup.py']

verbose_mode = False

class Command(object):
    """
    Provide an enumeration of commands.
    """
    Download = 1
    Create = 2
    Prepare = 3
    Update = 4
    Generate = 5

class CommandStack(object):
    """
    This class provides an iterable stack.
    """
    def __init__(self):
        self.current_index = 0
        self.data = []

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        if self.data[index].get(u'arguments'):
            return self.data[index][u'command'], self.data[index][u'arguments']
        else:
            return self.data[index][u'command']

    def __iter__(self):
        return self

    def next(self):
        if self.current_index == len(self.data):
            raise StopIteration
        else:
            current_item = self.data[self.current_index][u'command']
            self.current_index += 1
            return current_item

    def append(self, command, **kwargs):
        data = {u'command': command}
        if u'arguments' in kwargs:
            data[u'arguments'] = kwargs[u'arguments']
        self.data.append(data)

    def reset(self):
        self.current_index = 0


def print_verbose(text):
    """
    This method checks to see if we are in verbose mode, and if so prints
    ``text`` out.

    ``text``
        The text to print.
    """
    global verbose_mode
    if verbose_mode:
        print u'    %s' % text

def run(command):
    """
    This method runs an external application.

    ``command``
        The command to run.
    """
    print_verbose(command)
    process = QtCore.QProcess()
    process.start(command)
    while (process.waitForReadyRead()):
        print_verbose(u'ReadyRead: %s' % QtCore.QString(process.readAll()))
    print_verbose(u'Error(s):\n%s' % process.readAllStandardError())
    print_verbose(u'Output:\n%s' % process.readAllStandardOutput())
    print u'   Done.'

def download_file(source_filename, dest_filename):
    """
    Download a file and save it to disk.

    ``source_filename``
        The file to download.

    ``dest_filename``
        The new local file name.
    """
    print_verbose(u'Downloading from: %s' % (SERVER_URL + source_filename))
    page = urllib.urlopen(SERVER_URL + source_filename)
    content = page.read().decode('utf8')
    page.close()
    file = open(dest_filename, u'w')
    file.write(content.encode('utf8'))
    file.close()

def download_translations():
    """
    This method downloads the translation files from the Pootle server.
    """
    print 'Download translation files from Pootle'
    page = urllib.urlopen(SERVER_URL)
    soup = BeautifulSoup(page)
    languages = soup.findAll(text=re.compile(r'.*\.ts'))
    for language in languages:
        filename = os.path.join(os.path.abspath(u'..'), u'resources', u'i18n',
            language)
        print_verbose(u'Get Translation File: %s' % filename)
        download_file(language, filename)
    print u'   Done.'

def prepare_project():
    """
    This method creates the project file needed to update the translation files
    and compile them into .qm files.
    """
    print u'Generating the openlp.pro file'
    lines = []
    start_dir = os.path.abspath(u'..')
    start_dir = start_dir + os.sep
    print_verbose(u'Starting directory: %s' % start_dir)
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            path = root.replace(start_dir, u'').replace(u'\\', u'/') #.replace(u'..', u'.')
            if file.startswith(u'hook-') or file.startswith(u'test_'):
               continue
            ignore = False
            for ignored_path in IGNORED_PATHS:
                if path.startswith(ignored_path):
                    ignore = True
                    break
            if ignore:
                continue
            ignore = False
            for ignored_file in IGNORED_FILES:
                if file == ignored_file:
                    ignore = True
                    break
            if ignore:
                continue
            if file.endswith(u'.py') or file.endswith(u'.pyw'):
                if path:
                    line = u'%s/%s' % (path, file)
                else:
                    line = file
                print_verbose(u'Parsing "%s"' % line)
                lines.append(u'SOURCES      += %s' % line)
            elif file.endswith(u'.ts'):
                line = u'%s/%s' % (path, file)
                print_verbose(u'Parsing "%s"' % line)
                lines.append(u'TRANSLATIONS += %s' % line)
    lines.sort()
    file = open(os.path.join(start_dir, u'openlp.pro'), u'w')
    file.write(u'\n'.join(lines).encode('utf8'))
    file.close()
    print u'   Done.'

def update_translations():
    print u'Update the translation files'
    if not os.path.exists(os.path.join(os.path.abspath(u'..'), u'openlp.pro')):
        print u'You have no generated a project file yet, please run this ' + \
            u'script with the -p option.'
        return
    else:
        os.chdir(os.path.abspath(u'..'))
        run(u'pylupdate4 -verbose -noobsolete openlp.pro')

def generate_binaries():
    print u'Generate the related *.qm files'
    if not os.path.exists(os.path.join(os.path.abspath(u'..'), u'openlp.pro')):
        print u'You have no generated a project file yet, please run this ' + \
            u'script with the -p option. It is also recommended that you ' + \
            u'this script with the -u option to update the translation ' + \
            u'files as well.'
        return
    else:
        os.chdir(os.path.abspath(u'..'))
        run(u'lrelease openlp.pro')

def create_translation(language):
    """
    This method creates a new translation file.

    ``language``
        The language file to create.
    """
    print "Create new Translation File"
    filename = os.path.join(os.path.abspath(u'..'), u'resources', u'i18n', language)
    download_file(u'en.ts', filename)
    print u'\n** Please Note **\n'
    print u'In order to get this file into OpenLP and onto the Pootle ' + \
        u'translation server you will need to subscribe to the OpenLP' + \
        u'Translators mailing list, and request that your language file ' + \
        u'be added to the project.\n'
    print u'   Done'

def process_stack(command_stack):
    """
    This method looks at the commands in the command stack, and processes them
    in the order they are in the stack.

    ``command_stack``
        The command stack to process.
    """
    if command_stack:
        print u'Processing %d commands...' % len(command_stack)
        for command in command_stack:
            print u'%d.' % (command_stack.current_index),
            if command == Command.Download:
                download_translations()
            elif command == Command.Prepare:
                prepare_project()
            elif command == Command.Update:
                update_translations()
            elif command == Command.Generate:
                generate_binaries()
            elif command == Command.Create:
                command, arguments = command_stack[command_stack.current_index]
                create_translation(*arguments)
        print u'Finished processing commands.'
    else:
        print u'No commands to process.'

def main():
    global verbose_mode
    # Set up command line options.
    usage = u'%prog [options]\nOptions are parsed in the order they are ' + \
        u'listed below. If no options are given, "-dpug" will be used.\n\n' + \
        u'This script is used to manage OpenLP\'s translation files.'
    parser = OptionParser(usage=usage)
    parser.add_option('-d', '--download-ts', dest='download',
        action='store_true', help='download language files from Pootle')
    parser.add_option('-c', '--create', dest=u'create', metavar='LANG',
        help='create a new translation file for language LANG, e.g. "en_GB"')
    parser.add_option('-p', '--prepare', dest='prepare', action='store_true',
        help='generate a project file, used to update the translations')
    parser.add_option('-u', '--update', action='store_true', dest='update',
        help='update translation files (needs a project file)')
    parser.add_option('-g', '--generate', dest='generate', action='store_true',
        help='compile .ts files into .qm files')
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
        help='show extra information while processing translations')
    (options, args) = parser.parse_args()
    # Create and populate the command stack
    command_stack = CommandStack()
    if options.download:
        command_stack.append(Command.Download)
    if options.create:
        command_stack.append(Command.Create, arguments=[options.create])
    if options.prepare:
        command_stack.append(Command.Prepare)
    if options.update:
        command_stack.append(Command.Update)
    if options.generate:
        command_stack.append(Command.Generate)
    verbose_mode = options.verbose
    if not command_stack:
        command_stack.append(Command.Download)
        command_stack.append(Command.Prepare)
        command_stack.append(Command.Update)
        command_stack.append(Command.Generate)
    # Process the commands
    process_stack(command_stack)

if __name__ == u'__main__':
    if os.path.split(os.path.abspath(u'.'))[1] != u'scripts':
        print u'You need to run this script from the scripts directory.'
    else:
        main()

