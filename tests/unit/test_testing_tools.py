import local.dev_config  # sets env variable 'TEST_ON_AWS'
import local.secrets  # sets AWS profile as env variable
import thiscovery_dev_tools.testing_tools as test_tools
import unittest
from http import HTTPStatus
from thiscovery_dev_tools.test_data.auth0_events import SUCCESSFUL_LOGIN


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
        auth0_event_data = SUCCESSFUL_LOGIN
        # source must be removed for the event to trigger the lambda function
        del auth0_event_data["source"]
        result = test_tools.test_eb_request_v2(
            local_method="Not applicable",
            aws_eb_event=auth0_event_data,
            lambda_name="PersistAuth0Event",
            stack_name="thiscovery-monitoring",
            aws_processing_delay=5,
            event_bus_name="auth0-event-bus",
        )
        self.assertEqual(HTTPStatus.OK, result["statusCode"])
