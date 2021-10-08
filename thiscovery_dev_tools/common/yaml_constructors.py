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


# region yaml constructors for stackery tags
class GetAtt(yaml.YAMLObject):
    yaml_tag = "!GetAtt"

    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return f"{self.yaml_tag} {self.val}"

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(node.value)


class Equals(GetAtt):
    yaml_tag = "!Equals"


class If(GetAtt):
    yaml_tag = "!If"


class Join(GetAtt):
    yaml_tag = "!Join"


class Not(GetAtt):
    yaml_tag = "!Not"


class Sub(GetAtt):
    yaml_tag = "!Sub"


class Select(GetAtt):
    yaml_tag = "!Select"


class Ref(GetAtt):
    yaml_tag = "!Ref"


# endregion
