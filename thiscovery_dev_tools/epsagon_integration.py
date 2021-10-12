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
from __future__ import annotations
import cfn_flip
import copy
import json
import requests

from http import HTTPStatus


class EpsagonIntegration:
    epsagon_token_parameter_name = "EpsagontokenAsString"

    def __init__(self, template_file_path="template.yaml"):
        with open(template_file_path) as f:
            template = f.read()
        self.t_dict = json.loads(cfn_flip.to_json(template))
        self.epsagon_layer = self.get_latest_epsagon_layer()
        self.epsagon_yaml = None  # edited by output_template

    @staticmethod
    def get_latest_epsagon_layer() -> str:
        region = "eu-west-1"
        r = requests.get(
            f"https://layers.epsagon.com/production?region={region}&name=epsagon-python-layer&max_items=1"
        ).json()
        assert (
            r["ResponseMetadata"]["HTTPStatusCode"] == HTTPStatus.OK
        ), f"Error fetching Epsagon layer: {r.text}"
        return r["LayerVersions"][0]["LayerVersionArn"]

    def add_epsagon_token_parameter(self):
        parameters = self.t_dict["Parameters"]
        parameters[self.epsagon_token_parameter_name] = {
            "Type": "String",
            "Description": "Epsagon token (GitHub secret injected by deployment script)",
        }

    def add_tracing_to_lambda(self, lambda_definition: dict) -> dict:
        prop = lambda_definition["Properties"]
        prop["Layers"] = [self.epsagon_layer]

        env_variables = prop["Environment"]["Variables"]

        handler = prop["Handler"]
        actual_handler = copy.copy(handler)
        prop["Handler"] = "epsagon.wrapper"
        env_variables["EPSAGON_HANDLER"] = actual_handler
        env_variables["EPSAGON_APP_NAME"] = "!Ref ${AWS::StackName}"
        env_variables["EPSAGON_TOKEN"] = f"!Ref {self.epsagon_token_parameter_name}"
        return lambda_definition

    def trace_lambdas(self):
        resources = self.t_dict["Resources"]
        for k, v in resources.items():
            if v.get("Type") == "AWS::Serverless::Function":
                resources[k] = self.add_tracing_to_lambda(v)

    def output_template(self):
        self.epsagon_yaml = cfn_flip.to_yaml(json.dumps(self.t_dict))
        with open("processed_template.yaml", "w") as f:
            f.write(self.epsagon_yaml)

    def main(self):
        self.add_epsagon_token_parameter()
        self.trace_lambdas()
        self.output_template()
