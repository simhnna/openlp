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
The :mod:`openlp.core.threading` module contains some common threading code
"""
from PyQt5 import QtCore


def run_thread(parent, worker, prefix='', auto_start=True):
    """
    Create a thread and assign a worker to it. This removes a lot of boilerplate code from the codebase.

    :param object parent: The parent object so that the thread and worker are not orphaned.
    :param QObject worker: A QObject-based worker object which does the actual work.
    :param str prefix: A prefix to be applied to the attribute names.
    :param bool auto_start: Automatically start the thread. Defaults to True.
    """
    # Set up attribute names
    thread_name = 'thread'
    worker_name = 'worker'
    if prefix:
        thread_name = '_'.join([prefix, thread_name])
        worker_name = '_'.join([prefix, worker_name])
    # Create the thread and add the thread and the worker to the parent
    thread = QtCore.QThread()
    setattr(parent, thread_name, thread)
    setattr(parent, worker_name, worker)
    # Move the worker into the thread's context
    worker.moveToThread(thread)
    # Connect slots and signals
    thread.started.connect(worker.start)
    worker.quit.connect(thread.quit)
    worker.quit.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)
    if auto_start:
        thread.start()
