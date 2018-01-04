# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2018 OpenLP Developers                                   #
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
Functional tests to test the AppLocation class and related methods.
"""
import os
import tempfile
from unittest import TestCase
from unittest.mock import MagicMock, patch

from openlp.core.common.httputils import get_user_agent, get_web_page, get_url_file_size, download_file
from openlp.core.common.path import Path
from tests.helpers.testmixin import TestMixin


class TestHttpUtils(TestCase, TestMixin):

    """
    A test suite to test out various http helper functions.
    """
    def setUp(self):
        self.tempfile = os.path.join(tempfile.gettempdir(), 'testfile')

    def tearDown(self):
        if os.path.isfile(self.tempfile):
            os.remove(self.tempfile)

    def test_get_user_agent_linux(self):
        """
        Test that getting a user agent on Linux returns a user agent suitable for Linux
        """
        with patch('openlp.core.common.httputils.sys') as mocked_sys:

            # GIVEN: The system is Linux
            mocked_sys.platform = 'linux2'

            # WHEN: We call get_user_agent()
            user_agent = get_user_agent()

            # THEN: The user agent is a Linux (or ChromeOS) user agent
            result = 'Linux' in user_agent or 'CrOS' in user_agent
            assert result is True, 'The user agent should be a valid Linux user agent'

    def test_get_user_agent_windows(self):
        """
        Test that getting a user agent on Windows returns a user agent suitable for Windows
        """
        with patch('openlp.core.common.httputils.sys') as mocked_sys:

            # GIVEN: The system is Windows
            mocked_sys.platform = 'win32'

            # WHEN: We call get_user_agent()
            user_agent = get_user_agent()

            # THEN: The user agent is a Linux (or ChromeOS) user agent
            assert 'Windows' in user_agent, 'The user agent should be a valid Windows user agent'

    def test_get_user_agent_macos(self):
        """
        Test that getting a user agent on OS X returns a user agent suitable for OS X
        """
        with patch('openlp.core.common.httputils.sys') as mocked_sys:

            # GIVEN: The system is macOS
            mocked_sys.platform = 'darwin'

            # WHEN: We call get_user_agent()
            user_agent = get_user_agent()

            # THEN: The user agent is a Linux (or ChromeOS) user agent
            assert 'Mac OS X' in user_agent, 'The user agent should be a valid OS X user agent'

    def test_get_user_agent_default(self):
        """
        Test that getting a user agent on a non-Linux/Windows/OS X platform returns the default user agent
        """
        with patch('openlp.core.common.httputils.sys') as mocked_sys:

            # GIVEN: The system is something else
            mocked_sys.platform = 'freebsd'

            # WHEN: We call get_user_agent()
            user_agent = get_user_agent()

            # THEN: The user agent is a Linux (or ChromeOS) user agent
            assert 'NetBSD'in user_agent, 'The user agent should be the default user agent'

    def test_get_web_page_no_url(self):
        """
        Test that sending a URL of None to the get_web_page method returns None
        """
        # GIVEN: A None url
        test_url = None

        # WHEN: We try to get the test URL
        result = get_web_page(test_url)

        # THEN: None should be returned
        assert result is None, 'The return value of get_web_page should be None'

    @patch('openlp.core.common.httputils.requests')
    @patch('openlp.core.common.httputils.get_user_agent')
    @patch('openlp.core.common.httputils.Registry')
    def test_get_web_page(self, MockRegistry, mocked_get_user_agent, mocked_requests):
        """
        Test that the get_web_page method works correctly
        """
        # GIVEN: Mocked out objects and a fake URL
        mocked_requests.get.return_value = MagicMock(text='text')
        mocked_get_user_agent.return_value = 'user_agent'
        fake_url = 'this://is.a.fake/url'

        # WHEN: The get_web_page() method is called
        returned_page = get_web_page(fake_url)

        # THEN: The correct methods are called with the correct arguments and a web page is returned
        mocked_requests.get.assert_called_once_with(fake_url, headers={'User-Agent': 'user_agent'},
                                                    proxies=None, timeout=30.0)
        mocked_get_user_agent.assert_called_once_with()
        assert MockRegistry.call_count == 0, 'The Registry() object should have never been called'
        assert returned_page == 'text', 'The returned page should be the mock object'

    @patch('openlp.core.common.httputils.requests')
    @patch('openlp.core.common.httputils.get_user_agent')
    def test_get_web_page_with_header(self, mocked_get_user_agent, mocked_requests):
        """
        Test that adding a header to the call to get_web_page() adds the header to the request
        """
        # GIVEN: Mocked out objects, a fake URL and a fake header
        mocked_requests.get.return_value = MagicMock(text='text')
        mocked_get_user_agent.return_value = 'user_agent'
        fake_url = 'this://is.a.fake/url'
        fake_headers = {'Fake-Header': 'fake value'}

        # WHEN: The get_web_page() method is called
        returned_page = get_web_page(fake_url, headers=fake_headers)

        # THEN: The correct methods are called with the correct arguments and a web page is returned
        expected_headers = dict(fake_headers)
        expected_headers.update({'User-Agent': 'user_agent'})
        mocked_requests.get.assert_called_once_with(fake_url, headers=expected_headers,
                                                    proxies=None, timeout=30.0)
        mocked_get_user_agent.assert_called_with()
        assert returned_page == 'text', 'The returned page should be the mock object'

    @patch('openlp.core.common.httputils.requests')
    @patch('openlp.core.common.httputils.get_user_agent')
    def test_get_web_page_with_user_agent_in_headers(self, mocked_get_user_agent, mocked_requests):
        """
        Test that adding a user agent in the header when calling get_web_page() adds that user agent to the request
        """
        # GIVEN: Mocked out objects, a fake URL and a fake header
        mocked_requests.get.return_value = MagicMock(text='text')
        fake_url = 'this://is.a.fake/url'
        user_agent_headers = {'User-Agent': 'OpenLP/2.2.0'}

        # WHEN: The get_web_page() method is called
        returned_page = get_web_page(fake_url, headers=user_agent_headers)

        # THEN: The correct methods are called with the correct arguments and a web page is returned
        mocked_requests.get.assert_called_once_with(fake_url, headers=user_agent_headers,
                                                    proxies=None, timeout=30.0)
        assert mocked_get_user_agent.call_count == 0, 'get_user_agent() should not have been called'
        assert returned_page == 'text', 'The returned page should be "test"'

    @patch('openlp.core.common.httputils.requests')
    @patch('openlp.core.common.httputils.get_user_agent')
    @patch('openlp.core.common.httputils.Registry')
    def test_get_web_page_update_openlp(self, MockRegistry, mocked_get_user_agent, mocked_requests):
        """
        Test that passing "update_openlp" as true to get_web_page calls Registry().get('app').process_events()
        """
        # GIVEN: Mocked out objects, a fake URL
        mocked_requests.get.return_value = MagicMock(text='text')
        mocked_get_user_agent.return_value = 'user_agent'
        mocked_registry_object = MagicMock()
        mocked_application_object = MagicMock()
        mocked_registry_object.get.return_value = mocked_application_object
        MockRegistry.return_value = mocked_registry_object
        fake_url = 'this://is.a.fake/url'

        # WHEN: The get_web_page() method is called
        returned_page = get_web_page(fake_url, update_openlp=True)

        # THEN: The correct methods are called with the correct arguments and a web page is returned
        mocked_requests.get.assert_called_once_with(fake_url, headers={'User-Agent': 'user_agent'},
                                                    proxies=None, timeout=30.0)
        mocked_get_user_agent.assert_called_once_with()
        mocked_registry_object.get.assert_called_with('application')
        mocked_application_object.process_events.assert_called_with()
        assert returned_page == 'text', 'The returned page should be the mock object'

    @patch('openlp.core.common.httputils.requests')
    def test_get_url_file_size(self, mocked_requests):
        """
        Test that calling "get_url_file_size" works correctly
        """
        # GIVEN: Mocked out objects, a fake URL
        mocked_requests.head.return_value = MagicMock(headers={'Content-Length': 100})
        fake_url = 'this://is.a.fake/url'

        # WHEN: The get_url_file_size() method is called
        file_size = get_url_file_size(fake_url)

        # THEN: The correct methods are called with the correct arguments and a web page is returned
        mocked_requests.head.assert_called_once_with(fake_url, allow_redirects=True, timeout=30.0)
        assert file_size == 100

    @patch('openlp.core.common.httputils.requests')
    def test_socket_timeout(self, mocked_requests):
        """
        Test socket timeout gets caught
        """
        # GIVEN: Mocked urlopen to fake a network disconnect in the middle of a download
        mocked_requests.get.side_effect = OSError

        # WHEN: Attempt to retrieve a file
        download_file(MagicMock(), url='http://localhost/test', file_path=Path(self.tempfile))

        # THEN: socket.timeout should have been caught
        # NOTE: Test is if $tmpdir/tempfile is still there, then test fails since ftw deletes bad downloaded files
        assert os.path.exists(self.tempfile) is False, 'tempfile should have been deleted'
