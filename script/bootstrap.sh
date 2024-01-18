#!/bin/bash

python -m venv .venv

. .venv/bin/activate

pip install -U pip pip-tools
pip-sync requirements_dev.txt

cp .github/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit
