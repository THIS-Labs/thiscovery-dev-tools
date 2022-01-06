"""
Clone parameters from one AWS dev account to another.

This is needed for before any thiscovery stack is deployed to AWS.

secrets.py will need adding/updating
.aws/credentials will need details of both the source and target accounts

"""

import boto3

import secrets  # sets env variables

SOURCE = secrets.THISCOVERY_SEM86_PROFILE
SOURCE_ID = 'sem86'
SOURCE_ENV = 'test'

TARGET = secrets.THISCOVERY_SEM86_PROFILE
TARGET_ID = 'sem86'
TARGET_ENV = 'dev'


def get_client(client_type):
    session = boto3.Session(profile_name=client_type)
    return session.client('ssm', region_name='eu-west-1')


if __name__ == "__main__":

    source_client = get_client(SOURCE)
    target_client = get_client(TARGET)

    paginator = source_client.get_paginator('get_parameters_by_path')

    for page in paginator.paginate(Path='/%s-%s/' % (SOURCE_ENV, SOURCE_ID), WithDecryption=True, Recursive=True):
        for param in page['Parameters']:
            param['Name'] = param['Name'].replace(SOURCE_ID, TARGET_ID)
            param['Name'] = param['Name'].replace(SOURCE_ENV, TARGET_ENV)
            param['Value'] = param['Value'].replace(SOURCE_ENV, TARGET_ENV)

            param.pop('Version', None)
            param.pop('LastModifiedDate', None)
            param.pop('ARN', None)

            try:
                response = target_client.put_parameter(**param)
            except target_client.exceptions.ParameterAlreadyExists:
                print(param['Name'] + ' already exists, skipping')
