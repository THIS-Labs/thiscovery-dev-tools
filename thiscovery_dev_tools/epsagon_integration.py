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
import copy
import os
import time
import unittest
import uuid
import yaml
from dateutil import parser
from http import HTTPStatus

import thiscovery_lib.utilities as utils
from thiscovery_lib.dynamodb_utilities import Dynamodb
from thiscovery_lib.eb_utilities import ThiscoveryEvent
import thiscovery_dev_tools.common.yaml_constructors as yc


class EpsagonIntegration:
    epsagon_token_parameter_name = "EpsagontokenAsString"

    def __init__(self, template_file_path="raw_template.yaml"):
        with open(template_file_path) as f:
            self.t_dict = yaml.load(f, Loader=yaml.Loader)
        self.epsagon_layer = self.get_latest_epsagon_layer()

    def get_latest_epsagon_layer(self) -> str:
        pass

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

        env_variables["EPSAGON_APP_NAME"] = yc.Ref("${AWS::StackName}")
        env_variables["EPSAGON_TOKEN"] = yc.Ref(self.epsagon_token_parameter_name)

    def trace_lambdas(self):
        resources = self.t_dict["Resources"]
        for k, v in resources.items():
            if v.get("Type") == "AWS::Serverless::Function":
                resources[k] = self.add_tracing_to_lambda(v)

    def output_template(self):
        with open("template.yaml") as f:
            f.write(yaml.dump(self.t_dict, Dumper=yaml.Dumper))

    def main(self):
        self.add_epsagon_token_parameter()
        self.trace_lambdas()
        self.output_template()
