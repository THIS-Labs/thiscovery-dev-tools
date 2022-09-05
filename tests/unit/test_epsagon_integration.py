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
import cfn_flip
import os
import unittest
import thiscovery_dev_tools.epsagon_integration as ei

from pprint import pprint


TEST_DATA_FOLDER = os.path.join(
    os.path.dirname(__file__), "../../thiscovery_dev_tools/test_data"
)


class EpsagonIntTestCase(unittest.TestCase):
    def test_init_ok(self):
        with open(os.path.join(TEST_DATA_FOLDER, "raw_template_01.yaml")) as f:
            template_string = f.read()
        integration = ei.EpsagonIntegration(
            template_as_string=template_string, environment="test"
        )
        self.assertIsInstance(integration.t_dict, dict)

    def test_main_ok(self):
        with open(os.path.join(TEST_DATA_FOLDER, "raw_template_01.yaml")) as f:
            template_string = f.read()
        integration = ei.EpsagonIntegration(
            template_as_string=template_string, environment="test"
        )
        integration.main()
        pprint(integration.epsagon_yaml)
