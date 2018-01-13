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

from openlp.core.common import md5_hash
from openlp.core.common.path import Path
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.lib import ItemCapabilities, ServiceItem, ServiceItemType, FormattingTags
from tests.helpers.testmixin import TestMixin
from tests.utils import assert_length, convert_file_service_item
from tests.utils.constants import RESOURCE_PATH

VERSE = 'The Lord said to {r}Noah{/r}: \n'\
        'There\'s gonna be a {su}floody{/su}, {sb}floody{/sb}\n'\
        'The Lord said to {g}Noah{/g}:\n'\
        'There\'s gonna be a {st}floody{/st}, {it}floody{/it}\n'\
        'Get those children out of the muddy, muddy \n'\
        '{r}C{/r}{b}h{/b}{bl}i{/bl}{y}l{/y}{g}d{/g}{pk}'\
        'r{/pk}{o}e{/o}{pp}n{/pp} of the Lord\n'
CLEANED_VERSE = 'The Lord said to Noah: \n'\
                'There\'s gonna be a floody, floody\n'\
                'The Lord said to Noah:\n'\
                'There\'s gonna be a floody, floody\n'\
                'Get those children out of the muddy, muddy \n'\
                'Children of the Lord\n'
RENDERED_VERSE = 'The Lord said to <span style="-webkit-text-fill-color:red">Noah</span>: \n'\
                 'There&#x27;s gonna be a <sup>floody</sup>, <sub>floody</sub>\n'\
                 'The Lord said to <span style="-webkit-text-fill-color:green">Noah</span>:\n'\
                 'There&#x27;s gonna be a <strong>floody</strong>, <em>floody</em>\n'\
                 'Get those children out of the muddy, muddy \n'\
                 '<span style="-webkit-text-fill-color:red">C</span><span style="-webkit-text-fill-color:black">h' \
                 '</span><span style="-webkit-text-fill-color:blue">i</span>'\
                 '<span style="-webkit-text-fill-color:yellow">l</span><span style="-webkit-text-fill-color:green">d'\
                 '</span><span style="-webkit-text-fill-color:#FFC0CB">r</span>'\
                 '<span style="-webkit-text-fill-color:#FFA500">e</span><span style="-webkit-text-fill-color:#800080">'\
                 'n</span> of the Lord\n'
FOOTER = ['Arky Arky (Unknown)', 'Public Domain', 'CCLI 123456']
TEST_PATH = str(RESOURCE_PATH / 'service')

__default_settings__ = {
    'songs/enable chords': True,
}


class TestServiceItem(TestCase, TestMixin):

    def setUp(self):
        """
        Set up the Registry
        """
        self.build_settings()
        Settings().extend_default_settings(__default_settings__)
        Registry.create()
        mocked_renderer = MagicMock()
        mocked_renderer.format_slide.return_value = [VERSE]
        Registry().register('renderer', mocked_renderer)
        Registry().register('image_manager', MagicMock())

    def tearDown(self):
        """
        Clean up
        """
        self.destroy_settings()

    def test_service_item_basic(self):
        """
        Test the Service Item - basic test
        """
        # GIVEN: A new service item

        # WHEN: A service item is created (without a plugin)
        service_item = ServiceItem(None)

        # THEN: We should get back a valid service item
        assert service_item.is_valid is True, 'The new service item should be valid'
        assert service_item.missing_frames() is True, 'There should not be any frames in the service item'

    def test_service_item_load_custom_from_service(self):
        """
        Test the Service Item - adding a custom slide from a saved service
        """
        # GIVEN: A new service item and a mocked add icon function
        service_item = ServiceItem(None)
        service_item.add_icon = MagicMock()
        FormattingTags.load_tags()

        # WHEN: We add a custom from a saved service
        line = convert_file_service_item(TEST_PATH, 'serviceitem_custom_1.osj')
        service_item.set_from_service(line)

        # THEN: We should get back a valid service item
        assert service_item.is_valid is True, 'The new service item should be valid'
        assert_length(0, service_item._display_frames, 'The service item should have no display frames')
        assert_length(5, service_item.capabilities, 'There should be 5 default custom item capabilities')

        # WHEN: We render the frames of the service item
        service_item.render(True)

        # THEN: The frames should also be valid
        assert 'Test Custom' == service_item.get_display_title(), 'The title should be "Test Custom"'
        assert CLEANED_VERSE[:-1] == service_item.get_frames()[0]['text'], \
            'The returned text matches the input, except the last line feed'
        assert RENDERED_VERSE.split('\n', 1)[0] == service_item.get_rendered_frame(1), \
            'The first line has been returned'
        assert 'Slide 1' == service_item.get_frame_title(0), '"Slide 1" has been returned as the title'
        assert 'Slide 2' == service_item.get_frame_title(1), '"Slide 2" has been returned as the title'
        assert '' == service_item.get_frame_title(2), 'Blank has been returned as the title of slide 3'

    def test_service_item_load_image_from_service(self):
        """
        Test the Service Item - adding an image from a saved service
        """
        # GIVEN: A new service item and a mocked add icon function
        image_name = 'image_1.jpg'
        test_file = os.path.join(TEST_PATH, image_name)
        frame_array = {'path': test_file, 'title': image_name}

        service_item = ServiceItem(None)
        service_item.add_icon = MagicMock()

        # WHEN: adding an image from a saved Service and mocked exists
        line = convert_file_service_item(TEST_PATH, 'serviceitem_image_1.osj')
        with patch('openlp.core.ui.servicemanager.os.path.exists') as mocked_exists,\
                patch('openlp.core.lib.serviceitem.AppLocation.get_section_data_path') as \
                mocked_get_section_data_path:
            mocked_exists.return_value = True
            mocked_get_section_data_path.return_value = os.path.normpath('/path/')
            service_item.set_from_service(line, TEST_PATH)

        # THEN: We should get back a valid service item
        assert service_item.is_valid is True, 'The new service item should be valid'
        assert os.path.normpath(test_file) == os.path.normpath(service_item.get_rendered_frame(0)), \
            'The first frame should match the path to the image'
        assert frame_array == service_item.get_frames()[0], 'The return should match frame array1'
        assert test_file == service_item.get_frame_path(0), 'The frame path should match the full path to the image'
        assert image_name == service_item.get_frame_title(0), 'The frame title should match the image name'
        assert image_name == service_item.get_display_title(), 'The display title should match the first image name'
        assert service_item.is_image() is True, 'This service item should be of an "image" type'
        assert service_item.is_capable(ItemCapabilities.CanMaintain) is True, \
            'This service item should be able to be Maintained'
        assert service_item.is_capable(ItemCapabilities.CanPreview) is True, \
            'This service item should be able to be be Previewed'
        assert service_item.is_capable(ItemCapabilities.CanLoop) is True, \
            'This service item should be able to be run in a can be made to Loop'
        assert service_item.is_capable(ItemCapabilities.CanAppend) is True, \
            'This service item should be able to have new items added to it'

    def test_service_item_load_image_from_local_service(self):
        """
        Test the Service Item - adding an image from a saved local service
        """
        # GIVEN: A new service item and a mocked add icon function
        image_name1 = 'image_1.jpg'
        image_name2 = 'image_2.jpg'
        test_file1 = os.path.normpath(os.path.join('/home/openlp', image_name1))
        test_file2 = os.path.normpath(os.path.join('/home/openlp', image_name2))
        frame_array1 = {'path': test_file1, 'title': image_name1}
        frame_array2 = {'path': test_file2, 'title': image_name2}

        service_item = ServiceItem(None)
        service_item.add_icon = MagicMock()

        service_item2 = ServiceItem(None)
        service_item2.add_icon = MagicMock()

        # WHEN: adding an image from a saved Service and mocked exists
        line = convert_file_service_item(TEST_PATH, 'serviceitem_image_2.osj')
        line2 = convert_file_service_item(TEST_PATH, 'serviceitem_image_2.osj', 1)

        with patch('openlp.core.ui.servicemanager.os.path.exists') as mocked_exists, \
                patch('openlp.core.lib.serviceitem.AppLocation.get_section_data_path') as \
                mocked_get_section_data_path:
            mocked_exists.return_value = True
            mocked_get_section_data_path.return_value = os.path.normpath('/path/')
            service_item2.set_from_service(line2)
            service_item.set_from_service(line)

        # THEN: We should get back a valid service item

        # This test is copied from service_item.py, but is changed since to conform to
        # new layout of service item. The layout use in serviceitem_image_2.osd is actually invalid now.
        assert service_item.is_valid is True, 'The first service item should be valid'
        assert service_item2.is_valid is True, 'The second service item should be valid'
        # These test will fail on windows due to the difference in folder seperators
        if os.name != 'nt':
            assert test_file1 == service_item.get_rendered_frame(0), \
                'The first frame should match the path to the image'
            assert test_file2 == service_item2.get_rendered_frame(0), \
                'The Second frame should match the path to the image'
            assert frame_array1 == service_item.get_frames()[0], 'The return should match the frame array1'
            assert frame_array2 == service_item2.get_frames()[0], 'The return should match the frame array2'
            assert test_file1 == service_item.get_frame_path(0), \
                'The frame path should match the full path to the image'
            assert test_file2 == service_item2.get_frame_path(0), \
                'The frame path should match the full path to the image'
        assert image_name1 == service_item.get_frame_title(0), 'The 1st frame title should match the image name'
        assert image_name2 == service_item2.get_frame_title(0), 'The 2nd frame title should match the image name'
        assert service_item.name == service_item.title.lower(), \
            'The plugin name should match the display title, as there are > 1 Images'
        assert service_item.is_image() is True, 'This service item should be of an "image" type'
        assert service_item.is_capable(ItemCapabilities.CanMaintain) is True, \
            'This service item should be able to be Maintained'
        assert service_item.is_capable(ItemCapabilities.CanPreview) is True, \
            'This service item should be able to be be Previewed'
        assert service_item.is_capable(ItemCapabilities.CanLoop) is True, \
            'This service item should be able to be run in a can be made to Loop'
        assert service_item.is_capable(ItemCapabilities.CanAppend) is True, \
            'This service item should be able to have new items added to it'

    def test_add_from_command_for_a_presentation(self):
        """
        Test the Service Item - adding a presentation
        """
        # GIVEN: A service item, a mocked icon and presentation data
        service_item = ServiceItem(None)
        presentation_name = 'test.pptx'
        image = MagicMock()
        display_title = 'DisplayTitle'
        notes = 'Note1\nNote2\n'
        frame = {'title': presentation_name, 'image': image, 'path': TEST_PATH,
                 'display_title': display_title, 'notes': notes}

        # WHEN: adding presentation to service_item
        service_item.add_from_command(TEST_PATH, presentation_name, image, display_title, notes)

        # THEN: verify that it is setup as a Command and that the frame data matches
        assert service_item.service_item_type == ServiceItemType.Command, 'It should be a Command'
        assert service_item.get_frames()[0] == frame, 'Frames should match'

    def test_add_from_comamnd_without_display_title_and_notes(self):
        """
        Test the Service Item - add from command, but not presentation
        """
        # GIVEN: A new service item, a mocked icon and image data
        service_item = ServiceItem(None)
        image_name = 'test.img'
        image = MagicMock()
        frame = {'title': image_name, 'image': image, 'path': TEST_PATH,
                 'display_title': None, 'notes': None}

        # WHEN: adding image to service_item
        service_item.add_from_command(TEST_PATH, image_name, image)

        # THEN: verify that it is setup as a Command and that the frame data matches
        assert service_item.service_item_type == ServiceItemType.Command, 'It should be a Command'
        assert service_item.get_frames()[0] == frame, 'Frames should match'

    @patch(u'openlp.core.lib.serviceitem.ServiceItem.image_manager')
    @patch('openlp.core.lib.serviceitem.AppLocation.get_section_data_path')
    def test_add_from_command_for_a_presentation_thumb(self, mocked_get_section_data_path, mocked_image_manager):
        """
        Test the Service Item - adding a presentation, updating the thumb path & adding the thumb to image_manager
        """
        # GIVEN: A service item, a mocked AppLocation and presentation data
        mocked_get_section_data_path.return_value = os.path.join('mocked', 'section', 'path')
        service_item = ServiceItem(None)
        service_item.add_capability(ItemCapabilities.HasThumbnails)
        service_item.has_original_files = False
        service_item.name = 'presentations'
        presentation_name = 'test.pptx'
        thumb = os.path.join('tmp', 'test', 'thumb.png')
        display_title = 'DisplayTitle'
        notes = 'Note1\nNote2\n'
        expected_thumb_path = os.path.join('mocked', 'section', 'path', 'thumbnails',
                                           md5_hash(os.path.join(TEST_PATH, presentation_name).encode('utf-8')),
                                           'thumb.png')
        frame = {'title': presentation_name, 'image': expected_thumb_path, 'path': TEST_PATH,
                 'display_title': display_title, 'notes': notes}

        # WHEN: adding presentation to service_item
        service_item.add_from_command(TEST_PATH, presentation_name, thumb, display_title, notes)

        # THEN: verify that it is setup as a Command and that the frame data matches
        assert service_item.service_item_type == ServiceItemType.Command, 'It should be a Command'
        assert service_item.get_frames()[0] == frame, 'Frames should match'
        assert 1 == mocked_image_manager.add_image.call_count, 'image_manager should be used'

    def test_service_item_load_optical_media_from_service(self):
        """
        Test the Service Item - load an optical media item
        """
        # GIVEN: A new service item and a mocked add icon function
        service_item = ServiceItem(None)
        service_item.add_icon = MagicMock()

        # WHEN: We load a serviceitem with optical media
        line = convert_file_service_item(TEST_PATH, 'serviceitem-dvd.osj')
        with patch('openlp.core.ui.servicemanager.os.path.exists') as mocked_exists:
            mocked_exists.return_value = True
            service_item.set_from_service(line)

        # THEN: We should get back a valid service item with optical media info
        assert service_item.is_valid is True, 'The service item should be valid'
        assert service_item.is_capable(ItemCapabilities.IsOptical) is True, 'The item should be Optical'
        assert service_item.start_time == 654.375, 'Start time should be 654.375'
        assert service_item.end_time == 672.069, 'End time should be 672.069'
        assert service_item.media_length == 17.694, 'Media length should be 17.694'

    def test_service_item_load_song_and_audio_from_service(self):
        """
        Test the Service Item - adding a song slide from a saved service
        """
        # GIVEN: A new service item and a mocked add icon function
        service_item = ServiceItem(None)
        service_item.add_icon = MagicMock()
        FormattingTags.load_tags()

        # WHEN: We add a custom from a saved service
        line = convert_file_service_item(TEST_PATH, 'serviceitem-song-linked-audio.osj')
        service_item.set_from_service(line, '/test/')

        # THEN: We should get back a valid service item
        assert service_item.is_valid is True, 'The new service item should be valid'
        assert 0 == len(service_item._display_frames), 'The service item should have no display frames'
        assert 7 == len(service_item.capabilities), 'There should be 7 default custom item capabilities'

        # WHEN: We render the frames of the service item
        service_item.render(True)

        # THEN: The frames should also be valid
        assert 'Amazing Grace' == service_item.get_display_title(), 'The title should be "Amazing Grace"'
        assert CLEANED_VERSE[:-1] == service_item.get_frames()[0]['text'], \
            'The returned text matches the input, except the last line feed'
        assert RENDERED_VERSE.split('\n', 1)[0] == service_item.get_rendered_frame(1), \
            'The first line has been returned'
        assert 'Amazing Grace! how sweet the s' == service_item.get_frame_title(0), \
            '"Amazing Grace! how sweet the s" has been returned as the title'
        assert '’Twas grace that taught my hea' == service_item.get_frame_title(1), \
            '"’Twas grace that taught my hea" has been returned as the title'
        assert Path('/test/amazing_grace.mp3') == service_item.background_audio[0], \
            '"/test/amazing_grace.mp3" should be in the background_audio list'
