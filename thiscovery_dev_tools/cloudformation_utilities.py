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
import thiscovery_lib.utilities as utils

from http import HTTPStatus


class CloudFormationClient(utils.BaseClient):
    def __init__(self):
        super().__init__("cloudformation")

    def validate_template(self, **kwargs):
        response = self.client.validate_template(**kwargs)
        assert (
            response["ResponseMetadata"]["HTTPStatusCode"] == HTTPStatus.OK
        ), f"Call to CloudFormation client failed with response: {response}"
        return response
