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
import thiscovery_dev_tools.aws_deployer as ad
import thiscovery_dev_tools.testing_tools as test_tools
import thiscovery_lib.utilities as utils
from http import HTTPStatus
from pprint import pprint


TEST_DATA_FOLDER = os.path.join(
    os.path.dirname(__file__), "../../thiscovery_dev_tools/test_data"
)


class AwsDeployerTestCase(test_tools.BaseTestCase):
    def test_resolve_environment_name_ok(self):
        aws_deployer = ad.AwsDeployer(
            stack_name="unittest",
            sam_template_path=os.path.join(TEST_DATA_FOLDER, "raw_template_01.yaml"),
        )
        self.assertIn(utils.get_environment_name(), aws_deployer._template_yaml)

    def test_parse_provisioned_concurrency_setting_ok(self):
        aws_deployer = ad.AwsDeployer(
            stack_name="unittest",
            sam_template_path=os.path.join(TEST_DATA_FOLDER, "raw_template_02.yaml"),
        )
        aws_deployer.parse_provisioned_concurrency_setting()
        self.assertNotIn("ProvisionedConcurrencyConfig", aws_deployer._template_yaml)

    def test_log_deployment_ok(self):
        aws_deployer = ad.AwsDeployer(
            stack_name="unittest",
            sam_template_path=os.path.join(TEST_DATA_FOLDER, "raw_template_02.yaml"),
        )
        response = aws_deployer.log_deployment()
        self.assertEqual(HTTPStatus.OK, response["ResponseMetadata"]["HTTPStatusCode"])
