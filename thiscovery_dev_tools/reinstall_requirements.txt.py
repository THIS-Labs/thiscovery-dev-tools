import subprocess
import sys


def uninstall(package):
    print('pip uninstall ' + package)
    subprocess.check_call([sys.executable, "-m", "pip", "uninstall" "--yes", package])


def install(package):
    print('pip install ' + package)
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


if __name__ == "__main__":

    with open('requirements.txt') as f:
        lines = f.readlines()

    for l in lines:

        if l.startswith('https://github'):
            uninstall(l.split("THIS-Institute/", 1)[1].split("/", 1)[0])

            install(l)
