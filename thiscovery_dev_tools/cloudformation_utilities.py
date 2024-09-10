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
