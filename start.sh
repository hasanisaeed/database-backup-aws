#!/bin/bash

# create virtual environment
python3.9 -m venv .venv

# active environment
source .venv/bin/activate

# install requirements
pip install -r requirements.txt