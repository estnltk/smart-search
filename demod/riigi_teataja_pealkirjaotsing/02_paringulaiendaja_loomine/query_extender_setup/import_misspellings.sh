#!/bin/bash

SOURCE_PATH=$(dirname "$0")
python3 ${SOURCE_PATH}/import_misspellings.py "$@"
