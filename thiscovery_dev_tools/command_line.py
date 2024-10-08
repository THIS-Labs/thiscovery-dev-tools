"""
Entry points to use some of this module's capabilities from the command line
"""

import argparse
from thiscovery_dev_tools.aws_deployer import AwsDeployer


def parse_container_env_vars(env_vars_list):
    env_vars_dict = {}
    for env_var in env_vars_list:
        key, value = env_var.split("=", 1)
        env_vars_dict[key] = value
    return env_vars_dict


def aws_deployer_build(args):
    deployer = AwsDeployer(stack_name=None)  # stack_name not needed for build
    container_env_vars = (
        parse_container_env_vars(args.container_env_var)
        if args.container_env_var
        else None
    )
    deployer.parse_sam_template()
    deployer.build(build_in_container=True, container_env_vars=container_env_vars)


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
    parser_build.add_argument(
        "--container-env-var",
        action="append",
        metavar="ENV_VAR",
        help="Environment variables to pass to the container, format: KEY=VALUE. Can be used multiple times.",
    )
    parser_build.set_defaults(func=aws_deployer_build)

    # create the parser for the "deploy" command
    parser_deploy = subparsers.add_parser("deploy", help="deploys a thiscovery stack")
    parser_deploy.add_argument(
        "stack_name",
        type=str,
        metavar="stack_name",
        help="Name of stack being deployed",
    )
    parser_deploy.add_argument(
        "-o",
        "--iam_capability_type",
        help="capabilities type when running sam deploy. Use "
        "CAPABILITY_NAMED_IAM for example."
        "Defaults to CAPABILITY_IAM",
    )
    parser_deploy.set_defaults(func=aws_deployer_deploy)

    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        print("ERROR: You must use an available subcommand: build, deploy", "\n")
        parser.print_usage()
