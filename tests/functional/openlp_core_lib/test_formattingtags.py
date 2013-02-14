"""
Package to test the openlp.core.lib.formattingtags package.
"""

from unittest import TestCase

from mock import patch

from openlp.core.lib import FormattingTags

class TestFormattingTags(TestCase):

    def get_html_tags_no_user_tags_test(self):
        """
        Test the get_html_tags static method.
        """
        with patch(u'openlp.core.lib.translate') as mocked_translate, \
                patch(u'openlp.core.lib.settings') as mocked_settings, \
                patch(u'openlp.core.lib.formattingtags.cPickle') as mocked_cPickle:
            # GIVEN: Our mocked modules and functions.
            mocked_translate.side_effect = lambda module, string_to_translate: string_to_translate
            mocked_settings.value.return_value = u''
            mocked_cPickle.load.return_value = []

            # WHEN: Get the display tags.
            FormattingTags.load_tags()
            old_tags_list = FormattingTags.get_html_tags()
            FormattingTags.load_tags()
            new_tags_list = FormattingTags.get_html_tags()

            # THEN: Lists should be identically.
            assert old_tags_list == new_tags_list, u'The formatting tag lists should be identically.'

    def get_html_tags_with_user_tags_test(self):
        """
        Add a tag and check if it still exists after reloading the tags list.
        """
        # FIXME: not working yet.
        with patch(u'openlp.core.lib.translate') as mocked_translate, \
                patch(u'openlp.core.lib.settings') as mocked_settings, \
                patch(u'openlp.core.lib.formattingtags.cPickle') as mocked_cPickle:
            # GIVEN: Our mocked modules and functions.
            mocked_translate.side_effect = lambda module, string_to_translate: string_to_translate
            mocked_settings.value.return_value = u''
            mocked_cPickle.load.return_value = []
            tags = [{
                u'end tag': '{/aa}',
                u'start html': '<span>',
                u'start tag': '{aa}',
                u'protected': False,
                u'end html': '</span>',
                u'desc': 'name'}
            ]

            # WHEN: Get the display tags.
            FormattingTags.add_html_tags(tags)
            FormattingTags.load_tags()
            old_tags_list = FormattingTags.get_html_tags()
            FormattingTags.load_tags()
            new_tags_list = FormattingTags.get_html_tags()

            # THEN: Lists should be identically.
            assert old_tags_list == new_tags_list, u'The formatting tag lists with user tags should be identically.'



