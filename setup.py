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
    install_requires=[
        "https://github.com/THIS-Institute/thiscovery-lib/archive/refs/heads/master.zip",
        "prettytable",
        "pyyaml",
        "cfn-flip",
        "dynamodump",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/THIS-Institute/thiscovery-dev-tools",
    packages=setuptools.find_packages(),
    package_data={
        "thiscovery_dev_tools": [
            os.path.join("test_data", "auth0_events.py"),
            os.path.join("test_data", "qualtrics_responses.csv"),
            os.path.join("test_data", "survey_personal_links.py"),
            os.path.join("test_data", "surveys_test_data.py"),
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
