import cfn_flip
import copy
import json
import os
from thiscovery_dev_tools.constants import (
    SENTRY_PYTHON_LAYER_ARN,
    SENTRY_NODE_LAYER_ARN,
)
from typing import Any, Dict


class SentryIntegration:
    def __init__(self, template_as_string, environment):
        self.t_dict = json.loads(cfn_flip.to_json(template_as_string))
        self.sentry_node_layer = SENTRY_NODE_LAYER_ARN
        self.sentry_python_layer = SENTRY_PYTHON_LAYER_ARN
        self.environment = environment

    def add_tracing_to_lambda(
        self, lambda_definition: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add Sentry layer and Sentry environment variables to lambda
        definition

        Args:
            lambda_definition: SAM lambda definition in dict format
                (converted from yaml using cfn_flip)

        Returns: modified lambda_definition with Sentry layer and variables
            appended
        """
        prop = lambda_definition["Properties"]

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

        if "python" in prop.get("Runtime", ""):
            # python runtimes require you to add the python sentry SDK layer,
            # and swap the handler for the function to the sentry handler,
            # storing the initial handler as an environment variable. See here:
            # https://docs.sentry.io/platforms/python/integrations/aws-lambda/manual-layer/
            prop["Layers"] = prop.get("Layers", list()) + [self.sentry_python_layer]
            handler = prop["Handler"]
            actual_handler = copy.copy(handler)
            prop[
                "Handler"
            ] = "sentry_sdk.integrations.init_serverless_sdk.sentry_lambda_handler"
            env_variables["SENTRY_INITIAL_HANDLER"] = actual_handler
        elif "node" in prop.get("Runtime", ""):
            # Unlike python runtimes, Node runtimes simply require adding the
            # node sentry SDK layer. See here:
            # https://docs.sentry.io/platforms/node/guides/aws-lambda/layer/
            prop["Layers"] = prop.get("Layers", list()) + [self.sentry_node_layer]
        env_variables["SENTRY_TRACES_SAMPLE_RATE"] = 1
        env_variables[
            "SENTRY_DSN"
        ] = f"{{{{resolve:secretsmanager:/{self.environment}/sentry-connection:SecretString:dsn}}}}"
        return lambda_definition

    def trace_lambdas(self) -> None:
        """
        Iterates through every resource definition in SAM template,
        calling self.add_tracing_to_lambda for each lambda function
        definition found.
        """
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
