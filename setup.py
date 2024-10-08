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
    entry_points={
        "console_scripts": ["thiscovery=thiscovery_dev_tools.command_line:main"],
    },
    install_requires=[
        "prettytable",
        "pyyaml",
        "cfn-flip",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/THIS-Labs/thiscovery-dev-tools",
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
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
