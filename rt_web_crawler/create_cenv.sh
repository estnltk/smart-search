#!/bin/bash

# create conda environment

conda update -n base -c defaults conda
conda env create -f requirements.yml --prefix ./cenv --force
conda list -p ${PWD}/cenv > packages-list-cenv.txt