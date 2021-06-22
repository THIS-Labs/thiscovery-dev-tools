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
from __future__ import annotations

import csv
import os
import random
import string
import thiscovery_lib.utilities as utils
from tkinter import Tk
from tkinter.filedialog import askopenfilename


class CsvImporter:
    def __init__(self, csvfile_path=None):
        self.logger = utils.get_logger()
        self.input_filename = csvfile_path
        if csvfile_path is None:
            root = Tk()
            root.withdraw()  # we don't want a full GUI, so keep the root window from appearing
            root.update()
            self.input_filename = askopenfilename(
                initialdir=os.path.expanduser("~"),
                title="Please select input file",
                filetypes=(("csv files", "*.csv"), ("all files", "*.*")),
            )
            root.update()
            root.destroy()


# region qualtrics test data
def generate_qualtrics_random_response_id(n: int) -> list[str]:
    characters = string.digits + string.ascii_letters
    response_ids = list()
    for _ in range(n):
        response_ids.append(
            "R_" + "".join(random.choice(characters) for i in range(15))
        )
    return response_ids


def generate_random_longitude(n: int) -> list[float]:
    return [random.uniform(-180, 180) for _ in range(n)]


def generate_random_latitude(n: int) -> list[float]:
    return [random.uniform(-90, 90) for _ in range(n)]


# endregion
