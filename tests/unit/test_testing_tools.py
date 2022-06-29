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


class EbRequestTestCase(test_tools.BaseTestCase):
    @unittest.skipIf(
        not test_tools.tests_running_on_aws(),
        "This test only checks that test_eb_request_v2 works when running on AWS",
    )
    def test_eb_request_v2_ok(self):
        """
        This test requires a functional deployment of thiscovery-events
        to the test environment because it relies on processing by the
        PersistEvent AWS lambda
        """
        test_event = {
            "detail-type": "test_event",
            "detail": {
                "appointment_id": 123456,
                "user_id": "f2fac677-cb2c-42a0-9fa6-494059352569",
            },
        }
        result = test_tools.test_eb_request_v2(
            local_method="Not applicable",
            aws_eb_event=test_event,
            lambda_name="PersistEvent",
            stack_name="thiscovery-events",
            aws_processing_delay=30,
        )
        self.assertEqual(HTTPStatus.OK, result["statusCode"])
