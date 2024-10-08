import cfn_flip
import json
import os
import subprocess
import sys
import requests
import thiscovery_lib.eb_utilities as eb_utils
import thiscovery_lib.ssm_utilities as ssm_utils
import thiscovery_lib.utilities as utils

from thiscovery_dev_tools import sentry_integration as si
from thiscovery_dev_tools.constants import SENTRY_PYTHON_LAYER, SENTRY_NODE_LAYER
from thiscovery_dev_tools.cloudformation_utilities import CloudFormationClient
from typing import Optional, Union


class AwsDeployer:
    def __init__(
        self,
        stack_name: Union[str, None],
        param_overrides: Optional[dict] = None,
        sam_template_path: str = "template.yaml",
    ):
        """
        Args:
            stack_name:
            param_overrides: extra parameters to inject at deployment time;
                    used by get_parameter_overrides method
        """
        self.stack_name = stack_name
        self.param_overrides = param_overrides
        self.branch = self.get_git_branch()
        self.revision = self.get_git_revision()
        self.environment = self.get_environment()
        self.sam_template = sam_template_path
        self.parsed_template = os.path.join(".thiscovery", "template.yaml")
        self._template_yaml = self.resolve_environment_name()
        self.logger = utils.get_logger()
        self.ssm_client = ssm_utils.SsmClient()
        self.cf_client = CloudFormationClient()
        self.thiscovery_lib_revision = None

    @staticmethod
    def get_git_revision():
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            check=True,
            text=True,
        ).stdout.strip()

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
    def get_environment():
        try:
            secrets_namespace = os.environ["SECRETS_NAMESPACE"]
        except KeyError as err:
            raise utils.DetailedValueError(
                "Environment variable not set", {"KeyError": err.__repr__()}
            )
        environment = utils.namespace2name(secrets_namespace)
        return environment

    def thiscovery_lib_master_revision(self):
        lib_ls = subprocess.run(
            [
                "git",
                "ls-remote",
                "https://github.com/THIS-Labs/thiscovery-lib",
            ],
            capture_output=True,
            check=True,
            text=True,
        ).stdout.strip()
        self.thiscovery_lib_revision = lib_ls.split()[0]
        return self.thiscovery_lib_revision

    def slack_message(self, message=None):
        env_var_name = "SLACK_DEPLOYMENT_NOTIFIER_WEBHOOKS"
        try:
            slack_webhooks = json.loads(os.environ[env_var_name])
        except KeyError as err:
            raise utils.DetailedValueError(
                f"Environment variable {env_var_name} not set",
                {"KeyError": err.__repr__()},
            )
        except json.decoder.JSONDecodeError:
            raise utils.DetailedValueError(
                f"Environment variable {env_var_name} should be the JSON representation of a dictionary "
                f'(e.g. `{{"stackery-deployments": "****", "Andre": "****"}}`',
                dict(),
            )
        if not message:
            message = f"Branch {self.branch} of {self.stack_name} has just been deployed to {self.environment}."
        header = {"Content-Type": "application/json"}
        payload = {"text": message}
        requests.post(
            slack_webhooks["stackery-deployments"],
            data=json.dumps(payload),
            headers=header,
        )

    def deployment_confirmation(self):
        proceed = input(
            f"About to deploy branch {self.branch} of {self.stack_name} to {self.environment}. Continue? [y/N]"
        )
        if not proceed.lower() in ["y", "yes"]:
            sys.exit("Deployment aborted")

    def build(
        self, build_in_container: bool, container_env_vars: Optional[dict] = None
    ):
        """
        Calls "sam build"
        (https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-build.html)
        Args:
            build_in_container: invokes sam build with the --use-container option
            container_env_vars: environment variables to pass to the build container
        """

        def run_build(build_command):
            subprocess.run(
                build_command,
                check=True,
                stderr=sys.stderr,
                stdout=sys.stdout,
            )

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
            if (
                isinstance(container_env_vars, dict)
                and ("GIT_PERSONAL_ACCESS_TOKEN" not in container_env_vars.keys())
            ) or not container_env_vars:
                self.logger.info(
                    "Attempting to pass GIT_PERSONAL_ACCESS_TOKEN to build container as "
                    "that's usually required"
                )
                try:
                    git_pat = os.environ["GIT_PERSONAL_ACCESS_TOKEN"]
                except KeyError:
                    self.logger.warning(
                        "GIT_PERSONAL_ACCESS_TOKEN not found in environment variables. Build will"
                        "fail if requirements include any private package"
                    )
                    git_pat = "Na"
                command += [
                    "--container-env-var",
                    f"GIT_PERSONAL_ACCESS_TOKEN={git_pat}",
                ]

        if container_env_vars:
            for k, v in container_env_vars.items():
                command += ["--container-env-var", f"{k}={v}"]

        try:
            run_build(command)
        except subprocess.CalledProcessError:
            if not build_in_container:
                self.logger.warning(
                    "Standard build strategy failed; attempting to build in Docker container"
                )
                self.build(build_in_container=True)
            else:
                raise
        self.logger.info("Finished building phase")

    def get_parameter_overrides(self):
        parameters = {
            "StackTagName": self.stack_name,
            "EnvironmentTagName": self.environment,
        }
        if self.param_overrides:
            parameters.update(self.param_overrides)
        param_overrides_str = str()
        for k, v in parameters.items():
            param_overrides_str += f"ParameterKey={k},ParameterValue={v} "
        return f'"{param_overrides_str.strip()}"'

    def deploy(self, confirm_cf_changeset, iam_capability_type="CAPABILITY_IAM"):
        self.logger.info("Starting deployment phase")
        deployment_method = os.environ.get("DEPLOYMENT_METHOD")
        if deployment_method == "github_actions":
            command = [
                "sam",
                "deploy",
                "--debug",
                "--region",
                "eu-west-1",
                "--template",
                os.environ["PACKAGED_TEMPLATE"],
                "--s3-bucket",
                os.environ["ARTIFACTS_BUCKET"],
                "--capabilities",
                "CAPABILITY_NAMED_IAM",
                "--no-fail-on-empty-changeset",
                "--stack-name",
                f"{self.stack_name}-{self.environment}",
                "--role-arn",
                os.environ["CLOUDFORMATION_EXECUTION_ROLE"],
                "--parameter-overrides",
                self.get_parameter_overrides(),
            ]
        else:
            aws_profile = utils.namespace2profile(
                utils.name2namespace(self.environment)
            )
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
                "--no-fail-on-empty-changeset",
                "--stack-name",
                f"{self.stack_name}-{self.environment}",
                "--parameter-overrides",
                self.get_parameter_overrides(),
            ]
        if confirm_cf_changeset:
            command.append("--confirm-changeset")
        print("command:", command)
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
        Strips ProvisionedConcurrencyConfig from template globals and resources if
        environment's provisioned-concurrency in AWS parameter store is set to zero
        (eval to False).
        """
        if not self.ssm_client.get_parameter("lambda/provisioned-concurrency"):
            template_dict = template_to_dict(self._template_yaml)
            try:
                del template_dict["Globals"]["Function"]["ProvisionedConcurrencyConfig"]
            except KeyError:
                pass
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
        sentry_integration = si.SentryIntegration(
            template_as_string=self._template_yaml, environment=self.environment
        )
        sentry_integration.main()
        self.logger.info("Ended template parsing phase")

    def validate_template(self):
        with open(self.parsed_template) as f:
            template_body = f.read()
            self.cf_client.validate_template(TemplateBody=template_body)

    def log_deployment(self):
        """
        Posts deployment event to bus. A lambda in thiscovery-devops is
        responsible for processing and saving this to Dynamodb
        """
        self.logger.info("Posting deployment event")
        self.thiscovery_lib_master_revision()
        self.sentry_python_layer_number = SENTRY_PYTHON_LAYER
        self.sentry_node_layer_number = SENTRY_NODE_LAYER
        deployment_dict = {
            "source": "aws_deployer",
            "detail-type": "deployment",
            "detail": {
                "stack": self.stack_name,
                "environment": self.environment,
                "revision": self.revision,
                "branch": self.branch,
                "sentry_python_layer_version": self.sentry_python_layer_number,
                "sentry_node_layer_version": self.sentry_node_layer_number,
                "thiscovery_lib_revision": self.thiscovery_lib_revision,
            },
        }
        deployment = eb_utils.ThiscoveryEvent(deployment_dict)
        response = deployment.put_event()
        self.logger.info("Finished posting deployment event")
        return response

    def main(self, **kwargs):
        """
        Args:
            **kwargs: confirm_cf_changeset (bool): confirm changes before deployment
                      build_in_container (bool): build in a Docker container
                      container_env_var (dict): environment variables to pass to the Docker container
                      skip_build (bool): skip building phase
                      skip_confirmation (bool): skip deployment confirmation
                      skip_slack_notification (bool): skip slack notification
        Returns:

        """
        if not kwargs.get("skip_confirmation", False):
            self.deployment_confirmation()
        if not kwargs.get("skip_build", False):
            self.parse_sam_template()
            if self.stack_name != "thiscovery-core":
                self.validate_template()
            self.build(
                kwargs.get("build_in_container", False), kwargs.get("container_env_var")
            )
        self.deploy(
            kwargs.get("confirm_cf_changes", False),
            kwargs.get("iam_capability_type", "CAPABILITY_IAM"),
        )
        self.log_deployment()
        if not kwargs.get("skip_slack_notification", False):
            self.slack_message()


def template_to_dict(template_as_string):
    return json.loads(cfn_flip.to_json(template_as_string))


def template_to_yaml(template_dict):
    return cfn_flip.to_yaml(json.dumps(template_dict))
