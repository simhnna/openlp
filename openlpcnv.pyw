#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2010 Raoul Snyman                                        #
# Portions copyright (c) 2008-2010 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Christian Richter, Maikel Stuivenberg, Martin      #
# Thompson, Jon Tibble, Carsten Tinggaard                                     #
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

import os
import logging
import time
import subprocess
import codecs

if os.name == u'nt':
    import win32api
    import win32con
    from win32com.client import Dispatch

from openlp.migration.display import *
from openlp.migration.migratefiles import *
from openlp.migration.migratebibles import *
from openlp.migration.migratesongs import *

###############################################################################
# For Windows, requires SQLite ODBC Driver to be installed
# (uses sqlite.exe and sqlite3.exe)
#     http://www.ch-werner.de/sqliteodbc/
###############################################################################

logging.basicConfig(level=logging.DEBUG,
                format=u'%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                datefmt=u'%m-%d %H:%M',
                filename=u'openlp-migration.log',
                filemode=u'w')

class Migration(object):
    """
    A class to take care of the migration process.
    """
    def __init__(self):
        """
        Initialise the process.
        """
        self.display = Display()
        self.stime = time.strftime(u'%Y-%m-%d-%H%M%S', time.localtime())
        self.display.output(u'OpenLp v1.9.0 Migration Utility Started')

    def process(self):
        """
        Perform the conversion.
        """
        #MigrateFiles(self.display).process()
        MigrateSongs(self.display).process()
        MigrateBibles(self.display).process()

    def move_log_file(self):
        """
        Move the log file to a new location.
        """
        fname = u'openlp-migration.log'
        c = os.path.splitext(fname)
        b = (c[0]+'-'+ unicode(self.stime) + c[1])
        self.display.output(u'Logfile ' + b + u' generated')
        self.display.output(u'Migration Utility Finished ')
        os.rename(fname, b)

    def convert_file(self, inname, outname):
        """
        Convert a file from another encoding into UTF-8.

        ``inname``
            The name of the file to be opened and converted.

        ``outname``
            The output file name.
        """
        infile = codecs.open(inname, u'r', encoding=u'CP1252')
        writefile = codecs.open(outname, u'w', encoding=u'utf-8')
        for line in infile:
            writefile.write(line)
        infile.close()
        writefile.close()

    def convert_sqlite2_to_3(self, olddb, newdb):
        print u'Converting sqlite2 ' + olddb + ' to sqlite3 ' + newdb
        if os.name == u'nt':
            # we can't make this a raw unicode string as the \U within it causes much confusion
            hKey = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, u'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\SQLite ODBC Driver')
            value, type = win32api.RegQueryValueEx (hKey, u'UninstallString')
            sqlitepath, temp = os.path.split(value)
            sqliteexe = os.path.join(sqlitepath, u'sqlite.exe')
        else:
            sqliteexe = u'sqlite'
        cmd = u'%s "%s" .dump' % (sqliteexe, olddb)
        if os.name == u'nt':
            subprocess.call(cmd, stdout=open(u'sqlite.dmp', u'w'))
        else:
            subprocess.call(cmd, stdout=open(u'sqlite.dmp', u'w'), shell=True)
        self.convert_file(u'sqlite.dmp', u'sqlite3.dmp')
        if os.name == u'nt':
            sqlite3exe = os.path.join(sqlitepath, u'sqlite3.exe')
        else:
            sqlite3exe = u'sqlite3'
        if os.path.isfile(newdb):
            saveddb = newdb + self.stime
            os.rename(newdb, saveddb)
        cmd = '%s "%s"' % (sqlite3exe, newdb)
        if os.name == u'nt':
            subprocess.call(cmd, stdin=open(u'sqlite3.dmp', u'r'))
        else:
            subprocess.call(cmd, stdin=open(u'sqlite3.dmp', u'r'), shell=True)
        os.remove(u'sqlite.dmp')
        os.remove(u'sqlite3.dmp')

if __name__ == u'__main__':
    mig = Migration()
    songconfig = PluginConfig(u'Songs')
    newsongpath = songconfig.get_data_path()
    bibleconfig = PluginConfig(u'Bibles')
    newbiblepath = bibleconfig.get_data_path()
    if os.name == u'nt':
        if not os.path.isdir(newsongpath):
            os.makedirs(newsongpath)
        if not os.path.isdir(newbiblepath):
            os.makedirs(newbiblepath)
        ALL_USERS_APPLICATION_DATA = 35
        shell = Dispatch(u'Shell.Application')
        folder = shell.Namespace(ALL_USERS_APPLICATION_DATA)
        folderitem = folder.Self
        oldsongdb = os.path.join(folderitem.path, u'openlp.org', u'Data', u'songs.olp')
        oldbiblepath = os.path.join(folderitem.path, u'openlp.org', u'Data', u'Bibles')
    else:
        oldsongdb = os.path.join(newsongpath, u'songs.olp')
    newsongdb = os.path.join(newsongpath, u'songs.sqlite')
    mig.convert_sqlite2_to_3(oldsongdb, newsongdb)
    files = os.listdir(oldbiblepath)
    for file in files:
        f = os.path.splitext(os.path.basename(file))[0]
        if f != 'kjv':   #kjv bible has an autoincrement key not supported in sqlite3
            mig.convert_sqlite2_to_3(os.path.join(oldbiblepath, file),
                os.path.join(newbiblepath, f + u'.sqlite'))
    mig.process()
    #mig.move_log_file()
