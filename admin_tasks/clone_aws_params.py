"""
Clone parameters from one AWS dev account to another.

This is needed for before any thiscovery stack is deployed to AWS.

secrets.py will need adding/updating
.aws/credentials will need details of both the source and target accounts

"""

import boto3

import secrets  # sets env variables

SOURCE = secrets.THISCOVERY_AFS25_PROFILE
SOURCE_ID = "afs25"
PARAMS_PATH = "/test-%s/" % SOURCE_ID
TARGET = secrets.THISCOVERY_SEM86_PROFILE
TARGET_ID = "sem86"


def get_client(client_type):
    session = boto3.Session(profile_name=client_type)
    return session.client("ssm", region_name="eu-west-1")


if __name__ == "__main__":

    source_client = get_client(SOURCE)
    target_client = get_client(TARGET)

    paginator = source_client.get_paginator("get_parameters_by_path")

    for page in paginator.paginate(
        Path=PARAMS_PATH, WithDecryption=True, Recursive=True
    ):
        for param in page["Parameters"]:
            param["Name"] = param["Name"].replace(SOURCE_ID, TARGET_ID)

            param.pop("Version", None)
            param.pop("LastModifiedDate", None)
            param.pop("ARN", None)

            response = target_client.put_parameter(**param)
