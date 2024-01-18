#!/bin/bash

(python -m piptools compile \
    -o requirements.txt \
    pyproject.toml \
    --no-header) || return

(python -m piptools compile \
    -o requirements_dev.txt \
    --no-header \
    --extra dev \
    --constraint requirements.txt \
    pyproject.toml) || return
