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
import unittest
import uuid
import yaml
from dateutil import parser
from http import HTTPStatus

import thiscovery_lib.utilities as utils
from thiscovery_lib.dynamodb_utilities import Dynamodb


def tests_running_on_aws():
    """
    Checks if tests are calling AWS API endpoints
    """
    try:
        test_on_aws = os.environ['TEST_ON_AWS']
    except KeyError:
        raise utils.DetailedValueError('TEST_ON_AWS environment variable not defined', {})

    if test_on_aws.lower() == 'true':
        return True
    elif test_on_aws.lower() == 'false':
        return False
    else:
        raise ValueError(f'Unsupported value for environment variable TEST_ON_AWS: {test_on_aws}')


class BaseTestCase(unittest.TestCase):
    """
    Subclass of unittest.TestCase with methods frequently used in Thiscovery testing.
    """
    maxDiff = None
    secrets_client = None

    @classmethod
    def setUpClass(cls):
        utils.set_running_unit_tests(True)
        if cls.secrets_client is None:  # initialise a new secrets_client only if another class instance has not done so yet
            cls.secrets_client = utils.SecretsManager()
        cls.secrets_client.create_or_update_secret('runtime-parameters', {'running-tests': 'true'})
        cls.logger = utils.get_logger()

    @classmethod
    def tearDownClass(cls):
        if cls.secrets_client is None:
            cls.secrets_client = utils.SecretsManager()
        cls.secrets_client.create_or_update_secret('runtime-parameters', {'running-tests': 'false'})
        utils.set_running_unit_tests(False)

    def clear_user_specific_urls(self):
        self.ddb_client = Dynamodb()
        self.ddb_client.delete_all('UserSpecificUrls')

    def value_test_and_remove(self, entity_dict, attribute_name, expected_value):
        actual_value = entity_dict[attribute_name]
        del entity_dict[attribute_name]
        self.assertEqual(expected_value, actual_value)
        return actual_value

    def now_datetime_test_and_remove(self, entity_dict, datetime_attribute_name, tolerance=10):
        datetime_string = entity_dict[datetime_attribute_name]
        del entity_dict[datetime_attribute_name]
        now = utils.now_with_tz()
        datetime_value = parser.parse(datetime_string)
        difference = abs(now - datetime_value)
        self.assertLess(difference.seconds, tolerance)
        return datetime_string

    def uuid_test_and_remove(self, entity_dict, uuid_attribute_name):
        uuid_value = entity_dict[uuid_attribute_name]
        del entity_dict[uuid_attribute_name]
        self.assertTrue(uuid.UUID(uuid_value).version == 4)
        return uuid_value

    def new_uuid_test_and_remove(self, entity_dict):
        try:
            uuid_value = self.uuid_test_and_remove(entity_dict, 'id')
            return uuid_value
        except KeyError:
            self.assertTrue(False, 'id missing')

    @staticmethod
    def remove_dict_items_to_be_ignored_by_tests(entity_dict, list_of_keys):
        for key in list_of_keys:
            del entity_dict[key]


@unittest.skipIf(not tests_running_on_aws(), "Running tests using local methods and this test only makes sense if calling an AWS API endpoint")
class TestApiEndpoints(BaseTestCase):
    blank_api_key = ''
    invalid_api_key = '3c907908-44a7-490a-9661-3866b3732d22'

    def _common_assertion(self, expected_status, request_verb, aws_url, path_parameters=None, querystring_parameters=None, request_body=None):
        for key in [self.blank_api_key, self.invalid_api_key]:
            result = _test_request(
                request_method=request_verb,
                local_method=None,
                aws_url=aws_url,
                path_parameters=path_parameters,
                querystring_parameters=querystring_parameters,
                request_body=request_body,
                aws_api_key=key)
            result_status = result['statusCode']
            self.assertEqual(expected_status, result_status)

    def check_api_is_restricted(self, request_verb, aws_url, path_parameters=None, querystring_parameters=None, request_body=None):
        expected_status = HTTPStatus.FORBIDDEN
        self._common_assertion(expected_status, request_verb, aws_url, path_parameters=path_parameters,
                               querystring_parameters=querystring_parameters, request_body=request_body)

    def check_api_is_public(self, request_verb, aws_url, expected_status=HTTPStatus.OK, path_parameters=None, querystring_parameters=None, request_body=None):
        self._common_assertion(expected_status, request_verb, aws_url, path_parameters=path_parameters,
                               querystring_parameters=querystring_parameters, request_body=request_body)


# region yaml constructors for stackery tags
class GetAtt(yaml.YAMLObject):
    yaml_tag = '!GetAtt'

    def __init__(self, val):
        self.val = val

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(node.value)


class Sub(GetAtt):
    yaml_tag = '!Sub'


class Select(GetAtt):
    yaml_tag = '!Select'


class Ref(GetAtt):
    yaml_tag = '!Ref'
# endregion


class TestSecurityOfEndpointsDefinedInTemplateYaml(BaseTestCase):
    public_endpoints = list()

    @classmethod
    def setUpClass(cls, template_file_path, api_resource_name='CoreAPI'):
        super().setUpClass()
        with open(template_file_path) as f:
            cls.t_dict = yaml.load(f, Loader=yaml.Loader)
        cls.api_resource_name = api_resource_name

    def check_defined_endpoints_are_secure(self):
        endpoint_counter = 0
        api_paths = self.t_dict['Resources'][self.api_resource_name]['Properties']['DefinitionBody']['paths']
        for url, value in api_paths.items():
            for verb in ['delete', 'get', 'head', 'patch', 'post', 'put']:
                endpoint_config = value.get(verb)
                if endpoint_config:
                    endpoint_counter += 1
                    self.logger.info(f'Found endpoint {verb.upper()} {url} in template.yaml. Checking if it is secure',
                                     extra={'endpoint_config': endpoint_config})
                    if (url, verb) in self.public_endpoints:
                        self.assertIsNone(endpoint_config.get('security'))
                    else:
                        self.assertEqual([{'api_key': []}], endpoint_config.get('security'))
        self.logger.info(f'The configuration of {endpoint_counter} endpoints in template.yaml is as expected')


def _aws_request(method, url, params=None, data=None, aws_api_key=None):
    return utils.aws_request(method, url, os.environ.get('AWS_TEST_API'), params=params, data=data, aws_api_key=aws_api_key)


def aws_get(url, params):
    return _aws_request(method='GET', url=url, params=params)


def aws_post(url, request_body):
    return _aws_request(method='POST', url=url, data=request_body)


def aws_patch(url, request_body):
    return _aws_request(method='PATCH', url=url, data=request_body)


def _test_request(request_method, local_method, aws_url, path_parameters=None, querystring_parameters=None, request_body=None, aws_api_key=None,
                  correlation_id=None):
    logger = utils.get_logger()

    if tests_running_on_aws():
        if path_parameters is not None:
            url = aws_url + '/' + path_parameters['id']
        else:
            url = aws_url
        logger.info(f'Url passed to _aws_request: {url}', extra={'path_parameters': path_parameters, 'querystring_parameters': querystring_parameters})
        return _aws_request(method=request_method, url=url, params=querystring_parameters, data=request_body, aws_api_key=aws_api_key)
    else:
        event = {}
        if path_parameters is not None:
            event['pathParameters'] = path_parameters
        if querystring_parameters is not None:
            event['queryStringParameters'] = querystring_parameters
        if request_body is not None:
            event['body'] = request_body
        return local_method(event, correlation_id)


def test_get(local_method, aws_url, path_parameters=None, querystring_parameters=None, aws_api_key=None, correlation_id=None):
    return _test_request('GET', local_method, aws_url, path_parameters=path_parameters,
                         querystring_parameters=querystring_parameters, aws_api_key=aws_api_key, correlation_id=correlation_id)


def test_post(local_method, aws_url, path_parameters=None, request_body=None, correlation_id=None):
    return _test_request('POST', local_method, aws_url, path_parameters=path_parameters, request_body=request_body, correlation_id=correlation_id)


def test_patch(local_method, aws_url, path_parameters=None, request_body=None, correlation_id=None):
    return _test_request('PATCH', local_method, aws_url, path_parameters=path_parameters, request_body=request_body, correlation_id=correlation_id)


def test_put(local_method, aws_url, path_parameters=None, querystring_parameters=None, request_body=None, correlation_id=None):
    return _test_request('PUT', local_method, aws_url, path_parameters=path_parameters,
                         querystring_parameters=querystring_parameters, request_body=request_body, correlation_id=correlation_id)
