import local.dev_config  # sets env variable 'TEST_ON_AWS'
import local.secrets  # sets AWS profile as env variable
import datetime
import os
import time
import thiscovery_dev_tools.testing_tools as test_tools
import unittest
from thiscovery_lib.dynamodb_utilities import Dynamodb
from pprint import pprint
from thiscovery_dev_tools.dynamodb_restore import DynamodbRestore


TEST_DATA_FOLDER = os.path.join(
    os.path.dirname(__file__), "../../thiscovery_dev_tools/test_data"
)


# region testdata
# todo: this region is an exact copy of test data in thiscovery-lib test_dynamodb.py
DEFAULT_TEST_TABLE_NAME = "UnitTestData"
SORTKEY_TEST_TABLE_NAME = "UnitTestDataSortKey"
TEST_TABLE_STACK = "thiscovery-events"
TIME_TOLERANCE_SECONDS = 10

TEST_ITEM_01 = {
    "key": "test01",
    "item_type": "test data",
    "details": {"att1": "val1", "att2": "val2"},
}

TEST_ITEM_02 = {
    **TEST_ITEM_01,
    "processing_status": "new",
    "country_code": "GB",
}

TEST_ITEM_03 = {
    **TEST_ITEM_01,
    "bool_attribute": True,
}

TEST_ITEM_SORT_KEY_01 = {
    "key": "test_data_with_sort_key",
    "item_type": "test data",
    "details": {"att1": "val1", "att2": "val2"},
    "data_sort": "test_sort_01",
}

TEST_ITEM_SORT_KEY_02 = {
    **TEST_ITEM_SORT_KEY_01,
    "processing_status": "new",
    "country_code": "GB",
}
# endregion


class DdbRestoreTestCase(test_tools.BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ddb = Dynamodb(stack_name=TEST_TABLE_STACK)

    def setUp(self):
        self.ddb.delete_all(DEFAULT_TEST_TABLE_NAME)

    def put_test_items(self, integer, postfix=""):
        """
        Puts "integer" test items in DEFAULT_TEST_TABLE_NAME
        :param integer: desired number of test items
        :param postfix: string to add to end of key
        """
        for n in range(integer):
            self.ddb.put_item(
                table_name=DEFAULT_TEST_TABLE_NAME,
                key=f"test{n:03}{postfix}",
                item_type="test data",
                item_details={"att1": f"val1.{n}", "att2": f"val2.{n}"},
                item={},
                update_allowed=True,
            )

    # @unittest.skip("Takes c. 8 minutes to run. Comment this decorator out if needed.")
    def test_restore_table_ok(self):
        self.put_test_items(10, "_original_item")
        time.sleep(5)  # allow a few seconds for PITR backup to be created
        one_second_ago = datetime.datetime.utcnow() - datetime.timedelta(seconds=1)

        # delete a few items; these should be restored
        self.ddb.delete_item(
            table_name=DEFAULT_TEST_TABLE_NAME, key="test000_original_item"
        )
        self.ddb.delete_item(
            table_name=DEFAULT_TEST_TABLE_NAME, key="test001_original_item"
        )
        self.ddb.delete_item(
            table_name=DEFAULT_TEST_TABLE_NAME, key="test002_original_item"
        )

        # update a few items; these should be restored
        self.ddb.update_item(
            table_name=DEFAULT_TEST_TABLE_NAME,
            key="test003_original_item",
            name_value_pairs={"details": "updated details"},
        )
        self.ddb.update_item(
            table_name=DEFAULT_TEST_TABLE_NAME,
            key="test004_original_item",
            name_value_pairs={"details": "updated details"},
        )
        self.ddb.update_item(
            table_name=DEFAULT_TEST_TABLE_NAME,
            key="test005_original_item",
            name_value_pairs={"details": "updated details"},
        )

        # add a few new items; these should NOT be deleted
        self.put_test_items(3, "_new_items")

        ddb_restore = DynamodbRestore(
            stack_name=TEST_TABLE_STACK,
            table_name=DEFAULT_TEST_TABLE_NAME,
            restore_datetime=one_second_ago,
        )

        ddb_restore.restore_deleted_or_updated_items()
        items = self.ddb.scan(DEFAULT_TEST_TABLE_NAME)
        self.assertEqual(13, len(items))
        items.sort(key=lambda x: x["created"])
        expected_items = [
            {
                "created": "2021-11-18 19:12:54.988223+00:00",
                "details": {"att1": "val1.0", "att2": "val2.0"},
                "id": "test000_original_item",
                "modified": "2021-11-18 19:12:54.988223+00:00",
                "type": "test data",
            },
            {
                "created": "2021-11-18 19:12:55.025588+00:00",
                "details": {"att1": "val1.1", "att2": "val2.1"},
                "id": "test001_original_item",
                "modified": "2021-11-18 19:12:55.025588+00:00",
                "type": "test data",
            },
            {
                "created": "2021-11-18 19:12:55.057248+00:00",
                "details": {"att1": "val1.2", "att2": "val2.2"},
                "id": "test002_original_item",
                "modified": "2021-11-18 19:12:55.057248+00:00",
                "type": "test data",
            },
            {
                "created": "2021-11-18 19:12:55.088962+00:00",
                "details": {"att1": "val1.3", "att2": "val2.3"},
                "id": "test003_original_item",
                "modified": "2021-11-18 19:12:55.088962+00:00",
                "type": "test data",
            },
            {
                "created": "2021-11-18 19:12:55.119771+00:00",
                "details": {"att1": "val1.4", "att2": "val2.4"},
                "id": "test004_original_item",
                "modified": "2021-11-18 19:12:55.119771+00:00",
                "type": "test data",
            },
            {
                "created": "2021-11-18 19:12:55.151315+00:00",
                "details": {"att1": "val1.5", "att2": "val2.5"},
                "id": "test005_original_item",
                "modified": "2021-11-18 19:12:55.151315+00:00",
                "type": "test data",
            },
            {
                "created": "2021-11-18 19:12:55.182221+00:00",
                "details": {"att1": "val1.6", "att2": "val2.6"},
                "id": "test006_original_item",
                "modified": "2021-11-18 19:12:55.182221+00:00",
                "type": "test data",
            },
            {
                "created": "2021-11-18 19:12:55.211970+00:00",
                "details": {"att1": "val1.7", "att2": "val2.7"},
                "id": "test007_original_item",
                "modified": "2021-11-18 19:12:55.211970+00:00",
                "type": "test data",
            },
            {
                "created": "2021-11-18 19:12:55.242213+00:00",
                "details": {"att1": "val1.8", "att2": "val2.8"},
                "id": "test008_original_item",
                "modified": "2021-11-18 19:12:55.242213+00:00",
                "type": "test data",
            },
            {
                "created": "2021-11-18 19:12:55.273272+00:00",
                "details": {"att1": "val1.9", "att2": "val2.9"},
                "id": "test009_original_item",
                "modified": "2021-11-18 19:12:55.273272+00:00",
                "type": "test data",
            },
            {
                "created": "2021-11-18 19:13:00.495930+00:00",
                "details": {"att1": "val1.0", "att2": "val2.0"},
                "id": "test000_new_items",
                "modified": "2021-11-18 19:13:00.495930+00:00",
                "type": "test data",
            },
            {
                "created": "2021-11-18 19:13:00.525523+00:00",
                "details": {"att1": "val1.1", "att2": "val2.1"},
                "id": "test001_new_items",
                "modified": "2021-11-18 19:13:00.525523+00:00",
                "type": "test data",
            },
            {
                "created": "2021-11-18 19:13:00.556285+00:00",
                "details": {"att1": "val1.2", "att2": "val2.2"},
                "id": "test002_new_items",
                "modified": "2021-11-18 19:13:00.556285+00:00",
                "type": "test data",
            },
        ]
        for expected, actual in zip(expected_items, items):
            for att in ["created", "modified"]:
                self.assertIn(att, actual.keys())
                del expected[att]
                del actual[att]
            self.assertDictEqual(expected, actual)
