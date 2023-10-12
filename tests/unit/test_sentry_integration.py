import json
from unittest.mock import patch, mock_open

try:
    from local import dev_config  # sets env variable 'TEST_ON_AWS'
    from local import secrets  # sets AWS profile as env variable
except ImportError:
    pass

import thiscovery_dev_tools.testing_tools as test_tools
from thiscovery_dev_tools.sentry_integration import SentryIntegration


class SentryIntegrationTestCase(test_tools.BaseTestCase):
    @patch("thiscovery_dev_tools.sentry_integration.SentryIntegration.output_template")
    @patch("thiscovery_dev_tools.sentry_integration.SentryIntegration.trace_lambdas")
    def test_main(self, mocked_trace_lambdas, mocked_output_template):
        sentry_intergration = SentryIntegration("", "")
        sentry_intergration.main()

        mocked_trace_lambdas.assert_called_once()
        mocked_output_template.assert_called_once()

    def test_output_template(self):
        template = {"Resources": {"test": {"Type": "AWS::Serverless::Function"}}}

        sentry_intergration = SentryIntegration(json.dumps(template), "")

        with patch('builtins.open', mock_open()) as m:
            sentry_intergration.output_template()
        
        handle = m()
        handle.write.assert_called_once_with(
            'Resources:\n  test:\n    Type: AWS::Serverless::Function\n'
        )

    @patch("thiscovery_dev_tools.sentry_integration.SentryIntegration.add_tracing_to_lambda")
    def test_trace_lambdas(self, mocked_add_tracing_to_lambda):
        template = {
            "Resources": {
                "test": {
                    "Type": "AWS::Serverless::Function"
                }
            }
        }

        sentry_integration = SentryIntegration(json.dumps(template), "")
        sentry_integration.trace_lambdas()

        mocked_add_tracing_to_lambda.assert_called_once()

    def test_add_tracing_to_lambda(self):
        template = {
            "Resources": {
                "test": {
                    "Type": "AWS::Serverless::Function",
                    "Properties": {
                        "Handler": "test.handler"
                    }
                }
            }
        }

        sentry_integration = SentryIntegration(json.dumps(template), "")
        result = sentry_integration.add_tracing_to_lambda(template["Resources"]["test"])

        self.assertEqual(
            result,
            {
                'Type': 'AWS::Serverless::Function',
                'Properties': {
                    'Handler': 'sentry_sdk.integrations.init_serverless_sdk.sentry_lambda_handler',
                    'Layers': ['arn:aws:lambda:eu-west-1:943013980633:layer:SentryPythonServerlessSDK:76'],
                    'Environment': {
                        'Variables': {
                            'SENTRY_INITIAL_HANDLER': 'test.handler',
                            'SENTRY_TRACES_SAMPLE_RATE': 1,
                            'SENTRY_DSN': '{{resolve:secretsmanager://sentry-connection:SecretString:dsn}}'
                        }
                    }
                }
            }
        )
