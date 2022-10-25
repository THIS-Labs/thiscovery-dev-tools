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

"""
Entry points to use some of this module's capabilities from the command line
"""

import argparse
from thiscovery_dev_tools.aws_deployer import AwsDeployer


def aws_deployer_build(args):
    deployer = AwsDeployer(stack_name=None)  # stack_name not needed for build
    deployer.parse_sam_template()
    if args.stack_name != "thiscovery-core":
        deployer.validate_template()
    deployer.build(build_in_container=True)


def aws_deployer_deploy(args):
    deployer = AwsDeployer(stack_name=args.stack_name)
    deployer.deploy(confirm_cf_changeset=False)
    deployer.log_deployment()


def main():
    description_text = "Thiscovery command line tool"

    # create the top-level parser
    parser = argparse.ArgumentParser(
        description=description_text,
        prog="Thiscovery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(help="sub-command help")

    # create the parser for the "build" command
    parser_build = subparsers.add_parser("build", help="builds a thiscovery stack")
    parser_build.set_defaults(func=aws_deployer_build)

    # create the parser for the "deploy" command
    parser_deploy = subparsers.add_parser("deploy", help="deploys a thiscovery stack")
    parser_deploy.add_argument(
        "stack_name",
        type=str,
        metavar="stack_name",
        help="Name of stack being deployed",
    )
    parser_deploy.set_defaults(func=aws_deployer_deploy)

    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        print("ERROR: You must use an available subcommand: build, deploy", "\n")
        parser.print_usage()
