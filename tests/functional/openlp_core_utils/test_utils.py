"""
Functional tests to test the AppLocation class and related methods.
"""
from unittest import TestCase

from mock import patch

from openlp.core.utils import clean_filename, _get_frozen_path, get_locale_key, get_natural_key, split_filename


class TestUtils(TestCase):
    """
    A test suite to test out various methods around the AppLocation class.
    """

    def get_frozen_path_test(self):
        """
        Test the _get_frozen_path() function
        """
        with patch(u'openlp.core.utils.sys') as mocked_sys:
            # GIVEN: The sys module "without" a "frozen" attribute
            mocked_sys.frozen = None
            # WHEN: We call _get_frozen_path() with two parameters
            # THEN: The non-frozen parameter is returned
            assert _get_frozen_path(u'frozen', u'not frozen') == u'not frozen', u'Should return "not frozen"'
            # GIVEN: The sys module *with* a "frozen" attribute
            mocked_sys.frozen = 1
            # WHEN: We call _get_frozen_path() with two parameters
            # THEN: The frozen parameter is returned
            assert _get_frozen_path(u'frozen', u'not frozen') == u'frozen', u'Should return "frozen"'

    def split_filename_with_file_path_test(self):
        """
        Test the split_filename() function with a path to a file
        """
        # GIVEN: A path to a file.
        file_path = u'/home/user/myfile.txt'
        wanted_result = (u'/home/user', u'myfile.txt')
        with patch(u'openlp.core.utils.os.path.isfile') as mocked_is_file:
            mocked_is_file.return_value = True

            # WHEN: Split the file name.
            result = split_filename(file_path)

            # THEN: A tuple should be returned.
            assert result == wanted_result, u'A tuple with the directory and file name should have been returned.'

    def split_filename_with_dir_path_test(self):
        """
        Test the split_filename() function with a path to a directory
        """
        # GIVEN: A path to a dir.
        file_path = u'/home/user/mydir'
        wanted_result = (u'/home/user/mydir', u'')
        with patch(u'openlp.core.utils.os.path.isfile') as mocked_is_file:
            mocked_is_file.return_value = False

            # WHEN: Split the file name.
            result = split_filename(file_path)

            # THEN: A tuple should be returned.
            assert result == wanted_result, \
                u'A two-entry tuple with the directory and file name (empty) should have been returned.'

    def clean_filename_test(self):
        """
        Test the clean_filename() function
        """
        # GIVEN: A invalid file name and the valid file name.
        invalid_name = u'A_file_with_invalid_characters_[\\/:\*\?"<>\|\+\[\]%].py'
        wanted_name = u'A_file_with_invalid_characters______________________.py'

        # WHEN: Clean the name.
        result = clean_filename(invalid_name)

        # THEN: The file name should be cleaned.
        assert result == wanted_name, u'The file name should not contain any special characters.'

    def get_locale_key_test(self):
        """
        Test the get_locale_key(string) function
        """
        with patch(u'openlp.core.utils.languagemanager.LanguageManager.get_language') as mocked_get_language:
            # GIVEN: The language is German
            # 0x00C3 (A with diaresis) should be sorted as "A". 0x00DF (sharp s) should be sorted as "ss".
            mocked_get_language.return_value = u'de'
            unsorted_list = [u'Auszug', u'Aushang', u'\u00C4u\u00DFerung']
            # WHEN: We sort the list and use get_locale_key() to generate the sorting keys
            # THEN: We get a properly sorted list
            test_passes = sorted(unsorted_list, key=get_locale_key) == [u'Aushang', u'\u00C4u\u00DFerung', u'Auszug']
            assert test_passes, u'Strings should be sorted properly'

    def get_natural_key_test(self):
        """
        Test the get_natural_key(string) function
        """
        with patch(u'openlp.core.utils.languagemanager.LanguageManager.get_language') as mocked_get_language:
            # GIVEN: The language is English (a language, which sorts digits before letters)
            mocked_get_language.return_value = u'en'
            unsorted_list = [u'item 10a', u'item 3b', u'1st item']
            # WHEN: We sort the list and use get_natural_key() to generate the sorting keys
            # THEN: We get a properly sorted list
            test_passes = sorted(unsorted_list, key=get_natural_key) == [u'1st item', u'item 3b', u'item 10a']
            assert test_passes, u'Numbers should be sorted naturally'
