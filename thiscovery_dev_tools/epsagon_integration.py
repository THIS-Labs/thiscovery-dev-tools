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
import os
import requests

from http import HTTPStatus


class EpsagonIntegration:
    def __init__(self, template_as_string, environment):
        self.t_dict = json.loads(cfn_flip.to_json(template_as_string))
        (
            self.epsagon_layer,
            self.epsagon_layer_version_number,
        ) = self.get_latest_epsagon_layer()
        self.epsagon_yaml = None  # edited by output_template
        self.environment = environment

    @staticmethod
    def get_latest_epsagon_layer() -> tuple:
        region = "eu-west-1"
        r = requests.get(
            f"https://layers.epsagon.com/production?region={region}&name=epsagon-python-layer&max_items=1"
        )
        assert (
            r.status_code == HTTPStatus.OK
        ), f"Error fetching Epsagon layer: {r.status_code} - {r.reason}"
        r_dict = r.json()
        latest_version = r_dict["LayerVersions"][0]
        return latest_version["LayerVersionArn"], latest_version["Version"]

    def add_tracing_to_lambda(self, lambda_definition: dict) -> dict:
        prop = lambda_definition["Properties"]
        prop["Layers"] = [self.epsagon_layer]

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
        prop["Handler"] = "epsagon.wrapper"
        env_variables["EPSAGON_HANDLER"] = actual_handler
        env_variables["EPSAGON_APP_NAME"] = {"Fn::Sub": "${AWS::StackName}"}
        env_variables[
            "EPSAGON_TOKEN"
        ] = f"{{{{resolve:secretsmanager:/{self.environment}/epsagon-connection:SecretString:token}}}}"
        return lambda_definition

    def trace_lambdas(self):
        resources = self.t_dict["Resources"]
        for k, v in resources.items():
            if v.get("Type") == "AWS::Serverless::Function":
                resources[k] = self.add_tracing_to_lambda(v)

    def output_template(self):
        self.epsagon_yaml = cfn_flip.to_yaml(json.dumps(self.t_dict))
        os.makedirs(".thiscovery", exist_ok=True)
        with open(os.path.join(".thiscovery", "template.yaml"), "w") as f:
            f.write(self.epsagon_yaml)

    def main(self):
        self.trace_lambdas()
        self.output_template()
