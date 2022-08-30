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
from datetime import datetime
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
        "id": "test",
        "detail-type": "test_event",
        "detail": {
            "data": {"date": str(datetime.now()), "type": "test"},
            "appointment_id": 123456,
            "user_id": "f2fac677-cb2c-42a0-9fa6-494059352569",
        },
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
            aws_eb_event=self.test_event,
            lambda_name="PersistAuth0Event",
            stack_name="thiscovery-monitoring",
            aws_processing_delay=5,
            event_bus_name="auth0-event-bus",
        )
        self.assertEqual(HTTPStatus.OK, result["statusCode"])
