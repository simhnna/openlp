
import os

from openlp.core.common.path import Path

OPENLP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TEST_RESOURCES_PATH = os.path.join(OPENLP_PATH, 'tests', 'resources')
RESOURCE_PATH = Path(TEST_RESOURCES_PATH)
