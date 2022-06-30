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
import json
import os
import re
import time
import unittest
import uuid
import warnings
import yaml
from dateutil import parser
from http import HTTPStatus
from typing import Union

import thiscovery_lib.utilities as utils
from thiscovery_lib.cloudwatch_utilities import CloudWatchLogsClient
from thiscovery_lib.dynamodb_utilities import Dynamodb
from thiscovery_lib.eb_utilities import ThiscoveryEvent


# region yaml constructors for cloudformation tags
class CloudFormationTag(yaml.YAMLObject):
    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return f"{self.yaml_tag} {self.val}"

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(node.value)


class GetAtt(CloudFormationTag):
    yaml_tag = "!GetAtt"


class Equals(CloudFormationTag):
    yaml_tag = "!Equals"


class If(CloudFormationTag):
    yaml_tag = "!If"


class Join(CloudFormationTag):
    yaml_tag = "!Join"


class Not(CloudFormationTag):
    yaml_tag = "!Not"


class Sub(CloudFormationTag):
    yaml_tag = "!Sub"


class Select(CloudFormationTag):
    yaml_tag = "!Select"


class Ref(CloudFormationTag):
    yaml_tag = "!Ref"


# endregion


def tests_running_on_aws():
    """
    Checks if tests are calling AWS API endpoints
    """
    try:
        test_on_aws = os.environ["TEST_ON_AWS"]
    except KeyError:
        raise utils.DetailedValueError(
            "TEST_ON_AWS environment variable not defined", {}
        )

    if test_on_aws.lower() == "true":
        return True
    elif test_on_aws.lower() == "false":
        return False
    else:
        raise ValueError(
            f"Unsupported value for environment variable TEST_ON_AWS: {test_on_aws}"
        )


def tests_running_on_github_actions():
    """
    Checks if tests are running in a GitHub Actions job
    """
    return os.environ.get("DEPLOYMENT_METHOD") == "github_actions"


class BaseDdbMixin:
    @classmethod
    def get_ddb_client(cls, stack_name):
        try:
            cls.ddb_client
        except AttributeError:
            cls.ddb_client = Dynamodb(stack_name=stack_name)

    @classmethod
    def set_notifications_table(cls):
        try:
            cls.notifications_table = f"thiscovery-core-{cls.env_name}-notifications"
        except AttributeError:
            cls.env_name = utils.get_environment_name()
            cls.notifications_table = f"thiscovery-core-{cls.env_name}-notifications"

    @classmethod
    def clear_notifications_table(cls):
        cls.set_notifications_table()
        try:
            cls.ddb_client.delete_all(
                table_name=cls.notifications_table, table_name_verbatim=True
            )
        except AttributeError:
            cls.ddb_client = Dynamodb()
            cls.ddb_client.delete_all(
                table_name=cls.notifications_table, table_name_verbatim=True
            )

    @classmethod
    def scan_notifications_table(cls):
        cls.set_notifications_table()
        try:
            return cls.ddb_client.scan(
                table_name=cls.notifications_table, table_name_verbatim=True
            )
        except AttributeError:
            cls.ddb_client = Dynamodb()
            return cls.ddb_client.scan(
                table_name=cls.notifications_table, table_name_verbatim=True
            )


class BaseTestCase(unittest.TestCase):
    """
    Subclass of unittest.TestCase with methods frequently used in Thiscovery testing.
    """

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        # staging and production fail-safe exception
        if os.environ["UNIT_TEST_NAMESPACE"] in [
            "/staging/",
            "/prod/",
            "/router-prod/",
        ]:
            raise ValueError(
                "Naughty developer! You must not run tests on %s?"
                % os.environ["UNIT_TEST_NAMESPACE"]
            )

        # deprecation warnings handling (inspired by https://stackoverflow.com/a/67484991)
        allow_deprecation_list = json.loads(os.environ.get("ALLOW_DEPRECATION", "null"))
        warnings.filterwarnings("error", category=DeprecationWarning)
        if allow_deprecation_list:
            for module in allow_deprecation_list:
                warnings.filterwarnings(
                    "default", category=DeprecationWarning, module=module
                )

        utils.set_running_unit_tests(True)
        cls.logger = utils.get_logger()

    @classmethod
    def tearDownClass(cls):
        utils.set_running_unit_tests(False)

    def value_test_and_remove(self, entity_dict, attribute_name, expected_value):
        actual_value = entity_dict[attribute_name]
        del entity_dict[attribute_name]
        self.assertEqual(expected_value, actual_value)
        return actual_value

    def now_datetime_test_and_remove(
        self, entity_dict, datetime_attribute_name, tolerance=10
    ):
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
            uuid_value = self.uuid_test_and_remove(entity_dict, "id")
            return uuid_value
        except KeyError:
            self.assertTrue(False, "id missing")

    @staticmethod
    def remove_dict_items_to_be_ignored_by_tests(entity_dict, list_of_keys):
        for key in list_of_keys:
            del entity_dict[key]


@unittest.skipIf(
    not tests_running_on_aws(),
    "Running tests using local methods and this test only makes sense if calling an AWS API endpoint",
)
class TestApiEndpoints(BaseTestCase):
    blank_api_key = ""
    invalid_api_key = "3c907908-44a7-490a-9661-3866b3732d22"

    def _common_assertion(
        self,
        expected_status,
        request_verb,
        aws_url,
        path_parameters=None,
        querystring_parameters=None,
        request_body=None,
    ):
        for key in [self.blank_api_key, self.invalid_api_key]:
            result = _test_request(
                request_method=request_verb,
                local_method=None,
                aws_url=aws_url,
                path_parameters=path_parameters,
                querystring_parameters=querystring_parameters,
                request_body=request_body,
                aws_api_key=key,
            )
            result_status = result["statusCode"]
            self.assertEqual(expected_status, result_status)

    def check_api_is_restricted(
        self,
        request_verb,
        aws_url,
        path_parameters=None,
        querystring_parameters=None,
        request_body=None,
    ):
        expected_status = HTTPStatus.FORBIDDEN
        self._common_assertion(
            expected_status,
            request_verb,
            aws_url,
            path_parameters=path_parameters,
            querystring_parameters=querystring_parameters,
            request_body=request_body,
        )

    def check_api_is_public(
        self,
        request_verb,
        aws_url,
        expected_status=HTTPStatus.OK,
        path_parameters=None,
        querystring_parameters=None,
        request_body=None,
    ):
        self._common_assertion(
            expected_status,
            request_verb,
            aws_url,
            path_parameters=path_parameters,
            querystring_parameters=querystring_parameters,
            request_body=request_body,
        )


class TestSecurityOfEndpointsDefinedInTemplateYaml(BaseTestCase):
    public_endpoints = list()

    @classmethod
    def setUpClass(cls, template_file_path, api_resource_name="CoreAPI"):
        super().setUpClass()
        with open(template_file_path) as f:
            cls.t_dict = yaml.load(f, Loader=yaml.Loader)
        cls.api_resource_name = api_resource_name

    def _check_security_definitions(self, api_definition_body):
        self.assertIn("securityDefinitions", api_definition_body.keys())
        expected_security_definitions = {
            "api_key": {"in": "header", "name": "x-api-key", "type": "apiKey"}
        }
        self.assertEqual(
            expected_security_definitions, api_definition_body["securityDefinitions"]
        )

    def check_defined_endpoints_are_secure(self):
        endpoint_counter = 0
        api_definition_body = self.t_dict["Resources"][self.api_resource_name][
            "Properties"
        ]["DefinitionBody"]
        self._check_security_definitions(api_definition_body=api_definition_body)
        api_paths = api_definition_body["paths"]
        for url, value in api_paths.items():
            for verb in ["delete", "get", "head", "patch", "post", "put"]:
                endpoint_config = value.get(verb)
                if endpoint_config:
                    endpoint_counter += 1
                    self.logger.info(
                        f"Found endpoint {verb.upper()} {url} in template.yaml. Checking if it is secure",
                        extra={"endpoint_config": endpoint_config},
                    )
                    if (url, verb) in self.public_endpoints:
                        self.assertIsNone(endpoint_config.get("security"))
                    else:
                        self.assertEqual(
                            [{"api_key": []}], endpoint_config.get("security")
                        )
        self.logger.info(
            f"The configuration of {endpoint_counter} endpoints in template.yaml is as expected"
        )


def _aws_request(method, url, params=None, data=None, aws_api_key=None):
    return utils.aws_request(
        method,
        url,
        os.environ.get("AWS_TEST_API"),
        params=params,
        data=data,
        aws_api_key=aws_api_key,
    )


def aws_get(url, params):
    return _aws_request(method="GET", url=url, params=params)


def aws_post(url, request_body):
    return _aws_request(method="POST", url=url, data=request_body)


def aws_patch(url, request_body):
    return _aws_request(method="PATCH", url=url, data=request_body)


def test_eb_request(local_method, aws_eb_event, aws_processing_delay=0):
    warnings.warn(
        "This method will be deprecated soon; use test_eb_request_v2 instead",
        PendingDeprecationWarning,
    )
    if tests_running_on_aws():
        te = ThiscoveryEvent(event=aws_eb_event)
        result = te.put_event()
        time.sleep(aws_processing_delay)
        return result
    else:
        return local_method(aws_eb_event, dict())


def test_eb_request_v2(
    local_method,
    aws_eb_event: dict,
    lambda_name: str,
    stack_name: str,
    aws_processing_delay: int = 0,
    **kwargs,
):
    """
    Test processes triggered via EventBridge

    Args:
        local_method: function to be called when testing locally
        aws_eb_event: event to be posted to event bus when testing on AWS
        lambda_name: resource name of AWS lambda that will be processing event
        stack_name: name of stack lambda_name belongs to
        aws_processing_delay: time in seconds to wait before fetching logs
        kwargs:
            force_query (bool): if True, fallback of querying logs using CloudWatch Log Insights
                will be used even if quicker method of finding target message in latest log stream
                is successful. This option is intended for use only in unittests, so that the
                fallback option can be tested.

    Returns:
        Return value of local_method or AWS Lambda, which are the same because
        local_method is always an AWS Lambda handler
    """
    if tests_running_on_aws():
        test_run_id = str(utils.new_correlation_id())
        aws_eb_event["detail"]["debug_test_run_id"] = test_run_id
        te = ThiscoveryEvent(event=aws_eb_event)
        earliest_log_time = int(utils.utc_now_timestamp() * 1000)  # milliseconds
        result = te.put_event()
        assert (
            result["ResponseMetadata"]["HTTPStatusCode"] == HTTPStatus.OK
        ), "Failed to post event to event bus"
        time.sleep(aws_processing_delay)
        logs_client = CloudWatchLogsClient()
        query_list = [test_run_id, utils.FUNCTION_RESULT_STR]
        log_message = logs_client.find_in_log_message(
            log_group_name=lambda_name,
            query_string=query_list,
            stack_name=stack_name,
            earliest_log=earliest_log_time,
        )
        log_message_re = re.compile("\{.+", re.DOTALL)
        try:
            m = log_message_re.search(log_message)
            if kwargs.get("force_query"):
                raise TypeError
        except TypeError:
            # try querying just in case log_message we are looking for is in an older log stream
            query_attempts = 0
            logger = utils.get_logger()
            logger.debug(
                f"Log message matching '{utils.FUNCTION_RESULT_STR}' and test_run_id {test_run_id} not "
                f"found in latest stream of log_group_name {lambda_name}. Attempting "
                f"CloudWatch Log Insights querying. Please note that this is a slow process "
                f"(your machine is probably NOT hanging)"
            )
            time.sleep(60)  # no point attempting a query before a minute has elapsed
            while query_attempts < 12:
                results = logs_client.query_one_log_group(
                    log_group_name=lambda_name,
                    query_string=query_list,
                    stack_name=stack_name,
                    start_time=earliest_log_time,
                )
                if results:
                    break
                query_attempts += 1
                time.sleep(10)
            try:
                log_message = results[0][1]["value"]
            except IndexError:
                raise utils.ObjectDoesNotExistError(
                    f"Log message matching '{utils.FUNCTION_RESULT_STR}' and test_run_id {test_run_id} not "
                    f"found in log_group_name {lambda_name}",
                    details=dict(),
                )
            else:
                m = log_message_re.search(log_message)
        log_dict = json.loads(m.group())
        return log_dict["result"]
    else:
        return local_method(aws_eb_event, dict())


def _test_request(
    request_method,
    local_method,
    aws_url,
    path_parameters=None,
    querystring_parameters=None,
    request_body=None,
    aws_api_key=None,
    correlation_id=None,
):
    logger = utils.get_logger()

    if tests_running_on_aws():
        if path_parameters is not None:
            url = aws_url + "/" + path_parameters["id"]
        else:
            url = aws_url
        logger.info(
            f"Url passed to _aws_request: {url}",
            extra={
                "path_parameters": path_parameters,
                "querystring_parameters": querystring_parameters,
            },
        )
        return _aws_request(
            method=request_method,
            url=url,
            params=querystring_parameters,
            data=request_body,
            aws_api_key=aws_api_key,
        )
    else:
        event = {}
        if path_parameters is not None:
            event["pathParameters"] = path_parameters
        if querystring_parameters is not None:
            event["queryStringParameters"] = querystring_parameters
        if request_body is not None:
            event["body"] = request_body
        return local_method(event, correlation_id)


def test_get(
    local_method,
    aws_url,
    path_parameters=None,
    querystring_parameters=None,
    request_body=None,
    aws_api_key=None,
    correlation_id=None,
):
    return _test_request(
        request_method="GET",
        local_method=local_method,
        aws_url=aws_url,
        path_parameters=path_parameters,
        querystring_parameters=querystring_parameters,
        request_body=request_body,
        aws_api_key=aws_api_key,
        correlation_id=correlation_id,
    )


def test_post(
    local_method, aws_url, path_parameters=None, request_body=None, correlation_id=None
):
    return _test_request(
        "POST",
        local_method,
        aws_url,
        path_parameters=path_parameters,
        request_body=request_body,
        correlation_id=correlation_id,
    )


def test_patch(
    local_method, aws_url, path_parameters=None, request_body=None, correlation_id=None
):
    return _test_request(
        "PATCH",
        local_method,
        aws_url,
        path_parameters=path_parameters,
        request_body=request_body,
        correlation_id=correlation_id,
    )


def test_put(
    local_method,
    aws_url,
    path_parameters=None,
    querystring_parameters=None,
    request_body=None,
    correlation_id=None,
):
    return _test_request(
        "PUT",
        local_method,
        aws_url,
        path_parameters=path_parameters,
        querystring_parameters=querystring_parameters,
        request_body=request_body,
        correlation_id=correlation_id,
    )
