#!/usr/bin/env python3

from local.dev_config import GITHUB_FOLDER, SECRETS_NAMESPACE
import os
import re
import subprocess
from prettytable import PrettyTable

ENVS = [
    'test-afs25',
    # 'staging',
    'prod',
]

REPOS = [
    's3-to-sdhs',
    'thiscovery-core',
    'thiscovery-emails',
    'thiscovery-events',
    'thiscovery-interviews',
    'thiscovery-monitoring',
    'thiscovery-surveys',
]


repos_table = PrettyTable()
repos_table.field_names = ['Stack', 'Environment', 'Commits behind', 'Commits ahead', 'Deployed revision']


class StackDeploymentStatus:

    def __init__(self, stack_name, env_name=None):
        print(f'Working on {stack_name} {env_name}')
        self.stack_name = stack_name
        self.env_name = env_name
        if env_name is None:
            self.env_name = SECRETS_NAMESPACE[1:-1]

        self.deployment_history = self.get_deployment_history()
        self.deployed_revision = self.get_deployed_revision_from_history()
        self.deployed_revision_behind, self.deployed_revision_ahead = self.get_commit_delta_to_master()
        self.append_stack_report_to_repos_table()

    def get_deployment_history(self):
        return subprocess.run(
            ['stackery', 'history', f'--stack-name={self.stack_name}', f'--env-name={self.env_name}'],
            capture_output=True,
            check=True,
            text=True
        ).stdout.strip()

    def get_deployed_revision_from_history(self):
        revision_re = re.compile('[a-z0-9]{40}')
        revisions = revision_re.findall(self.deployment_history)
        return revisions[0]

    def get_commit_delta_to_master(self):
        def get_delta():
            return subprocess.run(
                ['git', 'rev-list', '--left-right', '--count', f'origin/master...{self.deployed_revision}'],
                capture_output=True,
                check=True,
                text=True
            ).stdout.strip()
        try:
            delta = get_delta()
        except subprocess.CalledProcessError:
            subprocess.run(['git', 'fetch'])
            delta = get_delta()
        behind, ahead = delta.split('\t')
        return behind, ahead

    def append_stack_report_to_repos_table(self):
        repos_table.add_row(
            [
                self.stack_name,
                self.env_name,
                self.deployed_revision_behind,
                self.deployed_revision_ahead,
                self.deployed_revision,
            ]
        )


def main():
    for e in ENVS:
        for r in REPOS:
            os.chdir(os.path.join(GITHUB_FOLDER, r))
            try:
                StackDeploymentStatus(stack_name=r, env_name=e)
            except subprocess.CalledProcessError:
                repos_table.add_row(
                    [
                        r,
                        e,
                        'NA',
                        'NA',
                        'NA',
                    ]
                )
                continue
    print('\nStack deployment status compared to origin/master:')
    print(repos_table)


if __name__ == '__main__':
    main()
