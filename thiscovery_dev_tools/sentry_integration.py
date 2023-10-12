import copy
from http import HTTPStatus
import json
import os

import cfn_flip

from thiscovery_dev_tools.constants import SENTRY_LAYER_ARN, SENTRY_LAYER

class SentryIntegration:
    def __init__(self, template_as_string, environment):
        self.t_dict = json.loads(cfn_flip.to_json(template_as_string))

        self.sentry_layer_version_number = SENTRY_LAYER
        self.sentry_layer = SENTRY_LAYER_ARN
        self.environment = environment

    def add_tracing_to_lambda(self, lambda_definition: dict) -> dict:
        prop = lambda_definition["Properties"]
        prop["Layers"] = [self.sentry_layer]

        try:
            env = prop["Environment"]
        except KeyError:
            prop["Environment"] = dict()
            env = prop["Environment"]

        try:
            env_variables = env["Variables"]
        except KeyError:
            env["Variables"] = dict()
            env_variables = env["Variables"]

        handler = prop["Handler"]
        actual_handler = copy.copy(handler)
        prop["Handler"] = "sentry_sdk.integrations.init_serverless_sdk.sentry_lambda_handler"
        env_variables["SENTRY_INITIAL_HANDLER"] = actual_handler
        env_variables["SENTRY_TRACES_SAMPLE_RATE"] = 1
        env_variables[
            "SENTRY_DSN"
        ] = f"{{{{resolve:secretsmanager:/{self.environment}/sentry-connection:SecretString:dsn}}}}"
        return lambda_definition

    def trace_lambdas(self):
        resources = self.t_dict["Resources"]
        for k, v in resources.items():
            if v.get("Type") == "AWS::Serverless::Function":
                resources[k] = self.add_tracing_to_lambda(v)

    def output_template(self):
        self.sentry_yaml = cfn_flip.to_yaml(json.dumps(self.t_dict))
        os.makedirs(".thiscovery", exist_ok=True)
        with open(os.path.join(".thiscovery", "template.yaml"), "w") as f:
            f.write(self.sentry_yaml)

    def main(self):
        self.trace_lambdas()
        self.output_template()
