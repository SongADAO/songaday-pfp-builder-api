#!/usr/bin/env bash

# set -o errexit
set -o pipefail
set -o nounset

PYENV_VIRTUALENV_DISABLE_PROMPT=1

eval "$(pyenv init -)"

pyenv install 3.9.11

pyenv virtualenv 3.9.11 pfpbuilderapi

_OLD_VIRTUAL_PATH=""
_OLD_VIRTUAL_PYTHONHOME=""
_OLD_VIRTUAL_PS1=""
pyenv activate pfpbuilderapi

python -m pip install -r requirements.txt