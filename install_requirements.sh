# This script sets environment variables from key/value pairs
# found in a .env file and then runs pip to install requirements.
# The .env file should define GIT_PERSONAL_ACCESS_TOKEN, which is a GitHub
# personal access token with read access to private packages such
# as thiscovery-lib

set -o allexport  # https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html
source .env
set +o allexport
pip install -r requirements.txt
