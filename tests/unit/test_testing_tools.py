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
import local.dev_config  # sets env variable 'TEST_ON_AWS'
import local.secrets  # sets AWS profile as env variable
import thiscovery_dev_tools.testing_tools as test_tools
import unittest
from http import HTTPStatus


@unittest.skipIf(
    not test_tools.tests_running_on_aws(),
    "Tests in this class check that test_eb_request_v2 works when running on AWS",
)
class EbRequestTestCase(test_tools.BaseTestCase):
    """
    Tests in this class require a functional deployment of thiscovery-events
    to the test environment because they rely on processing by the
    PersistEvent AWS lambda
    """

    test_event = {
        "detail-type": "test_event",
        "detail": {
            "appointment_id": 123456,
            "user_id": "f2fac677-cb2c-42a0-9fa6-494059352569",
        },
    }

    test_auth_0_event = {
        "version": "0",
        "id": "028650c9-1b93-421c-d1a0-e2153adfb645",
        "detail-type": "Auth0 log",
        "source": "Auth 0",
        "account": "266657513168",
        "time": "2022-09-01T10:25:54Z",
        "region": "eu-west-1",
        "resources": [],
        "detail": {
            "data": {
                "date": "2021-01-16T12:12:30.147Z",
                "log_id": "80020210116121232560015923748216455316604749397232713763",
                "user_name": "altha@email.co.uk",
                "ip": "3a02:c7d:bb78:ad10:343c:4c88:60cb:be04",
                "strategy_type": "database",
                "type": "s",
                "client_id": "WflrpooXWyDv3vzf6LxIzYBd6fafewjw",
                "hostname": "thiscovery.eu.auth0.com",
                "connection_id": "con_C85rtu1sSH9UFXmR",
                "user_id": "auth0|6012d7eccvf1c41076d8ed3d",
                "connection": "Username-Password-Authentication",
                "details": {
                    "session_id": "dt1G5nlxkGV10uJx4sKKBH7hwEVbaHAx",
                    "initiatedAt": 1610799117840,
                    "completedAt": 1610799150146,
                    "stats": {"loginsCount": 1},
                    "prompts": [
                        {
                            "initiatedAt": 1610799149624,
                            "completedAt": 1610799149961,
                            "connection_id": "con_C85rtu1sSH9UFXmR",
                            "stats": {"loginsCount": 1},
                            "identity": "6012d7eccvf1c41076d8ed3d",
                            "name": "lock-password-authenticate",
                            "connection": "Username-Password-Authentication",
                            "strategy": "auth0",
                            "session_user": "7102e82d05c97d006e666478",
                            "elapsedTime": 337,
                        },
                        {
                            "initiatedAt": 1610799117842,
                            "completedAt": 1610799149964,
                            "timers": {"rules": 153},
                            "user_id": "auth0|6012d7eccvf1c41076d8ed3d",
                            "user_name": "altha@email.co.uk",
                            "name": "login",
                            "flow": "login",
                            "elapsedTime": 32122,
                        },
                    ],
                    "elapsedTime": 32306,
                },
                "strategy": "auth0",
                "client_name": "Thiscovery",
                "user_agent": "Mozilla/5.0 (Linux; Android 10; SM-A908B Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36 EdgW/1.0",
            },
            "log_id": "80020210116121232560015923748216455316604749397232713763",
        },
        "correlation_id": "33fe1766-2c4c-4139-94f3-f9144cfe7be2",
    }

    def test_eb_request_v2_ok(self):
        result = test_tools.test_eb_request_v2(
            local_method="Not applicable",
            aws_eb_event=self.test_event,
            lambda_name="PersistEvent",
            stack_name="thiscovery-events",
            aws_processing_delay=5,
        )
        self.assertEqual(HTTPStatus.OK, result["statusCode"])

    def test_eb_request_v2_query_fallback_ok(self):
        """
        This test takes a long time to complete.
        """
        result = test_tools.test_eb_request_v2(
            local_method="Not applicable",
            aws_eb_event=self.test_event,
            lambda_name="PersistEvent",
            stack_name="thiscovery-events",
            aws_processing_delay=5,
            force_query=True,
        )
        self.assertEqual(HTTPStatus.OK, result["statusCode"])

    def test_eb_request_v2_event_bus_name(self):
        result = test_tools.test_eb_request_v2(
            local_method="Not applicable",
            aws_eb_event=self.test_auth_0_event,
            lambda_name="PersistAuth0Event",
            stack_name="thiscovery-monitoring",
            aws_processing_delay=5,
            event_bus_name="auth0-event-bus",
        )
        self.assertEqual(HTTPStatus.OK, result["statusCode"])
