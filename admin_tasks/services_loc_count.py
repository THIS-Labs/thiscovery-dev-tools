#!/usr/bin/env python3

from local.dev_config import GITHUB_FOLDER, SECRETS_NAMESPACE, ENVS, REPOS, COMMIT_TIMESTAMP
import os
import re
import subprocess
from prettytable import PrettyTable


repos_table = PrettyTable()
repos_table.field_names = [
    "Stack",
    "Lines of code",
    "Git revision",
]


class StackLocCounter:
    def __init__(self, stack_name):
        print(f"Working on {stack_name}")
        self.stack_name = stack_name
        self.git_revision = self.get_master_revision_at_timestamp()
        self.append_stack_report_to_repos_table()

    def get_master_revision_at_timestamp(self):
        def get_revision():
            return subprocess.run(
                [
                    "git",
                    "rev-list",
                    "-1",
                    "--before",
                    f"{COMMIT_TIMESTAMP}",
                ],
                capture_output=True,
                check=True,
                text=True,
            ).stdout.strip()

        try:
            rev = get_revision()
        except subprocess.CalledProcessError:
            subprocess.run(["git", "fetch"])
            rev = get_revision()
        return rev

    def count_lines_of_code_for_revision(self):
        """
        Uses the cloc command line tool (https://github.com/AlDanial/cloc)
        """
        cloc_report = subprocess.run(
            [
                "cloc",
                "--exclude-dir=vendors,public",
                "--exclude-ext=sty",
                "--git",
                self.git_revision,
            ],
            capture_output=True,
            check=True,
            text=True,
        ).stdout.strip()


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
    for r in REPOS:
        os.chdir(os.path.join(GITHUB_FOLDER, r))
        try:
            StackDeploymentStatus(stack_name=r, env_name=e)
        except subprocess.CalledProcessError:
            repos_table.add_row(
                [
                    r,
                    e,
                    "NA",
                    "NA",
                    "NA",
                ]
            )
            continue
    print("\nLines of code per GitHub repository (excluding comments and blank lines):")
    print(repos_table)


if __name__ == "__main__":
    main()
