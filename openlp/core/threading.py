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

from openlp.core.common.registry import Registry


class ThreadWorker(QtCore.QObject):
    """
    The :class:`~openlp.core.threading.ThreadWorker` class provides a base class for all worker objects
    """
    quit = QtCore.pyqtSignal()

    def start(self):
        """
        The start method is how the worker runs. Basically, put your code here.
        """
        raise NotImplementedError('Your base class needs to override this method and run self.quit.emit() at the end.')


def run_thread(worker, thread_name, can_start=True):
    """
    Create a thread and assign a worker to it. This removes a lot of boilerplate code from the codebase.

    :param QObject worker: A QObject-based worker object which does the actual work.
    :param str thread_name: The name of the thread, used to keep track of the thread.
    :param bool can_start: Start the thread. Defaults to True.
    """
    if not thread_name:
        raise ValueError('A thread_name is required when calling the "run_thread" function')
    main_window = Registry().get('main_window')
    if thread_name in main_window.threads:
        raise KeyError('A thread with the name "{}" has already been created, please use another'.format(thread_name))
    # Create the thread and add the thread and the worker to the parent
    thread = QtCore.QThread()
    main_window.threads[thread_name] = {
        'thread': thread,
        'worker': worker
    }
    # Move the worker into the thread's context
    worker.moveToThread(thread)
    # Connect slots and signals
    thread.started.connect(worker.start)
    worker.quit.connect(thread.quit)
    worker.quit.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)
    thread.finished.connect(make_remove_thread(thread_name))
    if can_start:
        thread.start()


def get_thread_worker(thread_name):
    """
    Get the worker by the thread name

    :param str thread_name: The name of the thread
    :returns ThreadWorker: The worker for this thread name
    """
    return Registry().get('main_window').threads.get(thread_name)


def is_thread_finished(thread_name):
    """
    Check if a thread is finished running.

    :param str thread_name: The name of the thread
    :returns bool: True if the thread is finished, False if it is still running
    """
    main_window = Registry().get('main_window')
    return thread_name not in main_window.threads or main_window.threads[thread_name]['thread'].isFinished()


def make_remove_thread(thread_name):
    """
    Create a function to remove the thread once the thread is finished.

    :param str thread_name: The name of the thread which should be removed from the thread registry.
    :returns function: A function which will remove the thread from the thread registry.
    """
    def remove_thread():
        """
        Stop and remove a registered thread

        :param str thread_name: The name of the thread to stop and remove
        """
        main_window = Registry().get('main_window')
        if thread_name in main_window.threads:
            del main_window.threads[thread_name]
    return remove_thread
