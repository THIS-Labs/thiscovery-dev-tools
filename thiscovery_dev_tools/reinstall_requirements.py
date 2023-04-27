"""Reinstall all packages in requirements.txt that are located on GitHub

These packages are normally updated by manually uninstalling and reinstalling
using pip.

Versioning of these packages confuses pip, so running 'pip install --upgrade'
doesn't work

Run this script by
    - installing thiscovery-dev-tools in the stack you are working on
    - Create a PyCharm run configuration pointing directly to this script
    - Working dir should be the top level dir of the stack, in order
      to find the correct requirements.txt

"""

import subprocess
import sys


def uninstall(package):
    print("pip uninstall " + package)
    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "--yes", package])


def install(package):
    print("pip install " + package)
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


if __name__ == "__main__":

    with open("requirements.txt") as f:
        lines = f.readlines()

    for l in lines:

        if l.startswith("https://github"):
            uninstall(l.split("THIS-Labs/", 1)[1].split("/", 1)[0])

            install(l)
