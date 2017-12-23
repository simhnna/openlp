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
Package to test the openlp.core.lib package.
"""
import os
from unittest import TestCase
from unittest.mock import MagicMock, patch

from PyQt5 import QtCore, QtGui

from openlp.core.common.path import Path
from openlp.core.lib import FormattingTags, build_icon, check_item_selected, clean_tags, compare_chord_lyric, \
    create_separated_list, create_thumb, expand_chords, expand_chords_for_printing, expand_tags, find_formatting_tags, \
    get_text_file_string, image_to_byte, resize_image, str_to_bool, validate_thumb

TEST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'resources'))


class TestLib(TestCase):

    def test_str_to_bool_with_bool_true(self):
        """
        Test the str_to_bool function with boolean input of True
        """
        # GIVEN: A boolean value set to true
        true_boolean = True

        # WHEN: We "convert" it to a bool
        true_result = str_to_bool(true_boolean)

        # THEN: We should get back a True bool
        assert isinstance(true_result, bool), 'The result should be a boolean'
        assert true_result is True, 'The result should be True'

    def test_str_to_bool_with_bool_false(self):
        """
        Test the str_to_bool function with boolean input of False
        """
        # GIVEN: A boolean value set to false
        false_boolean = False

        # WHEN: We "convert" it to a bool
        false_result = str_to_bool(false_boolean)

        # THEN: We should get back a True bool
        assert isinstance(false_result, bool), 'The result should be a boolean'
        assert false_result is False, 'The result should be True'

    def test_str_to_bool_with_integer(self):
        """
        Test the str_to_bool function with an integer input
        """
        # GIVEN: An integer value
        int_string = 1

        # WHEN: we convert it to a bool
        int_result = str_to_bool(int_string)

        # THEN: we should get back a false
        assert int_result is False, 'The result should be False'

    def test_str_to_bool_with_invalid_string(self):
        """
        Test the str_to_bool function with an invalid string
        """
        # GIVEN: An string value with completely invalid input
        invalid_string = 'my feet are wet'

        # WHEN: we convert it to a bool
        str_result = str_to_bool(invalid_string)

        # THEN: we should get back a false
        assert str_result is False, 'The result should be False'

    def test_str_to_bool_with_string_false(self):
        """
        Test the str_to_bool function with a string saying "false"
        """
        # GIVEN: A string set to "false"
        false_string = 'false'

        # WHEN: we convert it to a bool
        false_result = str_to_bool(false_string)

        # THEN: we should get back a false
        assert false_result is False, 'The result should be False'

    def test_str_to_bool_with_string_no(self):
        """
        Test the str_to_bool function with a string saying "NO"
        """
        # GIVEN: An string set to "NO"
        no_string = 'NO'

        # WHEN: we convert it to a bool
        str_result = str_to_bool(no_string)

        # THEN: we should get back a false
        assert str_result is False, 'The result should be False'

    def test_str_to_bool_with_true_string_value(self):
        """
        Test the str_to_bool function with a string set to "True"
        """
        # GIVEN: A string set to "True"
        true_string = 'True'

        # WHEN: we convert it to a bool
        true_result = str_to_bool(true_string)

        # THEN: we should get back a true
        assert true_result is True, 'The result should be True'

    def test_str_to_bool_with_yes_string_value(self):
        """
        Test the str_to_bool function with a string set to "yes"
        """
        # GIVEN: An string set to "yes"
        yes_string = 'yes'

        # WHEN: we convert it to a bool
        str_result = str_to_bool(yes_string)

        # THEN: we should get back a true
        assert str_result is True, 'The result should be True'

    def test_get_text_file_string_no_file(self):
        """
        Test the get_text_file_string() function when a file does not exist
        """
        # GIVEN: A patched is_file which returns False, and a file path
        with patch.object(Path, 'is_file', return_value=False):
            file_path = Path('testfile.txt')

            # WHEN: get_text_file_string is called
            result = get_text_file_string(file_path)

            # THEN: The result should be False
            file_path.is_file.assert_called_with()
            assert result is False, 'False should be returned if no file exists'

    def test_get_text_file_string_read_error(self):
        """
        Test the get_text_file_string() method when a read error happens
        """
        # GIVEN: A patched open which raises an exception and is_file which returns True
        with patch.object(Path, 'is_file'), \
                patch.object(Path, 'open'):
            file_path = Path('testfile.txt')
            file_path.is_file.return_value = True
            file_path.open.side_effect = OSError()

            # WHEN: get_text_file_string is called
            result = get_text_file_string(file_path)

            # THEN: None should be returned
            file_path.is_file.assert_called_once_with()
            file_path.open.assert_called_once_with('r', encoding='utf-8')
            assert result is None, 'None should be returned if the file cannot be opened'

    def test_get_text_file_string_decode_error(self):
        """
        Test the get_text_file_string() method when the contents cannot be decoded
        """
        self.skipTest('Impossible to test due to conflicts when mocking out the "open" function')

    def test_build_icon_with_qicon(self):
        """
        Test the build_icon() function with a QIcon instance
        """
        # GIVEN: An icon QIcon
        icon = QtGui.QIcon()

        # WHEN: We pass a QIcon instance in
        result = build_icon(icon)

        # THEN: The result should be the same icon as we passed in
        assert icon is result, 'The result should be the same icon as we passed in'

    def test_build_icon_with_resource(self):
        """
        Test the build_icon() function with a resource URI
        """
        with patch('openlp.core.lib.QtGui') as MockedQtGui, \
                patch('openlp.core.lib.QtGui.QPixmap') as MockedQPixmap:
            # GIVEN: A mocked QIcon and a mocked QPixmap
            MockedQtGui.QIcon = MagicMock
            MockedQtGui.QIcon.Normal = 1
            MockedQtGui.QIcon.Off = 2
            MockedQPixmap.return_value = 'mocked_pixmap'
            resource_uri = ':/resource/uri'

            # WHEN: We pass a QIcon instance in
            result = build_icon(resource_uri)

            # THEN: The result should be our mocked QIcon
            MockedQPixmap.assert_called_with(resource_uri)
            # There really should be more assert statements here but due to type checking and things they all break. The
            # best we can do is to assert that we get back a MagicMock object.
            assert isinstance(result, MagicMock), 'The result should be a MagicMock, because we mocked it out'

    def test_image_to_byte(self):
        """
        Test the image_to_byte() function
        """
        with patch('openlp.core.lib.QtCore') as MockedQtCore:
            # GIVEN: A set of mocked-out Qt classes
            mocked_byte_array = MagicMock()
            MockedQtCore.QByteArray.return_value = mocked_byte_array
            mocked_buffer = MagicMock()
            MockedQtCore.QBuffer.return_value = mocked_buffer
            MockedQtCore.QIODevice.WriteOnly = 'writeonly'
            mocked_image = MagicMock()

            # WHEN: We convert an image to a byte array
            result = image_to_byte(mocked_image, base_64=False)

            # THEN: We should receive the mocked_buffer
            MockedQtCore.QByteArray.assert_called_with()
            MockedQtCore.QBuffer.assert_called_with(mocked_byte_array)
            mocked_buffer.open.assert_called_with('writeonly')
            mocked_image.save.assert_called_with(mocked_buffer, "PNG")
            assert mocked_byte_array.toBase64.called is False
            assert mocked_byte_array == result, 'The mocked out byte array should be returned'

    def test_image_to_byte_base_64(self):
        """
        Test the image_to_byte() function
        """
        with patch('openlp.core.lib.QtCore') as MockedQtCore:
            # GIVEN: A set of mocked-out Qt classes
            mocked_byte_array = MagicMock()
            MockedQtCore.QByteArray.return_value = mocked_byte_array
            mocked_byte_array.toBase64.return_value = QtCore.QByteArray(b'base64mock')
            mocked_buffer = MagicMock()
            MockedQtCore.QBuffer.return_value = mocked_buffer
            MockedQtCore.QIODevice.WriteOnly = 'writeonly'
            mocked_image = MagicMock()

            # WHEN: We convert an image to a byte array
            result = image_to_byte(mocked_image)

            # THEN: We should receive a value of 'base64mock'
            MockedQtCore.QByteArray.assert_called_with()
            MockedQtCore.QBuffer.assert_called_with(mocked_byte_array)
            mocked_buffer.open.assert_called_with('writeonly')
            mocked_image.save.assert_called_with(mocked_buffer, "PNG")
            mocked_byte_array.toBase64.assert_called_with()
            assert 'base64mock' == result, 'The result should be the return value of the mocked out base64 method'

    def test_create_thumb_with_size(self):
        """
        Test the create_thumb() function with a given size.
        """
        # GIVEN: An image to create a thumb of.
        image_path = Path(TEST_PATH, 'church.jpg')
        thumb_path = Path(TEST_PATH, 'church_thumb.jpg')
        thumb_size = QtCore.QSize(10, 20)

        # Remove the thumb so that the test actually tests if the thumb will be created. Maybe it was not deleted in the
        # last test.
        try:
            thumb_path.unlink()
        except:
            pass

        # Only continue when the thumb does not exist.
        assert thumb_path.exists() is False, 'Test was not run, because the thumb already exists.'

        # WHEN: Create the thumb.
        icon = create_thumb(image_path, thumb_path, size=thumb_size)

        # THEN: Check if the thumb was created and scaled to the given size.
        assert thumb_path.exists() is True, 'Test was not ran, because the thumb already exists'
        assert isinstance(icon, QtGui.QIcon), 'The icon should be a QIcon'
        assert icon.isNull() is False, 'The icon should not be null'
        assert thumb_size == QtGui.QImageReader(str(thumb_path)).size(), 'The thumb should have the given size'

        # Remove the thumb so that the test actually tests if the thumb will be created.
        try:
            thumb_path.unlink()
        except:
            pass

    def test_create_thumb_no_size(self):
        """
        Test the create_thumb() function with no size specified.
        """
        # GIVEN: An image to create a thumb of.
        image_path = Path(TEST_PATH, 'church.jpg')
        thumb_path = Path(TEST_PATH, 'church_thumb.jpg')
        expected_size = QtCore.QSize(63, 88)

        # Remove the thumb so that the test actually tests if the thumb will be created. Maybe it was not deleted in the
        # last test.
        try:
            thumb_path.unlink()
        except:
            pass

        # Only continue when the thumb does not exist.
        assert thumb_path.exists() is False, 'Test was not run, because the thumb already exists.'

        # WHEN: Create the thumb.
        icon = create_thumb(image_path, thumb_path)

        # THEN: Check if the thumb was created, retaining its aspect ratio.
        assert thumb_path.exists() is True, 'Test was not ran, because the thumb already exists'
        assert isinstance(icon, QtGui.QIcon), 'The icon should be a QIcon'
        assert icon.isNull() is False, 'The icon should not be null'
        assert expected_size == QtGui.QImageReader(str(thumb_path)).size(), 'The thumb should have the given size'

        # Remove the thumb so that the test actually tests if the thumb will be created.
        try:
            thumb_path.unlink()
        except:
            pass

    def test_create_thumb_invalid_size(self):
        """
        Test the create_thumb() function with invalid size specified.
        """
        # GIVEN: An image to create a thumb of.
        image_path = Path(TEST_PATH, 'church.jpg')
        thumb_path = Path(TEST_PATH, 'church_thumb.jpg')
        thumb_size = QtCore.QSize(-1, -1)
        expected_size = QtCore.QSize(63, 88)

        # Remove the thumb so that the test actually tests if the thumb will be created. Maybe it was not deleted in the
        # last test.
        try:
            thumb_path.unlink()
        except:
            pass

        # Only continue when the thumb does not exist.
        assert thumb_path.exists() is False, 'Test was not run, because the thumb already exists.'

        # WHEN: Create the thumb.
        icon = create_thumb(image_path, thumb_path, size=thumb_size)

        # THEN: Check if the thumb was created, retaining its aspect ratio.
        assert thumb_path.exists() is True, 'Test was not ran, because the thumb already exists'
        assert isinstance(icon, QtGui.QIcon), 'The icon should be a QIcon'
        assert icon.isNull() is False, 'The icon should not be null'
        assert expected_size == QtGui.QImageReader(str(thumb_path)).size(), 'The thumb should have the given size'

        # Remove the thumb so that the test actually tests if the thumb will be created.
        try:
            thumb_path.unlink()
        except:
            pass

    def test_create_thumb_width_only(self):
        """
        Test the create_thumb() function with a size of only width specified.
        """
        # GIVEN: An image to create a thumb of.
        image_path = Path(TEST_PATH, 'church.jpg')
        thumb_path = Path(TEST_PATH, 'church_thumb.jpg')
        thumb_size = QtCore.QSize(100, -1)
        expected_size = QtCore.QSize(100, 137)

        # Remove the thumb so that the test actually tests if the thumb will be created. Maybe it was not deleted in the
        # last test.
        try:
            thumb_path.unlink()
        except:
            pass

        # Only continue when the thumb does not exist.
        assert thumb_path.exists() is False, 'Test was not run, because the thumb already exists.'

        # WHEN: Create the thumb.
        icon = create_thumb(image_path, thumb_path, size=thumb_size)

        # THEN: Check if the thumb was created, retaining its aspect ratio.
        assert thumb_path.exists() is True, 'Test was not ran, because the thumb already exists'
        assert isinstance(icon, QtGui.QIcon), 'The icon should be a QIcon'
        assert icon.isNull() is False, 'The icon should not be null'
        assert expected_size == QtGui.QImageReader(str(thumb_path)).size(), 'The thumb should have the given size'

        # Remove the thumb so that the test actually tests if the thumb will be created.
        try:
            thumb_path.unlink()
        except:
            pass

    def test_create_thumb_height_only(self):
        """
        Test the create_thumb() function with a size of only height specified.
        """
        # GIVEN: An image to create a thumb of.
        image_path = Path(TEST_PATH, 'church.jpg')
        thumb_path = Path(TEST_PATH, 'church_thumb.jpg')
        thumb_size = QtCore.QSize(-1, 100)
        expected_size = QtCore.QSize(72, 100)

        # Remove the thumb so that the test actually tests if the thumb will be created. Maybe it was not deleted in the
        # last test.
        try:
            thumb_path.unlink()
        except:
            pass

        # Only continue when the thumb does not exist.
        assert thumb_path.exists() is False, 'Test was not run, because the thumb already exists.'

        # WHEN: Create the thumb.
        icon = create_thumb(image_path, thumb_path, size=thumb_size)

        # THEN: Check if the thumb was created, retaining its aspect ratio.
        assert thumb_path.exists() is True, 'Test was not ran, because the thumb already exists'
        assert isinstance(icon, QtGui.QIcon), 'The icon should be a QIcon'
        assert icon.isNull() is False, 'The icon should not be null'
        assert expected_size == QtGui.QImageReader(str(thumb_path)).size(), 'The thumb should have the given size'

        # Remove the thumb so that the test actually tests if the thumb will be created.
        try:
            thumb_path.unlink()
        except:
            pass

    def test_create_thumb_empty_img(self):
        """
        Test the create_thumb() function with a size of only height specified.
        """
        # GIVEN: An image to create a thumb of.
        image_path = Path(TEST_PATH, 'church.jpg')
        thumb_path = Path(TEST_PATH, 'church_thumb.jpg')
        thumb_size = QtCore.QSize(-1, 100)
        expected_size_1 = QtCore.QSize(88, 88)
        expected_size_2 = QtCore.QSize(100, 100)

        # Remove the thumb so that the test actually tests if the thumb will be created. Maybe it was not deleted in the
        # last test.
        try:
            thumb_path.unlink()
        except:
            pass

        # Only continue when the thumb does not exist.
        assert thumb_path.exists() is False, 'Test was not run, because the thumb already exists.'

        # WHEN: Create the thumb.
        with patch('openlp.core.lib.QtGui.QImageReader.size') as mocked_size:
            mocked_size.return_value = QtCore.QSize(0, 0)
            icon = create_thumb(image_path, thumb_path, size=None)

        # THEN: Check if the thumb was created with aspect ratio of 1.
        assert thumb_path.exists() is True, 'Test was not ran, because the thumb already exists'
        assert isinstance(icon, QtGui.QIcon), 'The icon should be a QIcon'
        assert icon.isNull() is False, 'The icon should not be null'
        assert expected_size_1 == QtGui.QImageReader(str(thumb_path)).size(), 'The thumb should have the given size'

        # WHEN: Create the thumb.
        with patch('openlp.core.lib.QtGui.QImageReader.size') as mocked_size:
            mocked_size.return_value = QtCore.QSize(0, 0)
            icon = create_thumb(image_path, thumb_path, size=thumb_size)

        # THEN: Check if the thumb was created with aspect ratio of 1.
        assert isinstance(icon, QtGui.QIcon), 'The icon should be a QIcon'
        assert icon.isNull() is False, 'The icon should not be null'
        assert expected_size_2 == QtGui.QImageReader(str(thumb_path)).size(), 'The thumb should have the given size'

        # Remove the thumb so that the test actually tests if the thumb will be created.
        try:
            thumb_path.unlink()
        except:
            pass

    def test_check_item_selected_true(self):
        """
        Test that the check_item_selected() function returns True when there are selected indexes
        """
        # GIVEN: A mocked out QtWidgets module and a list widget with selected indexes
        # mocked_QtWidgets = patch('openlp.core.lib.QtWidgets')
        mocked_list_widget = MagicMock()
        mocked_list_widget.selectedIndexes.return_value = True
        message = 'message'

        # WHEN: We check if there are selected items
        result = check_item_selected(mocked_list_widget, message)

        # THEN: The selectedIndexes function should have been called and the result should be true
        mocked_list_widget.selectedIndexes.assert_called_with()
        assert result is True, 'The result should be True'

    def test_check_item_selected_false(self):
        """
        Test that the check_item_selected() function returns False when there are no selected indexes.
        """
        # GIVEN: A mocked out QtWidgets module and a list widget with selected indexes
        with patch('openlp.core.lib.QtWidgets') as MockedQtWidgets, \
                patch('openlp.core.lib.translate') as mocked_translate:
            mocked_translate.return_value = 'mocked translate'
            mocked_list_widget = MagicMock()
            mocked_list_widget.selectedIndexes.return_value = False
            mocked_list_widget.parent.return_value = 'parent'
            message = 'message'

            # WHEN: We check if there are selected items
            result = check_item_selected(mocked_list_widget, message)

            # THEN: The selectedIndexes function should have been called and the result should be true
            mocked_list_widget.selectedIndexes.assert_called_with()
            MockedQtWidgets.QMessageBox.information.assert_called_with('parent', 'mocked translate', 'message')
            assert result is False, 'The result should be False'

    def test_clean_tags(self):
        """
        Test clean_tags() method.
        """
        with patch('openlp.core.lib.FormattingTags.get_html_tags') as mocked_get_tags:
            # GIVEN: Mocked get_html_tags() method.
            mocked_get_tags.return_value = [{
                'desc': 'Black',
                'start tag': '{b}',
                'start html': '<span style="-webkit-text-fill-color:black">',
                'end tag': '{/b}', 'end html': '</span>', 'protected': True,
                'temporary': False
            }]
            string_to_pass = 'ASDF<br>foo{br}bar&nbsp;{b}black{/b}'
            wanted_string = 'ASDF\nfoo\nbar black'

            # WHEN: Clean the string.
            result_string = clean_tags(string_to_pass)

            # THEN: The strings should be identical.
            assert wanted_string == result_string, 'The strings should be identical'

    def test_expand_tags(self):
        """
        Test the expand_tags() method.
        """
        with patch('openlp.core.lib.FormattingTags.get_html_tags') as mocked_get_tags:
            # GIVEN: Mocked get_html_tags() method.
            mocked_get_tags.return_value = [
                {
                    'desc': 'Black',
                    'start tag': '{b}',
                    'start html': '<span style="-webkit-text-fill-color:black">',
                    'end tag': '{/b}', 'end html': '</span>', 'protected': True,
                    'temporary': False
                },
                {
                    'desc': 'Yellow',
                    'start tag': '{y}',
                    'start html': '<span style="-webkit-text-fill-color:yellow">',
                    'end tag': '{/y}', 'end html': '</span>', 'protected': True,
                    'temporary': False
                },
                {
                    'desc': 'Green',
                    'start tag': '{g}',
                    'start html': '<span style="-webkit-text-fill-color:green">',
                    'end tag': '{/g}', 'end html': '</span>', 'protected': True,
                    'temporary': False
                }
            ]
            string_to_pass = '{b}black{/b}{y}yellow{/y}'
            wanted_string = '<span style="-webkit-text-fill-color:black">black</span>' + \
                '<span style="-webkit-text-fill-color:yellow">yellow</span>'

            # WHEN: Replace the tags.
            result_string = expand_tags(string_to_pass)

            # THEN: The strings should be identical.
            assert wanted_string == result_string, 'The strings should be identical.'

    def test_validate_thumb_file_does_not_exist(self):
        """
        Test the validate_thumb() function when the thumbnail does not exist
        """
        # GIVEN: A mocked out os module, with path.exists returning False, and fake paths to a file and a thumb
        with patch.object(Path, 'exists', return_value=False):
            file_path = Path('path', 'to', 'file')
            thumb_path = Path('path', 'to', 'thumb')

            # WHEN: we run the validate_thumb() function
            result = validate_thumb(file_path, thumb_path)

            # THEN: we should have called a few functions, and the result should be False
            thumb_path.exists.assert_called_once_with()
            assert result is False, 'The result should be False'

    def test_validate_thumb_file_exists_and_newer(self):
        """
        Test the validate_thumb() function when the thumbnail exists and has a newer timestamp than the file
        """
        with patch.object(Path, 'exists'), patch.object(Path, 'stat'):
            # GIVEN: Mocked file_path and thumb_path which return different values fo the modified times
            file_path = MagicMock(**{'stat.return_value': MagicMock(st_mtime=10)})
            thumb_path = MagicMock(**{'exists.return_value': True, 'stat.return_value': MagicMock(st_mtime=11)})

            # WHEN: we run the validate_thumb() function
            result = validate_thumb(file_path, thumb_path)

            # THEN: `validate_thumb` should return True
            assert result is True

    def test_validate_thumb_file_exists_and_older(self):
        """
        Test the validate_thumb() function when the thumbnail exists but is older than the file
        """
        # GIVEN: Mocked file_path and thumb_path which return different values fo the modified times
        file_path = MagicMock(**{'stat.return_value': MagicMock(st_mtime=10)})
        thumb_path = MagicMock(**{'exists.return_value': True, 'stat.return_value': MagicMock(st_mtime=9)})

        # WHEN: we run the validate_thumb() function
        result = validate_thumb(file_path, thumb_path)

        # THEN: `validate_thumb` should return False
        thumb_path.stat.assert_called_once_with()
        assert result is False, 'The result should be False'

    def test_resize_thumb(self):
        """
        Test the resize_thumb() function
        """
        # GIVEN: A path to an image.
        image_path = os.path.join(TEST_PATH, 'church.jpg')
        wanted_width = 777
        wanted_height = 72
        # We want the background to be white.
        wanted_background_hex = '#FFFFFF'
        wanted_background_rgb = QtGui.QColor(wanted_background_hex).rgb()

        # WHEN: Resize the image and add a background.
        image = resize_image(image_path, wanted_width, wanted_height, wanted_background_hex)

        # THEN: Check if the size is correct and the background was set.
        result_size = image.size()
        assert wanted_height == result_size.height(), 'The image should have the requested height.'
        assert wanted_width == result_size.width(), 'The image should have the requested width.'
        assert image.pixel(0, 0) == wanted_background_rgb, 'The background should be white.'

    def test_resize_thumb_ignoring_aspect_ratio(self):
        """
        Test the resize_thumb() function ignoring aspect ratio
        """
        # GIVEN: A path to an image.
        image_path = os.path.join(TEST_PATH, 'church.jpg')
        wanted_width = 1000
        wanted_height = 1000
        # We want the background to be white.
        wanted_background_hex = '#FFFFFF'
        wanted_background_rgb = QtGui.QColor(wanted_background_hex).rgb()

        # WHEN: Resize the image and add a background.
        image = resize_image(image_path, wanted_width, wanted_height, wanted_background_hex, True)

        # THEN: Check if the size is correct and the background was set.
        result_size = image.size()
        assert wanted_height == result_size.height(), 'The image should have the requested height.'
        assert wanted_width == result_size.width(), 'The image should have the requested width.'
        assert image.pixel(0, 0) == wanted_background_rgb, 'The background should be white.'

    @patch('openlp.core.lib.QtCore.QLocale.createSeparatedList')
    def test_create_separated_list_qlocate(self, mocked_createSeparatedList):
        """
        Test the create_separated_list function using the Qt provided method
        """
        # GIVEN: A list of strings and the mocked Qt module.
        mocked_createSeparatedList.return_value = 'Author 1, Author 2, and Author 3'
        string_list = ['Author 1', 'Author 2', 'Author 3']

        # WHEN: We get a string build from the entries it the list and a separator.
        string_result = create_separated_list(string_list)

        # THEN: We should have "Author 1, Author 2, and Author 3"
        assert string_result == 'Author 1, Author 2 and Author 3', \
            'The string should be "Author 1, Author 2, and Author 3".'

    def test_create_separated_list_empty_list(self):
        """
        Test the create_separated_list function with an empty list
        """
        # GIVEN: An empty list and the mocked Qt module.
        string_list = []

        # WHEN: We get a string build from the entries it the list and a separator.
        string_result = create_separated_list(string_list)

        # THEN: We shoud have an emptry string.
        assert string_result == '', 'The string sould be empty.'

    def test_create_separated_list_with_one_item(self):
        """
        Test the create_separated_list function with a list consisting of only one entry
        """
        # GIVEN: A list with a string.
        string_list = ['Author 1']

        # WHEN: We get a string build from the entries it the list and a separator.
        string_result = create_separated_list(string_list)

        # THEN: We should have "Author 1"
        assert string_result == 'Author 1', 'The string should be "Author 1".'

    def test_create_separated_list_with_two_items(self):
        """
        Test the create_separated_list function with a list of two entries
        """
        # GIVEN: A list with two strings.
        string_list = ['Author 1', 'Author 2']

        # WHEN: We get a string build from the entries it the list and a seperator.
        string_result = create_separated_list(string_list)

        # THEN: We should have "Author 1 and Author 2"
        assert string_result == 'Author 1 and Author 2', 'The string should be "Author 1 and Author 2".'

    def test_create_separated_list_with_three_items(self):
        """
        Test the create_separated_list function with a list of three items
        """
        # GIVEN: A list with three strings.
        string_list = ['Author 1', 'Author 2', 'Author 3']

        # WHEN: We get a string build from the entries it the list and a seperator.
        string_result = create_separated_list(string_list)

        # THEN: We should have "Author 1, Author 2 and Author 3"
        assert string_result == 'Author 1, Author 2 and Author 3', \
            'The string should be "Author 1, Author 2, and Author 3".'

    def test_expand_chords(self):
        """
        Test that the expanding of chords works as expected.
        """
        # GIVEN: A lyrics-line with chords
        text_with_chords = 'H[C]alleluya.[F] [G]'

        # WHEN: Expanding the chords
        text_with_expanded_chords = expand_chords(text_with_chords)

        # THEN: We should get html that looks like below
        expected_html = '<span class="chordline firstchordline">H<span class="chord"><span><strong>C</strong></span>' \
                        '</span>alleluya.<span class="chord"><span><strong>F</strong></span></span><span class="ws">' \
                        '&nbsp;&nbsp;</span> <span class="chord"><span><strong>G</strong></span></span></span>'
        assert expected_html == text_with_expanded_chords, 'The expanded chords should look as expected!'

    def test_expand_chords2(self):
        """
        Test that the expanding of chords works as expected when special chars are involved.
        """
        # GIVEN: A lyrics-line with chords
        text_with_chords = "I[D]'M NOT MOVED BY WHAT I SEE HALLE[F]LUJA[C]H"

        # WHEN: Expanding the chords
        text_with_expanded_chords = expand_tags(text_with_chords, True)

        # THEN: We should get html that looks like below
        expected_html = '<span class="chordline firstchordline">I<span class="chord"><span><strong>D</strong></span>' \
                        '</span>&#x27;M NOT MOVED BY WHAT I SEE HALLE<span class="chord"><span><strong>F</strong>' \
                        '</span></span>LUJA<span class="chord"><span><strong>C</strong></span></span>H</span>'
        assert expected_html == text_with_expanded_chords, 'The expanded chords should look as expected!'

    def test_compare_chord_lyric_short_chord(self):
        """
        Test that the chord/lyric comparing works.
        """
        # GIVEN: A chord and some lyric
        chord = 'C'
        lyrics = 'alleluya'

        # WHEN: Comparing the chord and lyrics
        ret = compare_chord_lyric(chord, lyrics)

        # THEN: The returned value should 0 because the lyric is longer than the chord
        assert 0 == ret, 'The returned value should 0 because the lyric is longer than the chord'

    def test_compare_chord_lyric_long_chord(self):
        """
        Test that the chord/lyric comparing works.
        """
        # GIVEN: A chord and some lyric
        chord = 'Gsus'
        lyrics = 'me'

        # WHEN: Comparing the chord and lyrics
        ret = compare_chord_lyric(chord, lyrics)

        # THEN: The returned value should 4 because the chord is longer than the lyric
        assert 4 == ret, 'The returned value should 4 because the chord is longer than the lyric'

    def test_find_formatting_tags(self):
        """
        Test that find_formatting_tags works as expected
        """
        # GIVEN: Lyrics with formatting tags and a empty list of formatting tags
        lyrics = '{st}Amazing {r}grace{/r} how sweet the sound'
        tags = []
        FormattingTags.load_tags()

        # WHEN: Detecting active formatting tags
        active_tags = find_formatting_tags(lyrics, tags)

        # THEN: The list of active tags should contain only 'st'
        assert ['st'] == active_tags, 'The list of active tags should contain only "st"'

    def test_expand_chords_for_printing(self):
        """
        Test that the expanding of chords for printing works as expected.
        """
        # GIVEN: A lyrics-line with chords
        text_with_chords = '{st}[D]Amazing {r}gr[D7]ace{/r}  how [G]sweet the [D]sound  [F]{/st}'
        FormattingTags.load_tags()

        # WHEN: Expanding the chords
        text_with_expanded_chords = expand_chords_for_printing(text_with_chords, '{br}')

        # THEN: We should get html that looks like below
        expected_html = '<table class="line" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td><table ' \
                        'class="segment" cellpadding="0" cellspacing="0" border="0" align="left"><tr class="chordrow">'\
                        '<td class="chord">&nbsp;</td><td class="chord">D</td></tr><tr><td class="lyrics">{st}{/st}' \
                        '</td><td class="lyrics">{st}Amazing&nbsp;{/st}</td></tr></table><table class="segment" ' \
                        'cellpadding="0" cellspacing="0" border="0" align="left"><tr class="chordrow">' \
                        '<td class="chord">&nbsp;</td><td class="chord">D7</td></tr><tr><td class="lyrics">{st}{r}gr' \
                        '{/r}{/st}</td><td class="lyrics">{r}{st}ace{/r}&nbsp;{/st}</td></tr></table><table ' \
                        'class="segment" cellpadding="0" cellspacing="0" border="0" align="left"><tr class="chordrow">'\
                        '<td class="chord">&nbsp;</td></tr><tr><td class="lyrics">{st}&nbsp;{/st}</td></tr></table>' \
                        '<table class="segment" cellpadding="0" cellspacing="0" border="0" align="left"><tr ' \
                        'class="chordrow"><td class="chord">&nbsp;</td></tr><tr><td class="lyrics">{st}how&nbsp;{/st}' \
                        '</td></tr></table><table class="segment" cellpadding="0" cellspacing="0" border="0" ' \
                        'align="left"><tr class="chordrow"><td class="chord">G</td></tr><tr><td class="lyrics">{st}' \
                        'sweet&nbsp;{/st}</td></tr></table><table class="segment" cellpadding="0" cellspacing="0" ' \
                        'border="0" align="left"><tr class="chordrow"><td class="chord">&nbsp;</td></tr><tr><td ' \
                        'class="lyrics">{st}the&nbsp;{/st}</td></tr></table><table class="segment" cellpadding="0" ' \
                        'cellspacing="0" border="0" align="left"><tr class="chordrow"><td class="chord">D</td></tr>' \
                        '<tr><td class="lyrics">{st}sound&nbsp;{/st}</td></tr></table><table class="segment" ' \
                        'cellpadding="0" cellspacing="0" border="0" align="left"><tr class="chordrow"><td ' \
                        'class="chord">&nbsp;</td></tr><tr><td class="lyrics">{st}&nbsp;{/st}</td></tr></table>' \
                        '<table class="segment" cellpadding="0" cellspacing="0" border="0" align="left"><tr ' \
                        'class="chordrow"><td class="chord">F</td></tr><tr><td class="lyrics">{st}{/st}&nbsp;</td>' \
                        '</tr></table></td></tr></table>'
        assert expected_html == text_with_expanded_chords, 'The expanded chords should look as expected!'
