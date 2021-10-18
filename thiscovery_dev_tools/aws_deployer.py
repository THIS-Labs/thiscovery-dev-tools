#!/usr/bin/env python3

import cfn_flip
import json
import os
import subprocess
import sys
import requests
import thiscovery_lib.ssm_utilities as ssm_utils
import thiscovery_lib.utilities as utils
import warnings

import thiscovery_dev_tools.epsagon_integration as ei


class AwsDeployer:
    def __init__(
        self, stack_name, param_overrides=None, sam_template_path="template.yaml"
    ):
        """
        Args:
            stack_name:
            param_overrides (dict): extra parameters to inject at deployment time;
                    used by get_parameter_overrides method
        """
        self.stack_name = stack_name
        self.param_overrides = param_overrides
        self.branch = self.get_git_branch()
        (
            self.environment,
            self.stackery_credentials,
            self.slack_webhooks,
        ) = self.get_environment_variables()
        self.sam_template = sam_template_path
        self.parsed_template = os.path.join(".thiscovery", "template.yaml")
        self._template_yaml = self.resolve_environment_name()
        self.logger = utils.get_logger()
        self.ssm_client = ssm_utils.SsmClient()

    @staticmethod
    def get_git_branch():
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            check=True,
            text=True,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status"], capture_output=True, check=True, text=True
        ).stdout.strip()
        if not utils.running_unit_tests() and (
            ("Your branch is ahead" in status)
            or ("Changes not staged for commit" in status)
        ):
            while True:
                proceed = input(
                    'It looks like your local branch is out of sync with remote. Continue anyway? [y/N] (or "s" to show "git status")'
                )
                if proceed.lower() == "s":
                    print(status)
                    print("--------------------------")
                elif proceed.lower() not in ["y", "yes"]:
                    sys.exit("Deployment aborted")
                else:
                    break
        return branch

    @staticmethod
    def get_environment_variables():
        try:
            secrets_namespace = os.environ["SECRETS_NAMESPACE"]
            stackery_credentials = os.environ["STACKERY_CREDENTIALS"]
            slack_webhooks = os.environ["SLACK_DEPLOYMENT_NOTIFIER_WEBHOOKS"]
        except KeyError as err:
            raise utils.DetailedValueError(
                "Environment variable not set", {"KeyError": err.__repr__()}
            )
        environment = utils.namespace2name(secrets_namespace)
        return environment, json.loads(stackery_credentials), json.loads(slack_webhooks)

    def slack_message(self, message=None):
        if not message:
            message = f"Branch {self.branch} of {self.stack_name} has just been deployed to {self.environment}."
        header = {"Content-Type": "application/json"}
        payload = {"text": message}
        requests.post(
            self.slack_webhooks["stackery-deployments"],
            data=json.dumps(payload),
            headers=header,
        )
        if "afs25" in self.environment:
            requests.post(
                self.slack_webhooks["Andre"], data=json.dumps(payload), headers=header
            )

    def stackery_deployment(self):
        warnings.warn(
            "This method will be deprecated on 1 Nov 2021",
            PendingDeprecationWarning,
        )
        profile = utils.namespace2profile(utils.name2namespace(self.environment))
        try:
            subprocess.run(
                [
                    "stackery",
                    "deploy",
                    f"--stack-name={self.stack_name}",
                    f"--aws-profile={profile}",
                    f"--env-name={self.environment}",
                    f"--git-ref={self.branch}",
                ],
                check=True,
                stderr=subprocess.PIPE,
            )
        except subprocess.CalledProcessError as err:
            print(err.stderr.decode("utf-8").strip())
            raise err

    def stackery_login(self):
        warnings.warn(
            "This method will be deprecated on 1 Nov 2021",
            PendingDeprecationWarning,
        )
        try:
            subprocess.run(
                [
                    "stackery",
                    "login",
                    "--email",
                    self.stackery_credentials["email"],
                    "--password",
                    self.stackery_credentials["password"],
                ],
                check=True,
                stderr=subprocess.PIPE,
            )
        except subprocess.CalledProcessError as err:
            print(err.stderr.decode("utf-8").strip())
            raise err

    def stackery_deploy(self):
        warnings.warn(
            "This method will be deprecated on 1 Nov 2021",
            PendingDeprecationWarning,
        )
        try:
            self.stackery_deployment()
        except subprocess.CalledProcessError as err:
            if (
                err.stderr.decode("utf-8").strip()
                == "Error: Failed to get settings: Attempting to access Stackery "
                "before logging in. Please run `stackery login` first."
            ):
                self.stackery_login()
                self.stackery_deployment()
            else:
                raise err

    def deployment_confirmation(self):
        proceed = input(
            f"About to deploy branch {self.branch} of {self.stack_name} to {self.environment}. Continue? [y/N]"
        )
        if not proceed.lower() in ["y", "yes"]:
            sys.exit("Deployment aborted")

    def build(self, build_in_container):
        self.logger.info("Starting building phase")
        command = [
            "sam",
            "build",
            "--debug",
            "-t",
            self.parsed_template,
            "--base-dir",
            ".",
        ]
        if build_in_container:
            command.append("--use-container")
        subprocess.run(
            command,
            check=True,
            stderr=sys.stderr,
            stdout=sys.stdout,
        )
        self.logger.info("Finished building phase")

    def get_parameter_overrides(self):
        parameters = {
            # "EpsagontokenAsString": f"/{self.environment}/epsagon-connection",
            "StackTagName": self.stack_name,
            "EnvironmentTagName": self.environment,
            # "EnvConfiglambdamemorysizeAsString": f"/{self.environment}/lambda/memory-size",
            # "EnvConfiglambdatimeoutAsString": f"/{self.environment}/lambda/timeout",
            # "EnvConfigeventbridgethiscoveryeventbusAsString": f"/{self.environment}/eventbridge/thiscovery-event-bus",
        }
        if self.param_overrides:
            parameters.update(self.param_overrides)
        param_overrides_str = str()
        for k, v in parameters.items():
            param_overrides_str += f"ParameterKey={k},ParameterValue={v} "
        return f'"{param_overrides_str.strip()}"'

    def deploy(self, confirm_cf_changeset):
        self.logger.info("Starting deployment phase")
        aws_profile = utils.namespace2profile(utils.name2namespace(self.environment))
        command = [
            "sam",
            "deploy",
            "--debug",
            "--profile",
            aws_profile,
            "--region",
            "eu-west-1",
            "--resolve-s3",
            "--capabilities",
            "CAPABILITY_NAMED_IAM",
            "--stack-name",
            f"{self.stack_name}-{self.environment}",
            "--parameter-overrides",
            self.get_parameter_overrides(),
        ]
        if confirm_cf_changeset:
            command.append("--confirm-changeset")
        subprocess.run(
            command,
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        self.logger.info("Finished deployment phase")

    def resolve_environment_name(self) -> str:
        with open(self.sam_template) as f:
            template = f.read()
            self._template_yaml = template.replace(
                "<EnvironmentName>", self.environment
            )
        return self._template_yaml

    def parse_provisioned_concurrency_setting(self):
        """
        Strips ProvisionedConcurrencyConfig from template resources if environemnt's
        provisioned-concurrency in AWS parameter store is set to zero (eval to False).
        """
        if not self.ssm_client.get_parameter("lambda/provisioned-concurrency"):
            template_dict = template_to_dict(self._template_yaml)
            for _, v in template_dict["Resources"].items():
                try:
                    del v["Properties"]["ProvisionedConcurrencyConfig"]
                except KeyError:
                    pass
            self._template_yaml = template_to_yaml(template_dict)
        return self._template_yaml

    def parse_sam_template(self):
        self.logger.info("Starting template parsing phase")
        self.parse_provisioned_concurrency_setting()
        epsagon_integration = ei.EpsagonIntegration(
            template_as_string=self._template_yaml, environment=self.environment
        )
        epsagon_integration.main()
        self.logger.info("Ended template parsing phase")

    def main(self, confirm_cf_changeset=False, build_in_container=False):
        self.deployment_confirmation()
        self.parse_sam_template()
        self.build(build_in_container)
        self.deploy(confirm_cf_changeset)
        self.slack_message()


def template_to_dict(template_as_string):
    return json.loads(cfn_flip.to_json(template_as_string))


def template_to_yaml(template_dict):
    return cfn_flip.to_yaml(json.dumps(template_dict))
