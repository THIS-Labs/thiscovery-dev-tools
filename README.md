# thiscovery-dev-tools

## Purpose

Library of utilities and data used for business logic that is never run by an
AWS lambda function. For example, code and data supporting testing and
deployment of thiscovery stacks are made available in this package.

## Installation

This library should not be deployed. Instead, it should be installed using `pip`
into the env of other stacks.

Run the command:

`pip install https://github.com/THIS-Labs/thiscovery-dev-tools/archive/master.zip`

## thiscovery deploy

`setup.py` is what is run when this package is installed into each repo. It
gives access to the `thiscovery deploy`command.

This `thiscovery deploy`command is run from the `feature.yaml` scripts of each
repo during CICD.

The functionality of `thiscovery deploy` is in the main() function of
`command_line.py`.