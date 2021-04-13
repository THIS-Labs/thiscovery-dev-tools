import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="thiscovery-dev-tools",  # Replace with your own username
    version="2021.2.1",
    author="Thiscovery team",
    author_email="support@thiscovery.org",
    description="Thiscovery development tools",
    install_requires=["thiscovery-lib", "prettytable", "pyyaml"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/THIS-Institute/thiscovery-dev-tools",
    packages=setuptools.find_packages(),
    package_data={
        "thiscovery_dev_tools": [
            os.path.join("test_data", "auth0_events.py"),
            os.path.join("test_data", "survey_personal_links.py"),
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
