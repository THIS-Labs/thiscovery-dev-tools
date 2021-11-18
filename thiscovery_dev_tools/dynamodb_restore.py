#
#   Thiscovery API - THIS Institute’s citizen science platform
#   Copyright (C) 2019 THIS Institute
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   A copy of the GNU Affero General Public License is available in the
#   docs folder of this project.  It is also available www.gnu.org/licenses/
#
import os
import subprocess
import sys
import thiscovery_lib.utilities as utils
from thiscovery_lib.dynamodb_utilities import Dynamodb


class DynamodbRestore:
    def __init__(self, stack_name, table_name, restore_datetime=None):
        """
        Args:
            restore_datetime (datetime): Point in time table should be restored to (e.g. datetime(2015, 1, 1)).
                    If None, latest backup will be used.
        """
        self.stack_name = stack_name
        self.table_name = table_name
        self.restore_datetime = restore_datetime
        self.full_table_name = "-".join(
            [
                self.stack_name,
                utils.get_environment_name(),
                self.table_name,
            ]
        )
        self.aws_restored_table = "-".join(
            [
                self.full_table_name,
                os.getenv("RESTORE_NAME_POSFIX", "Restored"),
            ]
        )
        self.ddb_client = Dynamodb(stack_name=stack_name)

    def create_aws_restored_table(self, **kwargs):
        if kwargs.get("RestoreDateTime") is None:
            if self.restore_datetime is None:
                kwargs["UseLatestRestorableTime"] = True
                kwargs.pop("RestoreDateTime", None)
            else:
                kwargs["RestoreDateTime"] = self.restore_datetime

        self.ddb_client.client.restore_table_to_point_in_time(
            SourceTableName=self.full_table_name,
            TargetTableName=self.aws_restored_table,
            **kwargs,
        )

    def wait_for_aws_restored_table_ready(self):
        self.ddb_client.wait_until_table_exists(
            table_name=self.aws_restored_table, table_name_verbatim=True
        )

    def create_local_dump_of_aws_restored_table(self):
        subprocess.run(
            [
                "dynamodump",
                "-m",
                "backup",
                "-r",
                "eu-west-1",
                "-p",
                utils.namespace2profile(utils.get_aws_namespace()),
                "-s",
                self.aws_restored_table,
            ],
            check=True,
            stderr=sys.stderr,
            stdout=sys.stdout,
        )

    def update_original_table_with_restored_data(self):
        subprocess.run(
            [
                "dynamodump",
                "-m",
                "restore",
                "--dataOnly",
                "-r",
                "eu-west-1",
                "-p",
                utils.namespace2profile(utils.get_aws_namespace()),
                "-s",
                self.aws_restored_table,
                "-d",
                self.full_table_name,
            ],
            check=True,
            stderr=sys.stderr,
            stdout=sys.stdout,
        )

    def restore_deleted_or_updated_items(self, **kwargs):
        """
        This routine restores deleted or updated items in a Dynamodb table.
        New items created since the backup snapshot was saved will not be affected.
        In other words, this routine does not delete any items from Dynamodb
        """
        self.create_aws_restored_table(**kwargs)
        self.wait_for_aws_restored_table_ready()
        self.create_local_dump_of_aws_restored_table()
        self.update_original_table_with_restored_data()
