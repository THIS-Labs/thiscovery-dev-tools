#!/usr/bin/env python3

import json
import os
import subprocess
import sys
import requests

import thiscovery_lib.utilities as utils


class AwsDeployer:
    def __init__(self, stack_name):
        self.stack_name = stack_name
        self.branch = self.get_git_branch()
        self.environment, self.stackery_credentials, self.slack_webhooks = self.get_environment_variables()

    @staticmethod
    def get_git_branch():
        branch = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True, check=True,
                                text=True).stdout.strip()
        status = subprocess.run(['git', 'status'], capture_output=True, check=True, text=True).stdout.strip()
        if ('Your branch is ahead' in status) or ('Changes not staged for commit' in status):
            while True:
                proceed = input('It looks like your local branch is out of sync with remote. Continue anyway? [y/N] (or "s" to show "git status")')
                if proceed.lower() == 's':
                    print(status)
                    print("--------------------------")
                elif proceed.lower() not in ['y', 'yes']:
                    sys.exit('Deployment aborted')
                else:
                    break
        return branch

    @staticmethod
    def get_environment_variables():
        secrets_namespace = None
        stackery_credentials = None
        slack_webhooks = None
        for env_var, env_var_name, json_format in [
            (secrets_namespace, 'SECRETS_NAMESPACE', False),
            (stackery_credentials, 'STACKERY_CREDENTIALS', True),
            (slack_webhooks, 'SLACK_DEPLOYMENT_NOTIFIER_WEBHOOKS', True)
        ]:
            try:
                env_var = os.environ[env_var_name]
            except KeyError:
                raise utils.DetailedValueError(f'Environment variable {env_var_name} not set', {})
            if json_format:
                env_var = json.loads(env_var)
        environment = utils.namespace2name(secrets_namespace)
        return environment, stackery_credentials, slack_webhooks

    def slack_message(self, message=None):
        if not message:
            message = f"Branch {self.branch} of {self.stack_name} has just been deployed to {self.environment}."
        header = {
            'Content-Type': 'application/json'
        }
        payload = {
            "text": message
        }
        requests.post(self.slack_webhooks['stackery-deployments'], data=json.dumps(payload), headers=header)
        if 'afs25' in self.environment:
            requests.post(self.slack_webhooks['Andre'], data=json.dumps(payload), headers=header)

    def stackery_deployment(self):
        profile = utils.namespace2profile(utils.name2namespace(self.environment))
        try:
            subprocess.run(['stackery', 'deploy', f'--stack-name={self.stack_name}', f'--aws-profile={profile}',
                            f'--env-name={self.environment}', f'--git-ref={self.branch}'], check=True,
                           stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as err:
            print(err.stderr.decode('utf-8').strip())
            raise err

    def stackery_login(self):
        try:
            subprocess.run(['stackery', 'login', '--email', self.stackery_credentials['email'],
                            '--password', self.stackery_credentials['password']],
                           check=True, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as err:
            print(err.stderr.decode('utf-8').strip())
            raise err

    def deployment_confirmation(self):
        proceed = input(f'About to deploy branch {self.branch} of {self.stack_name} to {self.environment}. Continue? [y/N]')
        if not proceed.lower() in ['y', 'yes']:
            sys.exit('Deployment aborted')

    def deploy(self):
        try:
            self.stackery_deployment()
        except subprocess.CalledProcessError as err:
            if err.stderr.decode('utf-8').strip() == "Error: Failed to get settings: Attempting to access Stackery " \
                                                     "before logging in. Please run `stackery login` first.":
                self.stackery_login()
                self.stackery_deployment()
            else:
                raise err

    def main(self):
        self.deployment_confirmation()
        self.deploy()
        self.slack_message()
