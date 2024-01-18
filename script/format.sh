#!/bin/bash

if [[ -z "${FIX}" ]]; then
    echo "Checking formatting & linting"
    ruff format --check . && ruff check .
else
    echo "Fixing formatting & linting"
    ruff format . && ruff check --fix .
fi
