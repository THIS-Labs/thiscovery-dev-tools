import thiscovery_lib.utilities as utils

import local.dev_config as conf
import local.secrets as secrets

"""
Use this script to copy ALL data from a Dynamodb table into another 
(note that the table indexes must be compatible, so this script is
particular useful when setting up a new thiscovery environment or
migrating a table to a different stack).

Example configuration in dev_config.py:

# Dynamodb data migration settings
source_env = "test-afs25"
target_env = source_env
migrations = [
    {
        "source": {
            "stack": "thiscovery-core",
            "env": source_env,
            "table": "lookups",
        },
        "target": {
            "stack": "thiscovery-crm",
            "env": target_env,
            "table": "lookups",
        },
    },
    {
        "source": {
            "stack": "thiscovery-core",
            "env": source_env,
            "table": "tokens",
        },
        "target": {
            "stack": "thiscovery-crm",
            "env": target_env,
            "table": "tokens",
        },
    },
    {
        "source": {
            "stack": "thiscovery-core",
            "env": source_env,
            "table": "HubspotEmailTemplates",
        },
        "target": {
            "stack": "thiscovery-crm",
            "env": target_env,
            "table": "HubspotEmailTemplates",
        },
    },
]
"""


def main(
    source_account_profile_name,
    target_account_profile_name,
    source_table_name,
    target_table_name=None,
):
    """
    Modified from https://stackoverflow.com/a/43612035
    """

    source_db_client = utils.BaseClient(
        service_name="dynamodb", profile_name=source_account_profile_name
    )
    target_db_client = utils.BaseClient(
        service_name="dynamodb", profile_name=target_account_profile_name
    )

    if target_table_name is None:
        target_table_name = source_table_name

    source_paginator = source_db_client.client.get_paginator("scan")
    source_response = source_paginator.paginate(
        TableName=source_table_name,
        Select="ALL_ATTRIBUTES",
        ReturnConsumedCapacity="NONE",
        ConsistentRead=True,
    )
    for page in source_response:
        for item in page["Items"]:
            target_db_client.client.put_item(TableName=target_table_name, Item=item)


def process_migration(migration: dict):
    def unpack_migration_component(component: dict):
        stack = component["stack"]
        env = component["env"]
        table = component["table"]
        full_table_name = f"{stack}-{env}-{table}"
        namespace = utils.name2namespace(env)
        profile_name = utils.namespace2profile(namespace)
        return full_table_name, profile_name

    source = migration["source"]
    target = migration["target"]
    (
        source_full_table_name,
        source_profile,
    ) = unpack_migration_component(source)
    (
        target_full_table_name,
        target_profile,
    ) = unpack_migration_component(target)

    print(
        f"Copying data from Dynamodb table {source_full_table_name} to {target_full_table_name}."
    )
    main(
        source_account_profile_name=source_profile,
        target_account_profile_name=target_profile,
        source_table_name=source_full_table_name,
        target_table_name=target_full_table_name,
    )
    print(f"Done.")


if __name__ == "__main__":
    for m in conf.migrations:
        process_migration(m)
