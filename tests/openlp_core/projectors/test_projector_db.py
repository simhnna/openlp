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
Package to test the openlp.core.projectors.db module.
record functions.

PREREQUISITE: add_record() and get_all() functions validated.
"""
import os
import shutil
from tempfile import mkdtemp
from unittest import TestCase
from unittest.mock import MagicMock, patch

from openlp.core.common.registry import Registry
from openlp.core.lib.db import upgrade_db
from openlp.core.projectors import upgrade
from openlp.core.projectors.constants import PJLINK_PORT
from openlp.core.projectors.db import Manufacturer, Model, Projector, ProjectorDB, ProjectorSource, Source
from openlp.core.ui.mainwindow import MainWindow
from tests.helpers.testmixin import TestMixin
from tests.resources.projector.data import TEST_DB_PJLINK1, TEST_DB, TEST1_DATA, TEST2_DATA, TEST3_DATA
from tests.utils.constants import TEST_RESOURCES_PATH


def compare_data(one, two):
    """
    Verify two Projector() instances contain the same data
    """
    return one is not None and \
        two is not None and \
        one.ip == two.ip and \
        one.port == two.port and \
        one.name == two.name and \
        one.location == two.location and \
        one.notes == two.notes and \
        one.sw_version == two.sw_version and \
        one.serial_no == two.serial_no and \
        one.model_filter == two.model_filter and \
        one.model_lamp == two.model_lamp


def compare_source(one, two):
    """
    Verify two ProjectorSource instances contain the same data
    """
    return one is not None and \
        two is not None and \
        one.projector_id == two.projector_id and \
        one.code == two.code and \
        one.text == two.text


def add_records(projector_db, test):
    """
    Add record if not in database
    """
    record_list = projector_db.get_projector_all()
    if len(record_list) < 1:
        added = False
        for record in test:
            added = projector_db.add_projector(record) or added
        return added

    for new_record in test:
        added = None
        for record in record_list:
            if compare_data(record, new_record):
                break
            added = projector_db.add_projector(new_record)
    return added


class TestProjectorDBUpdate(TestCase):
    """
    Test case for upgrading Projector DB.
    NOTE: Separate class so I don't have to look for upgrade tests.
    """
    def setUp(self):
        """
        Setup for tests
        """
        self.tmp_folder = mkdtemp(prefix='openlp_')

    def tearDown(self):
        """
        Clean up after tests
        """
        # Ignore errors since windows can have problems with locked files
        shutil.rmtree(self.tmp_folder, ignore_errors=True)

    def test_upgrade_old_projector_db(self):
        """
        Test that we can upgrade a version 1 db to the current schema
        """
        # GIVEN: An old prjector db
        old_db = os.path.join(TEST_RESOURCES_PATH, "projector", TEST_DB_PJLINK1)
        tmp_db = os.path.join(self.tmp_folder, TEST_DB)
        shutil.copyfile(old_db, tmp_db)
        db_url = 'sqlite:///{db}'.format(db=tmp_db)

        # WHEN: upgrading the db
        updated_to_version, latest_version = upgrade_db(db_url, upgrade)

        # THEN: the song db should have been upgraded to the latest version
        assert updated_to_version == latest_version, 'The projector DB should have been upgrade to the latest version'


class TestProjectorDB(TestCase, TestMixin):
    """
    Test case for ProjectorDB
    """
    @patch('openlp.core.projectors.db.init_url')
    def setUp(self, mocked_init_url):
        """
        Set up anything necessary for all tests
        """
        # Create a test app to keep from segfaulting
        Registry.create()
        self.registry = Registry()
        self.setup_application()
        # Mock cursor busy/normal methods.
        self.app.set_busy_cursor = MagicMock()
        self.app.set_normal_cursor = MagicMock()
        self.app.args = []
        Registry().register('application', self.app)
        Registry().set_flag('no_web_server', True)
        # Mock classes and methods used by mainwindow.
        with patch('openlp.core.ui.mainwindow.SettingsForm'), \
                patch('openlp.core.ui.mainwindow.ImageManager'), \
                patch('openlp.core.ui.mainwindow.LiveController'), \
                patch('openlp.core.ui.mainwindow.PreviewController'), \
                patch('openlp.core.ui.mainwindow.OpenLPDockWidget'), \
                patch('openlp.core.ui.mainwindow.QtWidgets.QToolBox'), \
                patch('openlp.core.ui.mainwindow.QtWidgets.QMainWindow.addDockWidget'), \
                patch('openlp.core.ui.mainwindow.ServiceManager'), \
                patch('openlp.core.ui.mainwindow.ThemeManager'), \
                patch('openlp.core.ui.mainwindow.ProjectorManager'), \
                patch('openlp.core.ui.mainwindow.Renderer'), \
                patch('openlp.core.ui.mainwindow.websockets.WebSocketServer'), \
                patch('openlp.core.ui.mainwindow.server.HttpServer'):
            self.main_window = MainWindow()

        # Create a temporary database directory and database
        self.tmp_folder = mkdtemp(prefix='openlp_')
        tmpdb_url = 'sqlite:///{db}'.format(db=os.path.join(self.tmp_folder, TEST_DB))
        mocked_init_url.return_value = tmpdb_url
        self.projector = ProjectorDB()

    def tearDown(self):
        """
        Clean up

        Delete all the C++ objects at the end so that we don't have a segfault
        """
        self.projector.session.close()
        self.projector = None
        del self.main_window
        # Ignore errors since windows can have problems with locked files
        shutil.rmtree(self.tmp_folder, ignore_errors=True)

    def test_find_record_by_ip(self):
        """
        Test find record by IP
        """
        # GIVEN: Record entries in database
        add_records(self.projector, [Projector(**TEST1_DATA), Projector(**TEST2_DATA)])

        # WHEN: Search for record using IP
        record = self.projector.get_projector_by_ip(TEST2_DATA['ip'])

        # THEN: Verify proper record returned
        assert compare_data(Projector(**TEST2_DATA), record) is True, 'Record found should have been test_2 data'

    def test_find_record_by_name(self):
        """
        Test find record by name
        """
        # GIVEN: Record entries in database
        add_records(self.projector, [Projector(**TEST1_DATA), Projector(**TEST2_DATA)])

        # WHEN: Search for record using name
        record = self.projector.get_projector_by_name(TEST2_DATA['name'])

        # THEN: Verify proper record returned
        assert compare_data(Projector(**TEST2_DATA), record) is True, 'Record found should have been test_2 data'

    def test_record_delete(self):
        """
        Test record can be deleted
        """
        # GIVEN: Record in database
        add_records(self.projector, [Projector(**TEST3_DATA), ])
        record = self.projector.get_projector_by_ip(TEST3_DATA['ip'])

        # WHEN: Record deleted
        self.projector.delete_projector(record)

        # THEN: Verify record not retrievable
        found = self.projector.get_projector_by_ip(TEST3_DATA['ip'])
        assert found is None, 'test_3 record should have been deleted'

    def test_record_edit(self):
        """
        Test edited record returns the same record ID with different data
        """
        # GIVEN: Record entries in database
        add_records(self.projector, [Projector(**TEST1_DATA), Projector(**TEST2_DATA)])

        # WHEN: We retrieve a specific record
        record = self.projector.get_projector_by_ip(TEST1_DATA['ip'])
        record_id = record.id

        # WHEN: Data is changed
        record.ip = TEST3_DATA['ip']
        record.port = TEST3_DATA['port']
        record.pin = TEST3_DATA['pin']
        record.name = TEST3_DATA['name']
        record.location = TEST3_DATA['location']
        record.notes = TEST3_DATA['notes']
        record.sw_version = TEST3_DATA['sw_version']
        record.serial_no = TEST3_DATA['serial_no']
        record.model_filter = TEST3_DATA['model_filter']
        record.model_lamp = TEST3_DATA['model_lamp']
        updated = self.projector.update_projector(record)
        assert updated is True, 'Save updated record should have returned True'
        record = self.projector.get_projector_by_ip(TEST3_DATA['ip'])

        # THEN: Record ID should remain the same, but data should be changed
        assert record_id == record.id, 'Edited record should have the same ID'
        assert compare_data(Projector(**TEST3_DATA), record) is True, 'Edited record should have new data'

    def test_source_add(self):
        """
        Test source entry for projector item
        """
        # GIVEN: Record entries in database
        projector1 = Projector(**TEST1_DATA)
        self.projector.add_projector(projector1)
        item = self.projector.get_projector_by_id(projector1.id)
        item_id = item.id

        # WHEN: A source entry is saved for item
        source = ProjectorSource(projector_id=item_id, code='11', text='First RGB source')
        self.projector.add_source(source)

        # THEN: Projector should have the same source entry
        item = self.projector.get_projector_by_id(item_id)
        assert compare_source(item.source_list[0], source) is True, 'Source entry should be the same'

    def test_manufacturer_repr(self):
        """
        Test Manufacturer.__repr__() text
        """
        # GIVEN: Test object
        manufacturer = Manufacturer()

        # WHEN: Name is set
        manufacturer.name = 'OpenLP Test'

        # THEN: __repr__ should return a proper string
        assert str(manufacturer) == '<Manufacturer(name="OpenLP Test")>', \
            'Manufacturer.__repr__() should have returned a proper representation string'

    def test_model_repr(self):
        """
        Test Model.__repr__() text
        """
        # GIVEN: Test object
        model = Model()

        # WHEN: Name is set
        model.name = 'OpenLP Test'

        # THEN: __repr__ should return a proper string
        assert str(model) == '<Model(name='"OpenLP Test"')>', \
            'Model.__repr__() should have returned a proper representation string'

    def test_source_repr(self):
        """
        Test Source.__repr__() text
        """
        # GIVEN: Test object
        source = Source()

        # WHEN: Source() information is set
        source.pjlink_name = 'Test object'
        source.pjlink_code = '11'
        source.text = 'Input text'

        # THEN: __repr__ should return a proper string
        assert str(source) == '<Source(pjlink_name="Test object", pjlink_code="11", text="Input text")>', \
            'Source.__repr__() should have returned a proper representation string'

    def test_projector_repr(self):
        """
        Test Projector.__repr__() text
        """
        # GIVEN: Test object
        test_string = '< Projector(id="0", ip="127.0.0.1", port="4352", mac_adx="None", pin="None", ' \
            'name="Test One", location="Somewhere over the rainbow", notes="Not again", ' \
            'pjlink_name="TEST", pjlink_class="None", manufacturer="IN YOUR DREAMS", model="OpenLP", ' \
            'serial_no="None", other="None", sources="None", source_list="[]", model_filter="None", ' \
            'model_lamp="None", sw_version="None") >'

        projector = Projector()

        # WHEN: projector() is populated
        # NOTE: projector.[pin, other, sources, sw_version, serial_no, sw_version, model_lamp, model_filter]
        #       should all return None.
        #       projector.source_list should return an empty list
        projector.id = 0
        projector.ip = '127.0.0.1'
        projector.port = PJLINK_PORT
        projector.name = 'Test One'
        projector.location = 'Somewhere over the rainbow'
        projector.notes = 'Not again'
        projector.pjlink_name = 'TEST'
        projector.manufacturer = 'IN YOUR DREAMS'
        projector.model = 'OpenLP'

        # THEN: __repr__ should return a proper string
        assert str(projector) == test_string, 'Projector.__repr__() should have returned a proper string'

    def test_projectorsource_repr(self):
        """
        Test ProjectorSource.__repr__() text
        """
        # GIVEN: test setup
        projector1 = Projector(**TEST1_DATA)
        self.projector.add_projector(projector1)
        item = self.projector.get_projector_by_id(projector1.id)
        item_id = item.id

        # WHEN: A source entry is saved for item
        source = ProjectorSource(projector_id=item_id, code='11', text='First RGB source')
        self.projector.add_source(source)

        # THEN: __repr__ should return a proper string
        assert str(source) == '<ProjectorSource(id="1", code="11", text="First RGB source", projector_id="1")>', \
            'ProjectorSource.__repr__)_ should have returned a proper representation string'

    def test_get_projector_by_id_none(self):
        """
        Test get_projector_by_id() returns None if no db entry
        """
        # GIVEN: Test object and data
        projector = self.projector

        # WHEN: DB search for entry not saved
        results = projector.get_projector_by_id(dbid=123134556409824506)

        # THEN: Verify return was None
        assert results is None, 'Returned results should have equaled None'

    def test_get_projector_all_none(self):
        """
        Test get_projector_all() with no projectors in db
        """
        # GIVEN: Test object with no data
        projector = self.projector

        # WHEN: We retrieve the database entries
        results = projector.get_projector_all()

        # THEN: Verify results is None
        assert [] == results, 'Returned results should have returned an empty list'

    def test_get_projector_all_one(self):
        """
        Test get_projector_all() with one entry in db
        """
        # GIVEN: One entry in database
        projector = Projector(**TEST1_DATA)
        self.projector.add_projector(projector)

        # WHEN: We retrieve the database entries
        results = self.projector.get_projector_all()

        # THEN: We should have a list with one entry
        assert 1 == len(results), 'Returned results should have returned a list with one entry'
        assert (projector in results) is True, 'Result should have been equal to TEST1_DATA'

    def test_get_projector_all_many(self):
        """
        Test get_projector_all() with multiple entries in db
        """
        # GIVEN: multiple entries in database
        projector_list = []
        projector_list.append(Projector(**TEST1_DATA))
        projector_list.append(Projector(**TEST2_DATA))
        projector_list.append(Projector(**TEST3_DATA))
        for projector in projector_list:
            self.projector.add_projector(projector)

        # WHEN: We retrieve the database entries
        results = self.projector.get_projector_all()

        # THEN: We should have a list with three entries
        assert len(results) == len(projector_list), 'Returned results should have returned a list with three entries'
        for projector in results:
            assert (projector in projector_list) is True, 'Projector DB entry should have been in expected list'

    def test_get_projector_by_name_fail(self):
        """
        Test get_projector_by_name() fail
        """
        # GIVEN: Test entry in database
        self.projector.add_projector(Projector(**TEST1_DATA))

        # WHEN: We attempt to get a projector that's not in database
        results = self.projector.get_projector_by_name(name=TEST2_DATA['name'])

        # THEN: We should have None
        assert results is None, 'projector.get_projector_by_name() should have returned None'

    def test_add_projector_fail(self):
        """
        Test add_projector() fail
        """
        # GIVEN: Test entry in the database
        self.projector.add_projector(Projector(**TEST1_DATA))

        # WHEN: Attempt to add same projector entry
        results = self.projector.add_projector(Projector(**TEST1_DATA))

        # THEN: We should have failed to add new entry
        assert results is False, 'add_projector() should have failed'

    def test_update_projector_default_fail(self):
        """
        Test update_projector() with no options fails
        """
        # GIVEN: projector instance
        projector = self.projector

        # WHEN: attempt to update a projector entry with no options
        results = projector.update_projector()

        # THEN: We should have failed
        assert results is False, 'update_projector(projector=None) should have returned False'

    def test_update_projector_not_in_db_fail(self):
        """
        Test update_projector() when entry not in database
        """
        # GIVEN: Projector entry in database
        self.projector.add_projector(Projector(**TEST1_DATA))
        projector = Projector(**TEST2_DATA)

        # WHEN: Attempt to update data with a different ID
        results = self.projector.update_projector(projector)

        # THEN: Results should be False
        assert results is False, 'update_projector(projector=projector) should have returned False'

    def test_delete_projector_fail(self):
        """
        Test delete_projector(projector) fails to delete record
        """
        # GIVEN: Test entry in db
        self.projector.add_projector(Projector(**TEST1_DATA))

        # wHEN: Attempting to delete an entry not in the databae
        results = self.projector.delete_projector(Projector(**TEST2_DATA))

        # THEN: Results should be False
        assert results is False, 'delete_projector() should have returned False'
