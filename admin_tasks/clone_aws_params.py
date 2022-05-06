"""
Clone parameters from one AWS dev account to another.

This is needed for before any thiscovery stack is deployed to AWS.

secrets.py will need adding/updating
.aws/credentials will need details of both the source and target accounts

"""
import local.secrets  # sets env variables
import local.dev_config as conf  # sets env variables


import boto3


def get_client(profile_name):
    """
    :param profile_name: A profile name in your AWS credentials file
    :return:
    """
    session = boto3.Session(profile_name=profile_name)
    return session.client("ssm", region_name="eu-west-1")


if __name__ == "__main__":

    source_client = get_client(conf.SOURCE_PROFILE)
    target_client = get_client(conf.TARGET_PROFILE)

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
                    f"Replace '{conf.SOURCE_ENV}' for 'conf.TARGET_ENV' in value of parameter {param_name}: {param_value}? (y/N)"
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
                print(param_name + " already exists, skipping")
            else:
                print(f"Parameter {param_name} successfully created")
