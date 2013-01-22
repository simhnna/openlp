"""
    Package to test the openlp.core.lib package.
"""
import os

from unittest import TestCase
from mock import MagicMock
from openlp.core.lib import ServiceItem, Registry

VERSE = u'The Lord said to {r}Noah{/r}: \n'\
        'There\'s gonna be a {su}floody{/su}, {sb}floody{/sb}\n'\
        'The Lord said to {g}Noah{/g}:\n'\
        'There\'s gonna be a {st}floody{/st}, {it}floody{/it}\n'\
        'Get those children out of the muddy, muddy \n'\
        '{r}C{/r}{b}h{/b}{bl}i{/bl}{y}l{/y}{g}d{/g}{pk}'\
        'r{/pk}{o}e{/o}{pp}n{/pp} of the Lord\n'
FOOTER = [u'Arky Arky (Unknown)', u'Public Domain', u'CCLI 123456']

TESTPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), u'..', u'..', u'resources'))

class TestServiceItem(TestCase):

    def setUp(self):
        """
        Set up the Registry
        """
        registry = Registry.create()
        mocked_renderer =  MagicMock()
        mocked_image_manager =  MagicMock()
        mocked_renderer.format_slide.return_value = [VERSE]
        Registry().register(u'renderer', mocked_renderer)
        Registry().register(u'image_manager', mocked_image_manager)

    def serviceitem_basic_test(self):
        """
        Test the Service Item basic test
        """
        # GIVEN: A new service item

        # WHEN:A service item is created (without a plugin)
        service_item = ServiceItem(None)

        # THEN: We should get back a valid service item
        assert service_item.is_valid is True, u'The new service item should be valid'
        assert service_item.missing_frames() is True, u'There should not be any frames in the service item'

    def serviceitem_add_text_test(self):
        """
        Test the Service Item add text test
        """
        # GIVEN: A new service item
        service_item = ServiceItem(None)

        # WHEN: adding text to a service item
        service_item.add_from_text(VERSE)
        service_item.raw_footer = FOOTER

        # THEN: We should get back a valid service item
        assert service_item.is_valid is True, u'The new service item should be valid'
        assert service_item.missing_frames() is False, u'check frames loaded '

        # WHEN: Render called
        assert len(service_item._display_frames) == 0, u'A blank Service Item with no display frames'
        service_item.render(True)

        # THEN: We should have a page of output.
        assert len(service_item._display_frames) == 1, u'A valid rendered Service Item has 1 display frame'
        assert service_item.get_rendered_frame(0) == VERSE.split(u'\n')[0], u'A output has rendered correctly.'

    def serviceitem_add_image_test(self):
        """
        Test the Service Item add image test
        """
        # GIVEN: A new service item and a mocked renderer
        service_item = ServiceItem(None)
        service_item.name = u'test'

        # WHEN: adding image to a service item
        test_image = os.path.join(TESTPATH, u'church.jpg')
        service_item.add_from_image(test_image, u'Image Title')

        # THEN: We should get back a valid service item
        assert service_item.is_valid is True, u'The new service item should be valid'
        assert len(service_item._display_frames) == 0, u'The service item has no display frames'

        # THEN: We should have a page of output.
        assert len(service_item._raw_frames) == 1, u'A valid rendered Service Item has display frames'
        assert service_item.get_rendered_frame(0) == test_image

        # WHEN: adding a second image to a service item
        service_item.add_from_image(test_image, u'Image1 Title')

        # THEN: We should have an increased page of output.
        assert len(service_item._raw_frames) == 2, u'A valid rendered Service Item has display frames'
        assert service_item.get_rendered_frame(0) == test_image
        assert service_item.get_rendered_frame(0) == service_item.get_rendered_frame(1)

        # WHEN requesting a saved service item
        service = service_item.get_service_repr(True)

        # THEN: We should have two parts of the service.
        assert len(service) == 2, u'A saved service has two parts'
        assert service[u'header'][u'name']  == u'test' , u'A test plugin was returned'
        assert service[u'data'][0][u'title'] == u'Image Title' , u'The first title name matches the request'
        assert service[u'data'][0][u'path'] == test_image , u'The first image name matches'
        assert service[u'data'][0][u'title'] != service[u'data'][1][u'title'], \
            u'The individual titles should not match'
        assert service[u'data'][0][u'path'] == service[u'data'][1][u'path'], u'The file paths should match'

        # WHEN validating a service item
        service_item.validate_item([u'jpg'])

        # THEN the service item should be valid
        assert service_item.is_valid is True, u'The new service item should be valid'

        # WHEN: adding a second image to a service item
        service_item.add_from_image(u'resources/church1.jpg', u'Image1 Title')

        # WHEN validating a service item
        service_item.validate_item([u'jpg'])

        # THEN the service item should be valid
        assert service_item.is_valid is False, u'The service item is not valid due to validation changes'

    def serviceitem_add_command_test(self):
        """
        Test the Service Item add command test
        """
        # GIVEN: A new service item and a mocked renderer
        service_item = ServiceItem(None)
        service_item.name = u'test'

        # WHEN: adding image to a service item
        test_file = os.path.join(TESTPATH, u'church.jpg')
        service_item.add_from_command(TESTPATH, u'church.jpg', test_file)

        # THEN: We should get back a valid service item
        assert service_item.is_valid is True, u'The new service item should be valid'
        assert len(service_item._display_frames) == 0, u'The service item has no display frames '

        # THEN: We should have a page of output.
        assert len(service_item._raw_frames) == 1, u'A valid rendered Service Item has one raw frame'
        assert service_item.get_rendered_frame(0) == test_file, u'The image matches the input'

        # WHEN requesting a saved service item
        service = service_item.get_service_repr(True)

        # THEN: We should have two parts of the service.
        assert len(service) == 2, u'A saved service has two parts'
        assert service[u'header'][u'name']  == u'test' , u'A test plugin'
        assert service[u'data'][0][u'title'] == u'church.jpg' , u'The first title name '
        assert service[u'data'][0][u'path'] == TESTPATH , u'The first image name'
        assert service[u'data'][0][u'image'] == test_file , u'The first image name'

        # WHEN validating a service item
        service_item.validate_item([u'jpg'])

        # THEN the service item should be valid
        assert service_item.is_valid is True, u'The service item is valid'

        # WHEN validating a service item with a different suffix
        service_item.validate_item([u'png'])

        # THEN the service item should not be valid
        assert service_item.is_valid is False, u'The service item is not valid'
