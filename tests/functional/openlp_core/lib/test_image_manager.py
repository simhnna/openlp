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
Package to test the openlp.core.ui package.
"""
import os
import time
from threading import Lock
from unittest import TestCase, skip
from unittest.mock import MagicMock, patch

from PyQt5 import QtGui

from openlp.core.common.registry import Registry
from openlp.core.display.screens import ScreenList
from openlp.core.lib.imagemanager import ImageWorker, ImageManager, Priority, PriorityQueue
from tests.helpers.testmixin import TestMixin
from tests.utils.constants import RESOURCE_PATH

TEST_PATH = str(RESOURCE_PATH)


class TestImageWorker(TestCase, TestMixin):
    """
    Test all the methods in the ImageWorker class
    """
    def test_init(self):
        """
        Test the constructor of the ImageWorker
        """
        # GIVEN: An ImageWorker class and a mocked ImageManager
        mocked_image_manager = MagicMock()

        # WHEN: Creating the ImageWorker
        worker = ImageWorker(mocked_image_manager)

        # THEN: The image_manager attribute should be set correctly
        assert worker.image_manager is mocked_image_manager, \
            'worker.image_manager should have been the mocked_image_manager'

    @patch('openlp.core.lib.imagemanager.ThreadWorker.quit')
    def test_start(self, mocked_quit):
        """
        Test that the start() method of the image worker calls the process method and then emits quit.
        """
        # GIVEN: A mocked image_manager and a new image worker
        mocked_image_manager = MagicMock()
        worker = ImageWorker(mocked_image_manager)

        # WHEN: start() is called
        worker.start()

        # THEN: process() should have been called and quit should have been emitted
        mocked_image_manager.process.assert_called_once_with()
        mocked_quit.emit.assert_called_once_with()

    def test_stop(self):
        """
        Test that the stop method does the right thing
        """
        # GIVEN: A mocked image_manager and a worker
        mocked_image_manager = MagicMock()
        worker = ImageWorker(mocked_image_manager)

        # WHEN: The stop() method is called
        worker.stop()

        # THEN: The stop_manager attrivute should have been set to True
        assert mocked_image_manager.stop_manager is True, 'mocked_image_manager.stop_manager should have been True'


class TestPriorityQueue(TestCase, TestMixin):
    """
    Test the PriorityQueue class
    """
    @patch('openlp.core.lib.imagemanager.PriorityQueue.remove')
    @patch('openlp.core.lib.imagemanager.PriorityQueue.put')
    def test_modify_priority(self, mocked_put, mocked_remove):
        """
        Test the modify_priority() method of PriorityQueue
        """
        # GIVEN: An instance of a PriorityQueue and a mocked image
        mocked_image = MagicMock()
        mocked_image.priority = Priority.Normal
        mocked_image.secondary_priority = Priority.Low
        queue = PriorityQueue()

        # WHEN: modify_priority is called with a mocked image and a new priority
        queue.modify_priority(mocked_image, Priority.High)

        # THEN: The remove() method should have been called, image priority updated and put() called
        mocked_remove.assert_called_once_with(mocked_image)
        assert mocked_image.priority == Priority.High, 'The priority should have been Priority.High'
        mocked_put.assert_called_once_with((Priority.High, Priority.Low, mocked_image))

    def test_remove(self):
        """
        Test the remove() method of PriorityQueue
        """
        # GIVEN: A PriorityQueue instance with a mocked image and queue
        mocked_image = MagicMock()
        mocked_image.priority = Priority.High
        mocked_image.secondary_priority = Priority.Normal
        queue = PriorityQueue()

        # WHEN: An image is removed
        with patch.object(queue, 'queue') as mocked_queue:
            mocked_queue.__contains__.return_value = True
            queue.remove(mocked_image)

        # THEN: The mocked queue.remove() method should have been called
        mocked_queue.remove.assert_called_once_with((Priority.High, Priority.Normal, mocked_image))


@skip('Probably not going to use ImageManager in WebEngine/Reveal.js')
class TestImageManager(TestCase, TestMixin):

    def setUp(self):
        """
        Create the UI
        """
        Registry.create()
        self.setup_application()
        ScreenList.create(self.app.desktop())
        self.image_manager = ImageManager()
        self.lock = Lock()
        self.sleep_time = 0.1

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        self.image_manager.stop_manager = True
        del self.app

    @patch('openlp.core.lib.imagemanager.run_thread')
    def test_basic_image_manager(self, mocked_run_thread):
        """
        Test the Image Manager setup basic functionality
        """
        # GIVEN: the an image add to the image manager
        full_path = os.path.normpath(os.path.join(TEST_PATH, 'church.jpg'))
        self.image_manager.add_image(full_path, 'church.jpg', None)

        # WHEN the image is retrieved
        image = self.image_manager.get_image(full_path, 'church.jpg')

        # THEN returned record is a type of image
        assert isinstance(image, QtGui.QImage), 'The returned object should be a QImage'

        # WHEN: The image bytes are requested.
        byte_array = self.image_manager.get_image_bytes(full_path, 'church.jpg')

        # THEN: Type should be a str.
        assert isinstance(byte_array, str), 'The returned object should be a str'

        # WHEN the image is retrieved has not been loaded
        # THEN a KeyError is thrown
        with self.assertRaises(KeyError) as context:
            self.image_manager.get_image(TEST_PATH, 'church1.jpg')
        assert context.exception is not '', 'KeyError exception should have been thrown for missing image'

    @patch('openlp.core.lib.imagemanager.run_thread')
    def test_different_dimension_image(self, mocked_run_thread):
        """
        Test the Image Manager with dimensions
        """
        # GIVEN: add an image with specific dimensions
        full_path = os.path.normpath(os.path.join(TEST_PATH, 'church.jpg'))
        self.image_manager.add_image(full_path, 'church.jpg', None, 80, 80)

        # WHEN: the image is retrieved
        image = self.image_manager.get_image(full_path, 'church.jpg', 80, 80)

        # THEN: The return should be of type image
        assert isinstance(image, QtGui.QImage), 'The returned object should be a QImage'

        # WHEN: adding the same image with different dimensions
        self.image_manager.add_image(full_path, 'church.jpg', None, 100, 100)

        # THEN: the cache should contain two pictures
        assert len(self.image_manager._cache) == 2, \
            'Image manager should consider two dimensions of the same picture as different'

        # WHEN: adding the same image with first dimensions
        self.image_manager.add_image(full_path, 'church.jpg', None, 80, 80)

        # THEN: the cache should still contain only two pictures
        assert len(self.image_manager._cache) == 2, 'Same dimensions should not be added again'

        # WHEN: calling with correct image, but wrong dimensions
        with self.assertRaises(KeyError) as context:
            self.image_manager.get_image(full_path, 'church.jpg', 120, 120)
        assert context.exception is not '', 'KeyError exception should have been thrown for missing dimension'

    @patch('openlp.core.lib.imagemanager.resize_image')
    @patch('openlp.core.lib.imagemanager.image_to_byte')
    @patch('openlp.core.lib.imagemanager.run_thread')
    def test_process_cache(self, mocked_run_thread, mocked_image_to_byte, mocked_resize_image):
        """
        Test the process_cache method
        """
        # GIVEN: Mocked functions
        mocked_resize_image.side_effect = self.mocked_resize_image
        mocked_image_to_byte.side_effect = self.mocked_image_to_byte
        image1 = 'church.jpg'
        image2 = 'church2.jpg'
        image3 = 'church3.jpg'
        image4 = 'church4.jpg'

        # WHEN: Add the images. Then get the lock (=queue can not be processed).
        self.lock.acquire()
        self.image_manager.add_image(TEST_PATH, image1, None)
        self.image_manager.add_image(TEST_PATH, image2, None)

        # THEN: All images have been added to the queue, and only the first image is not be in the list anymore, but
        #  is being processed (see mocked methods/functions).
        # Note: Priority.Normal means, that the resize_image() was not completed yet (because afterwards the #
        # priority is adjusted to Priority.Lowest).
        assert self.get_image_priority(image1) == Priority.Normal, "image1's priority should be 'Priority.Normal'"
        assert self.get_image_priority(image2) == Priority.Normal, "image2's priority should be 'Priority.Normal'"

        # WHEN: Add more images.
        self.image_manager.add_image(TEST_PATH, image3, None)
        self.image_manager.add_image(TEST_PATH, image4, None)
        # Allow the queue to process.
        self.lock.release()
        # Request some "data".
        self.image_manager.get_image_bytes(TEST_PATH, image4)
        self.image_manager.get_image(TEST_PATH, image3)
        # Now the mocked methods/functions do not have to sleep anymore.
        self.sleep_time = 0
        # Wait for the queue to finish.
        while not self.image_manager._conversion_queue.empty():
            time.sleep(0.1)
        # Because empty() is not reliable, wait a litte; just to make sure.
        time.sleep(0.1)
        # THEN: The images' priority reflect how they were processed.
        assert self.image_manager._conversion_queue.qsize() == 0, "The queue should be empty."
        assert self.get_image_priority(image1) == Priority.Lowest, \
            "The image should have not been requested (=Lowest)"
        assert self.get_image_priority(image2) == Priority.Lowest, \
            "The image should have not been requested (=Lowest)"
        assert self.get_image_priority(image3) == Priority.Low, \
            "Only the QImage should have been requested (=Low)."
        assert self.get_image_priority(image4) == Priority.Urgent, \
            "The image bytes should have been requested (=Urgent)."

    def get_image_priority(self, image):
        """
        This is a help method to get the priority of the given image out of the image_manager's cache.

        NOTE: This requires, that the image has been added to the image manager using the *TEST_PATH*.

        :param image: The name of the image. E. g. ``image1``
        """
        return self.image_manager._cache[(TEST_PATH, image, -1, -1)].priority

    def mocked_resize_image(self, *args):
        """
        This is a mocked method, so that we can control the work flow of the image manager.
        """
        self.lock.acquire()
        self.lock.release()
        # The sleep time is adjusted in the test case.
        time.sleep(self.sleep_time)
        return QtGui.QImage()

    def mocked_image_to_byte(self, *args):
        """
        This is a mocked method, so that we can control the work flow of the image manager.
        """
        self.lock.acquire()
        self.lock.release()
        # The sleep time is adjusted in the test case.
        time.sleep(self.sleep_time)
        return ''
