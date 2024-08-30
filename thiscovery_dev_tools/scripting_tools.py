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
