"""
Clone parameters from one AWS dev account to another.

Skips any parameters that already exist. Note that the script will attempt to
    reformat any params and values before it copies, but may then skip if it
    already exists.

This is needed for before any thiscovery stack is deployed to AWS.

secrets.py will need adding/updating
.aws/credentials will need details of both the source and target accounts

"""

import boto3

import local.secrets  # sets env variables
import local.dev_config as conf  # sets env variables

from thiscovery_lib.utilities import namespace2profile


def get_client(profile):
    """
    :param profile: profile name, eg test-sem86
    :return:
    """

    profile_name = namespace2profile('/' + profile + '/')
    session = boto3.Session(profile_name=profile_name)
    return session.client("ssm", region_name="eu-west-1")


if __name__ == "__main__":

    source_client = get_client(conf.SOURCE_ENV)
    target_client = get_client(conf.TARGET_ENV)

    paginator = source_client.get_paginator("get_parameters_by_path")

    for page in paginator.paginate(
            Path=f"/{conf.SOURCE_ENV}/",  # SOURCE_ENV is e.g. dev-afs25, test-sem86, etc
            WithDecryption=True,
            Recursive=True,
    ):
        for param in page["Parameters"]:
            param_name = param["Name"]
            param_value = param["Value"]

            param["Name"] = param_name.replace(conf.SOURCE_ENV, conf.TARGET_ENV)
            if conf.SOURCE_ENV in param_value:
                prompt = input(
                    f"Replace '{conf.SOURCE_ENV}' for '{conf.TARGET_ENV}' in value of parameter {param_name}: {param_value}? (y/N)"
                )
                if prompt.lower() == "y":
                    param["Value"] = param_value.replace(
                        conf.SOURCE_ENV, conf.TARGET_ENV
                    )

            for attribute in ["Version", "LastModifiedDate", "ARN"]:
                del param[attribute]

            try:
                response = target_client.put_parameter(**param)
            except target_client.exceptions.ParameterAlreadyExists:
                print(param["Name"] + " already exists, skipping")
            else:
                print(f"Parameter {param['Name']} successfully created")
