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
import yaml


# region yaml constructors for cloudformation tags
class CloudFormationTag(yaml.YAMLObject):
    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return f"{self.yaml_tag} {self.val}"

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(node.value)


class GetAtt(CloudFormationTag):
    yaml_tag = "!GetAtt"


class Equals(CloudFormationTag):
    yaml_tag = "!Equals"


class If(CloudFormationTag):
    yaml_tag = "!If"


class Join(CloudFormationTag):
    yaml_tag = "!Join"


class Not(CloudFormationTag):
    yaml_tag = "!Not"


class Sub(CloudFormationTag):
    yaml_tag = "!Sub"


class Select(CloudFormationTag):
    yaml_tag = "!Select"


class Ref(CloudFormationTag):
    yaml_tag = "!Ref"


# endregion
